"""Turn a filled Sheets plan into Google Sheets API request bodies, sent verbatim.

Files, in send order (manifest.json lists them):
  01-tabs.json          spreadsheets.batchUpdate: add or clear the MRR tabs, delete retired
                        MRR tabs. New tabs get fixed sheet ids, so later files can name them.
  02-values-NN.json     spreadsheets.values.batchUpdate (USER_ENTERED): every write.
  03-format-NN.json     spreadsheets.batchUpdate: formats, merges, dropdowns, conditional
                        colors, widths, hidden columns, charts, warning-only protection,
                        and tab order.
Each file stays under the chunk size (default 60,000 bytes) so a chat can send it in one
call. Only tabs named in the plan appear in any request: Kick and user tabs are never
named, so they can't be changed.

The existing-tab map comes from a spreadsheets.get response (existing_from_spreadsheet) or
from --sheet-ids. It maps an existing tab name to its sheet id, or to
{"sheetId": n, "chartIds": [...], "protectedRangeIds": [...], "conditionalFormatCount": n}.
"_userTabCount" (number of tabs that aren't MRR tabs) lets the tab-order step place the
MRR tabs after the user's tabs; without it that step is skipped and the manifest says so.
"""

import json
import re
import zlib
from pathlib import Path

DEFAULT_ROWS = 1000
A1_RE = re.compile(r"^(?:'((?:[^']|'')+)'!)?([A-Z]*)(\d*)(?::([A-Z]*)(\d*))?$")


def col_index(letters):
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def new_sheet_id(name):
    return zlib.crc32(name.encode("utf-8")) & 0x3FFFFFFF


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return {"rgbColor": {"red": int(h[0:2], 16) / 255, "green": int(h[2:4], 16) / 255,
                         "blue": int(h[4:6], 16) / 255}}


def grid(sheet_id, a1):
    m = A1_RE.match(a1)
    if not m:
        raise ValueError("bad A1 range: %s" % a1)
    _, c1, r1, c2, r2 = m.groups()
    out = {"sheetId": sheet_id}
    if m.group(4) is None and m.group(5) is None:
        c2, r2 = c1, r1
    if c1:
        out["startColumnIndex"] = col_index(c1)
    if c2:
        out["endColumnIndex"] = col_index(c2) + 1
    if r1:
        out["startRowIndex"] = int(r1) - 1
    if r2:
        out["endRowIndex"] = int(r2)
    return out


def split_columns(sheet_id, a1):
    g = grid(sheet_id, a1)
    return [{**g, "startColumnIndex": c, "endColumnIndex": c + 1}
            for c in range(g["startColumnIndex"], g["endColumnIndex"])]


def resolve(ids, sheet_id, a1):
    m = A1_RE.match(a1)
    if m and m.group(1):
        return ids[m.group(1).replace("''", "'")], a1.split("!", 1)[1]
    return sheet_id, a1


def number_type(pattern):
    if "%" in pattern:
        return "PERCENT"
    if re.search(r"[dmy]", pattern.replace('"', "")) and "#" not in pattern:
        return "DATE"
    return "NUMBER"


def format_request(sheet_id, f):
    fmt, fields = {}, []
    if "numberFormat" in f:
        fmt["numberFormat"] = {"type": number_type(f["numberFormat"]), "pattern": f["numberFormat"]}
        fields.append("userEnteredFormat.numberFormat")
    text = {}
    if f.get("bold"):
        text["bold"] = True
        fields.append("userEnteredFormat.textFormat.bold")
    if "fontSize" in f:
        text["fontSize"] = f["fontSize"]
        fields.append("userEnteredFormat.textFormat.fontSize")
    if "fontColor" in f:
        text["foregroundColorStyle"] = rgb(f["fontColor"])
        fields.append("userEnteredFormat.textFormat.foregroundColorStyle")
    if text:
        fmt["textFormat"] = text
    if "background" in f:
        fmt["backgroundColorStyle"] = rgb(f["background"])
        fields.append("userEnteredFormat.backgroundColorStyle")
    return {"repeatCell": {"range": grid(sheet_id, f["range"]), "cell": {"userEnteredFormat": fmt},
                           "fields": ",".join(fields)}}


