#!/usr/bin/env python3
"""
Recalculate a workbook and prove the formulas work. Run before delivering any model.

    python3 verify_model.py model.xlsx
    python3 verify_model.py cash-forecast.xlsx \
                                       --report "Cash Flow!A10" "Cash Flow!B14"

openpyxl writes formula strings without evaluating them, so a workbook can save
perfectly and still open full of #REF! or a circular-reference warning. This catches
three separate failures:

  1. error values:           #REF!, #DIV/0!, #VALUE!, #NAME?, #N/A, #NUM!
  2. unevaluated formulas:   cells holding a formula that the engine refused to
                              resolve, which in practice means a circular reference or
                              an unsupported function. This is the dangerous one: the
                              workbook looks fine and the numbers are simply absent.
  3. dead scenarios:         a switch that does not move the reported cells

Anything in category 2 is a real defect in the model, not a quirk of the checker.
A circular reference means a formula chain feeds back into itself, and Excel will
show 0 for the whole chain.

Requires: pip install formulas openpyxl
"""
import argparse
import sys

ERRORS = ("#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A", "#NULL!", "#NUM!")


def scalar(v):
    v = getattr(v, "value", v)
    while hasattr(v, "__len__") and not isinstance(v, str) and len(v):
        v = v[0]
    return v


def formula_cells(path):
    """Every cell in the file that holds a formula, as {(SHEET, ADDR): formula}."""
    import openpyxl
    wb = openpyxl.load_workbook(path)
    out = {}
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("="):
                    out[(ws.title.upper(), c.coordinate)] = c.value
    return out


def evaluate(path, overrides=None):
    """{(SHEET, ADDR): value} for everything the engine resolved."""
    import formulas
    xl = formulas.ExcelModel().loads(path).finish()
    sol = xl.calculate(inputs=overrides or {})
    idx = {}
    for key, v in sol.items():
        if "]" not in key or "!" not in key:
            continue
        sheet = key.split("]", 1)[1].split("'")[0].upper()
        idx[(sheet, key.rsplit("!", 1)[1].replace("$", ""))] = scalar(v)
    return idx


def switch_key(path, ref):
    sheet, addr = ref.rsplit("!", 1)
    return f"'[{path.split('/')[-1]}]{sheet.strip(chr(39)).upper()}'!{addr.upper()}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--switch", nargs="+", metavar=("CELL", "VALUE"),
                    help='switch cell then the values to test, '
                         'e.g. --switch "Cash Flow!C5" Base Downside Upside')
    ap.add_argument("--report", nargs="*", default=[], metavar="CELL",
                    help='cells to print per run, e.g. "Cash Flow!A10"')
    args = ap.parse_args()
    switch_cell, switch_values = (args.switch[0], args.switch[1:]) if args.switch else (None, [])

    formulas_in_file = formula_cells(args.path)
    print(f"{args.path}: {len(formulas_in_file)} formula cells")

    runs = [(None, "as saved")]
    if switch_cell and switch_values:
        runs = [(v, v) for v in switch_values]

    failed = False
    reported = {}
    for value, label in runs:
        overrides = {switch_key(args.path, switch_cell): value} if value else None
        try:
            idx = evaluate(args.path, overrides)
        except Exception as exc:
            print(f"  [{label}] could not recalculate: {type(exc).__name__}: {exc}")
            print("           Say plainly that formulas calculate on open. Do not imply "
                  "you verified them.")
            return 1

        bad = {k: v for k, v in idx.items()
               if isinstance(v, str) and v.strip().upper() in ERRORS}
        missing = [k for k in formulas_in_file if k not in idx]

        state = "OK" if not bad and not missing else "FAILED"
        print(f"  [{label}] {len(idx)} cells resolved | {len(bad)} errors | "
              f"{len(missing)} unevaluated -> {state}")
        for k, v in list(bad.items())[:10]:
            print(f"           {v:9} {k[0]}!{k[1]}")
        if missing:
            failed = True
            print("           unevaluated formulas (circular reference or unsupported "
                  "function):")
            for k in missing[:10]:
                print(f"           {k[0]}!{k[1]}  {formulas_in_file[k][:64]}")
            if len(missing) > 10:
                print(f"           ... and {len(missing) - 10} more")
        if bad:
            failed = True

        for ref in args.report:
            sheet, addr = ref.rsplit("!", 1)
            v = idx.get((sheet.strip("'").upper(), addr.replace("$", "")))
            v = round(v, 2) if isinstance(v, float) else v
            print(f"           {ref} = {v}")
            reported.setdefault(ref, []).append(v)

    if len(runs) > 1 and args.report:
        dead = [r for r, vals in reported.items() if len(set(map(str, vals))) == 1]
        if dead:
            failed = True
            print("\n  Scenario switch does not move these cells, so it is not wired "
                  "through:")
            for r in dead:
                print(f"           {r}")
        else:
            print("\n  Scenario switch moves every reported cell.")

    print("\n" + ("FAILED. Do not deliver this workbook." if failed
                  else "PASSED. Every formula resolves."))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
