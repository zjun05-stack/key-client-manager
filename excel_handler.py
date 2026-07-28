"""Excel 读写层：客户名单 + 联系记录管理."""

import os
from datetime import date, timedelta
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

EXCEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "重点客户名单.xlsx")

BODY_FONT = Font(name="微软雅黑", size=11)
BODY_ALIGN = Alignment(horizontal="center", vertical="center")
NAME_ALIGN = Alignment(horizontal="left", vertical="center")
THIN_BORDER = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"), bottom=Side(style="thin"),
)


def _get_week_range(today=None):
    """Return (monday, sunday) for the current week."""
    if today is None:
        today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def load_customers():
    """Read customer list from Sheet 1. Returns list of {index, name}."""
    wb = load_workbook(EXCEL_FILE, data_only=True)
    ws = wb["客户名单"]
    customers = []
    for row in ws.iter_rows(min_row=2, max_row=21, min_col=1, max_col=2, values_only=True):
        idx, name = row
        if name and str(name).strip():
            customers.append({"index": idx, "name": str(name).strip()})
    wb.close()
    return customers


def get_contact_records():
    """Read all contact records from Sheet 2. Returns list of dicts."""
    wb = load_workbook(EXCEL_FILE, data_only=True)
    ws = wb["联系记录"]
    records = []
    for row in ws.iter_rows(min_row=2, min_col=1, max_col=5, values_only=True):
        idx, name, method, record_date, notes = row
        if name and str(name).strip():
            records.append({
                "index": idx,
                "name": str(name).strip(),
                "method": str(method).strip() if method else "",
                "date": _parse_date(record_date),
                "notes": str(notes).strip() if notes else "",
            })
    wb.close()
    return records


def _parse_date(value):
    """Parse a date value from openpyxl (could be datetime, date, or string)."""
    if value is None:
        return None
    from datetime import datetime
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    # Try to parse string
    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"]:
        try:
            return datetime.strptime(str(value).strip(), fmt).date()
        except ValueError:
            continue
    return None


def get_this_week_contacted():
    """Return set of customer names contacted this week (Mon-Sun)."""
    monday, sunday = _get_week_range()
    records = get_contact_records()
    contacted = set()
    for r in records:
        if r["date"] and monday <= r["date"] <= sunday:
            contacted.add(r["name"])
    return contacted


def get_last_contact_date(name):
    """Return the most recent contact date for a customer, or None."""
    records = get_contact_records()
    latest = None
    for r in records:
        if r["name"] == name and r["date"]:
            if latest is None or r["date"] > latest:
                latest = r["date"]
    return latest


def add_contact_record(name, method, record_date, notes=""):
    """Append a contact record to Sheet 2."""
    wb = load_workbook(EXCEL_FILE)
    ws = wb["联系记录"]
    next_row = ws.max_row + 1
    if next_row < 2:
        next_row = 2

    ws[f"A{next_row}"] = next_row - 1
    ws[f"B{next_row}"] = name
    ws[f"C{next_row}"] = method
    ws[f"D{next_row}"] = record_date
    ws[f"D{next_row}"].number_format = "YYYY-MM-DD"
    ws[f"E{next_row}"] = notes

    # Apply styles
    for col in ["A", "B", "C", "D", "E"]:
        cell = ws[f"{col}{next_row}"]
        cell.font = BODY_FONT
        cell.border = THIN_BORDER
        if col == "B":
            cell.alignment = NAME_ALIGN
        else:
            cell.alignment = BODY_ALIGN

    wb.save(EXCEL_FILE)
    wb.close()


def get_week_info():
    """Return (week_number, monday, friday) for display."""
    today = date.today()
    week_num = today.isocalendar()[1]
    monday, _ = _get_week_range(today)
    friday = monday + timedelta(days=4)
    return week_num, monday, friday