def conditional_request(sheet_id, c, index):
    if "formula" in c:
        cond = {"type": "CUSTOM_FORMULA", "values": [{"userEnteredValue": c["formula"]}]}
    else:
        cond = {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": c["textContains"]}]}
    fmt = {"backgroundColorStyle": rgb(c["background"])}
    if "fontColor" in c:
        fmt["textFormat"] = {"foregroundColorStyle": rgb(c["fontColor"])}
    return {"addConditionalFormatRule": {"index": index, "rule": {
        "ranges": [grid(sheet_id, c["range"])], "booleanRule": {"condition": cond, "format": fmt}}}}


def chart_request(ids, sheet_id, c):
    columns = []
    for a1 in c["ranges"]:
        sid, local = resolve(ids, sheet_id, a1)
        columns += split_columns(sid, local)
    opts = c.get("options", {})
    anchor = grid(sheet_id, c["anchor"])
    position = {"overlayPosition": {
        "anchorCell": {"sheetId": sheet_id, "rowIndex": anchor["startRowIndex"],
                       "columnIndex": anchor["startColumnIndex"]},
        "widthPixels": opts.get("width", 600), "heightPixels": opts.get("height", 320)}}
    legend = "NO_LEGEND" if opts.get("legend", {}).get("position") == "none" else "BOTTOM_LEGEND"
    src = lambda g: {"sourceRange": {"sources": [g]}}
    if c["type"] == "PIE":
        spec = {"pieChart": {"legendPosition": "RIGHT_LEGEND", "domain": src(columns[0]),
                             "series": src(columns[1]), "pieHole": opts.get("pieHole", 0)}}
    else:
        colors = opts.get("colors", [])
        axis = "BOTTOM_AXIS" if c["type"] == "BAR" else "LEFT_AXIS"
        series = []
        for i, col in enumerate(columns[1:]):
            s = {"series": src(col), "targetAxis": axis}
            if i < len(colors):
                s["colorStyle"] = rgb(colors[i])
            series.append(s)
        spec = {"basicChart": {"chartType": c["type"], "legendPosition": legend,
                               "headerCount": c.get("headerRows", 1),
                               "domains": [{"domain": src(columns[0])}], "series": series}}
        if opts.get("isStacked"):
            spec["basicChart"]["stackedType"] = "STACKED"
    spec["title"] = opts.get("title", "")
    return {"addChart": {"chart": {"spec": spec, "position": position}}}


def sheet_properties(tab, sheet_id):
    props = {"sheetId": sheet_id, "title": tab["name"],
             "gridProperties": {"rowCount": tab.get("rowCount", DEFAULT_ROWS),
                                "columnCount": tab.get("columnCount", 26),
                                "frozenRowCount": tab.get("frozenRows", 0),
                                "frozenColumnCount": tab.get("frozenColumns", 0),
                                "hideGridlines": bool(tab.get("hideGridlines"))}}
    if tab.get("tabColor"):
        props["tabColorStyle"] = rgb(tab["tabColor"])
    return props


def existing_from_spreadsheet(doc, plan):
    """The existing-tab map from a spreadsheets.get response, for the tabs the plan owns."""
    owned = {t["name"] for t in plan["tabs"]} | set(plan.get("retiredTabs", []))
    out, user_tabs = {}, 0
    for sheet in doc.get("sheets", []):
        props = sheet.get("properties", {})
        title = props.get("title", "")
        if title not in owned:
            user_tabs += 1
            continue
        out[title] = {
            "sheetId": props["sheetId"],
            "chartIds": [c["chartId"] for c in sheet.get("charts", []) if "chartId" in c],
            "protectedRangeIds": [p["protectedRangeId"] for p in sheet.get("protectedRanges", [])
                                  if "protectedRangeId" in p],
            "conditionalFormatCount": len(sheet.get("conditionalFormats", [])),
        }
    out["_userTabCount"] = user_tabs
    return out


def existing_entry(existing, name):
    value = existing.get(name)
    if value is None:
        return None
    return value if isinstance(value, dict) else {"sheetId": value}


def chunk(items, limit, wrap):
    files, current = [], []
    for item in items:
        trial = current + [item]
        if current and len(json.dumps(wrap(trial))) > limit:
            files.append(wrap(current))
            current = [item]
        else:
            current = trial
    if current:
        files.append(wrap(current))
    return files


def emit_payloads(plan, out_dir, existing, chunk_bytes):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ids, tab_requests, skipped, notes = {}, [], [], []
    for name in plan.get("retiredTabs", []):
        entry = existing_entry(existing, name)
        if entry:
            tab_requests.append({"deleteSheet": {"sheetId": entry["sheetId"]}})
    active = []
    for tab in plan["tabs"]:
        entry = existing_entry(existing, tab["name"])
        if entry and tab.get("createOnly"):
            ids[tab["name"]] = entry["sheetId"]
            skipped.append(tab["name"])
            continue
        if entry:
            sid = entry["sheetId"]
            ids[tab["name"]] = sid
            tab_requests += [{"deleteEmbeddedObject": {"objectId": cid}} for cid in entry.get("chartIds", [])]
            tab_requests += [{"deleteProtectedRange": {"protectedRangeId": pid}}
                             for pid in entry.get("protectedRangeIds", [])]
            tab_requests += [{"deleteConditionalFormatRule": {"sheetId": sid, "index": 0}}
                             for _ in range(entry.get("conditionalFormatCount", 0))]
            tab_requests += [{"unmergeCells": {"range": {"sheetId": sid}}},
                             {"updateCells": {"range": {"sheetId": sid}, "fields": "*"}},
                             {"updateSheetProperties": {"properties": sheet_properties(tab, sid),
                                                        "fields": "title,gridProperties,tabColorStyle"}}]
        else:
            sid = new_sheet_id(tab["name"])
            ids[tab["name"]] = sid
            tab_requests.append({"addSheet": {"properties": sheet_properties(tab, sid)}})
        active.append(tab)
    for name in skipped:
        ids.setdefault(name, existing_entry(existing, name)["sheetId"])

    value_data = []
    for tab in active:
        for wr in tab.get("writes", []):
            value_data.append({"range": "'%s'!%s" % (tab["name"].replace("'", "''"), wr["range"]),
                               "values": [["" if v is None else v for v in row] for row in wr["values"]]})

    fmt = []
    for tab in active:
        sid = ids[tab["name"]]
        fmt += [{"mergeCells": {"range": grid(sid, a1), "mergeType": "MERGE_ALL"}} for a1 in tab.get("merges", [])]
        fmt += [format_request(sid, f) for f in tab.get("formats", [])]
        for v in tab.get("validations", []):
            fmt.append({"setDataValidation": {"range": grid(sid, v["range"]), "rule": {
                "condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": x} for x in v["list"]]},
                "showCustomUi": True, "strict": False}}})
        fmt += [conditional_request(sid, c, i) for i, c in enumerate(tab.get("conditionalFormats", []))]
        for cw in tab.get("columnWidths", []):
            g = grid(sid, cw["columns"])
            fmt.append({"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS",
                        "startIndex": g["startColumnIndex"], "endIndex": g["endColumnIndex"]},
                        "properties": {"pixelSize": cw["width"]}, "fields": "pixelSize"}})
        for rh in tab.get("rowHeights", []):
            g = grid(sid, rh["rows"])
            fmt.append({"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "ROWS",
                        "startIndex": g["startRowIndex"], "endIndex": g["endRowIndex"]},
                        "properties": {"pixelSize": rh["height"]}, "fields": "pixelSize"}})
        if tab.get("hiddenColumns"):
            g = grid(sid, tab["hiddenColumns"])
            fmt.append({"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS",
                        "startIndex": g["startColumnIndex"], "endIndex": g["endColumnIndex"]},
                        "properties": {"hiddenByUser": True}, "fields": "hiddenByUser"}})
        fmt += [chart_request(ids, sid, c) for c in tab.get("charts", [])]
        if tab.get("protect") == "warning":
            fmt.append({"addProtectedRange": {"protectedRange": {
                "range": {"sheetId": sid}, "description": "%s: formulas, rebuilt by the MRR skill" % tab["name"],
                "warningOnly": True}}})
    if "_userTabCount" in existing:
        base = int(existing["_userTabCount"])
        fmt += [{"updateSheetProperties": {"properties": {"sheetId": ids[n], "index": base + i}, "fields": "index"}}
                for i, n in enumerate(plan.get("displayOrder", [])) if n in ids]
    else:
        notes.append("Tab order skipped: pass _userTabCount in --sheet-ids to place the MRR tabs after the user's tabs.")

    files = []

    def save(name, body):
        path = out_dir / name
        path.write_text(json.dumps(body, ensure_ascii=False))
        files.append({"file": name, "bytes": path.stat().st_size,
                      "api": "spreadsheets.values.batchUpdate" if name.startswith("02") else "spreadsheets.batchUpdate"})

    save("01-tabs.json", {"requests": tab_requests})
    for i, body in enumerate(chunk(value_data, chunk_bytes, lambda d: {"valueInputOption": "USER_ENTERED", "data": d}), 1):
        save("02-values-%02d.json" % i, body)
    for i, body in enumerate(chunk(fmt, chunk_bytes, lambda r: {"requests": r}), 1):
        save("03-format-%02d.json" % i, body)
    oversized = [f["file"] for f in files if f["bytes"] > chunk_bytes]
    if oversized:
        notes.append("Single writes larger than the chunk size: %s. Send them alone." % ", ".join(oversized))
    manifest = {"send_in_order": files, "sheet_ids": ids, "skipped_create_only": skipped,
                "created_tabs": [t["name"] for t in active if not existing_entry(existing, t["name"])],
                "notes": notes}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    return {"dir": str(out_dir), "files": len(files), "created_tabs": manifest["created_tabs"], "notes": notes}
