/**
 * MRR and ARR report: one-time installer for Google Sheets.
 *
 * Fallback for chats that can't write to Google Sheets, generated from the same
 * plan the chat would send. Paste into Extensions > Apps Script in the spreadsheet
 * that holds the source tabs, then run installMrrReport once. It writes only tabs
 * named "MRR ..." and never edits, formats, renames, moves, or protects any other
 * tab. Re-running rebuilds the MRR tabs and keeps your edits on "MRR settings".
 */

const PLAN = __MRR_SHEET_PLAN__;

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("MRR report")
    .addItem("Rebuild MRR tabs", "installMrrReport")
    .addItem("Remove MRR tabs", "removeMrrTabs")
    .addToUi();
}

function installMrrReport() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const created = [];
  try {
    (PLAN.retiredTabs || []).forEach((name) => {
      const old = ss.getSheetByName(name);
      if (old) ss.deleteSheet(old);
    });
    const sheets = PLAN.tabs.map((tab) => prepareSheet(ss, tab, created)).filter(Boolean);
    sheets.forEach(({ sheet, tab }) => applyTab(ss, sheet, tab));
    orderTabs(ss);
  } catch (error) {
    const names = created.map((sheet) => sheet.getName()).join(", ");
    throw new Error(
      "MRR install stopped: " + error.message + ". Tabs created by this run: " + (names || "none") +
        ". Run removeMrrTabs to delete them, or fix the cause and run installMrrReport again.",
    );
  }
  SpreadsheetApp.flush();
  ss.setActiveSheet(ss.getSheetByName(PLAN.displayOrder[0]));
  ss.toast("MRR tabs are ready. They update when their source tabs change.", "MRR report", 10);
}

function removeMrrTabs() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const names = PLAN.tabs.map((tab) => tab.name).concat(PLAN.retiredTabs || []);
  names.forEach((name) => {
    const sheet = ss.getSheetByName(name);
    if (sheet && ss.getSheets().length > 1) ss.deleteSheet(sheet);
  });
}

function prepareSheet(ss, tab, created) {
  const existing = ss.getSheetByName(tab.name);
  if (existing && tab.createOnly) return null;
  let sheet = existing;
  if (!sheet) {
    sheet = ss.insertSheet(tab.name, ss.getSheets().length);
    created.push(sheet);
  } else {
    sheet.getCharts().forEach((chart) => sheet.removeChart(chart));
    sheet.getProtections(SpreadsheetApp.ProtectionType.SHEET).forEach((p) => p.remove());
    sheet.getRange(1, 1, sheet.getMaxRows(), sheet.getMaxColumns()).breakApart();
    sheet.clear();
    sheet.clearConditionalFormatRules();
    sheet.getRange(1, 1, sheet.getMaxRows(), sheet.getMaxColumns()).clearDataValidations();
    sheet.showColumns(1, sheet.getMaxColumns());
  }
  const needed = tab.columnCount || 26;
  if (sheet.getMaxColumns() < needed) sheet.insertColumnsAfter(sheet.getMaxColumns(), needed - sheet.getMaxColumns());
  return { sheet, tab };
}

function applyTab(ss, sheet, tab) {
  if (tab.tabColor) sheet.setTabColor(tab.tabColor);
  (tab.merges || []).forEach((a1) => sheet.getRange(a1).merge());
  (tab.writes || []).forEach((w) => {
    const values = w.values.map((row) => row.map((v) => (v === null ? "" : v)));
    const range = sheet.getRange(w.range).offset(0, 0, values.length, values[0].length);
    const isFormula = values.some((row) => row.some((v) => typeof v === "string" && v.startsWith("=")));
    if (isFormula && values.length === 1 && values[0].length === 1) range.setFormula(values[0][0]);
    else range.setValues(values);
  });
  (tab.formats || []).forEach((f) => {
    const range = sheet.getRange(f.range);
    if (f.numberFormat) range.setNumberFormat(f.numberFormat);
    if (f.bold) range.setFontWeight("bold");
    if (f.background) range.setBackground(f.background);
    if (f.fontSize) range.setFontSize(f.fontSize);
    if (f.fontColor) range.setFontColor(f.fontColor);
  });
  (tab.validations || []).forEach((v) =>
    sheet.getRange(v.range).setDataValidation(
      SpreadsheetApp.newDataValidation().requireValueInList(v.list, true).setAllowInvalid(true).build(),
    ),
  );
  if (tab.conditionalFormats) {
    sheet.setConditionalFormatRules(
      tab.conditionalFormats.map((c) => {
        let rule = SpreadsheetApp.newConditionalFormatRule();
        rule = c.formula ? rule.whenFormulaSatisfied(c.formula) : rule.whenTextContains(c.textContains);
        rule = rule.setBackground(c.background);
        if (c.fontColor) rule = rule.setFontColor(c.fontColor);
        return rule.setRanges([sheet.getRange(c.range)]).build();
      }),
    );
  }
  (tab.columnWidths || []).forEach((c) => {
    const range = sheet.getRange(c.columns);
    sheet.setColumnWidths(range.getColumn(), range.getNumColumns(), c.width);
  });
  (tab.rowHeights || []).forEach((r) => {
    const range = sheet.getRange(r.rows);
    sheet.setRowHeights(range.getRow(), range.getNumRows(), r.height);
  });
  if (tab.frozenRows) sheet.setFrozenRows(tab.frozenRows);
  if (tab.frozenColumns) sheet.setFrozenColumns(tab.frozenColumns);
  if (tab.hideGridlines) sheet.setHiddenGridlines(true);
  (tab.charts || []).forEach((c) => sheet.insertChart(buildChart(ss, sheet, c)));
  if (tab.hiddenColumns) {
    const range = sheet.getRange(tab.hiddenColumns);
    sheet.hideColumns(range.getColumn(), range.getNumColumns());
  }
  if (tab.protect === "warning") {
    sheet.protect().setDescription(tab.name + ": formulas, rebuilt by the MRR skill").setWarningOnly(true);
  }
}

function orderTabs(ss) {
  (PLAN.displayOrder || []).forEach((name) => {
    const sheet = ss.getSheetByName(name);
    if (!sheet) return;
    ss.setActiveSheet(sheet);
    ss.moveActiveSheet(ss.getSheets().length);
  });
}

function resolveRange(ss, sheet, a1) {
  const match = a1.match(/^'(.+)'!(.+)$/);
  return match ? ss.getSheetByName(match[1].replace(/''/g, "'")).getRange(match[2]) : sheet.getRange(a1);
}

function buildChart(ss, sheet, c) {
  const anchor = sheet.getRange(c.anchor);
  let builder = sheet
    .newChart()
    .setChartType(Charts.ChartType[c.type])
    .setNumHeaders(c.headerRows || 1)
    .setPosition(anchor.getRow(), anchor.getColumn(), 0, 0);
  c.ranges.forEach((a1) => {
    builder = builder.addRange(resolveRange(ss, sheet, a1));
  });
  Object.entries(c.options || {}).forEach(([key, value]) => {
    builder = builder.setOption(key, value);
  });
  return builder.build();
}
