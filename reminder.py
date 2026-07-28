"""提醒逻辑：判断提醒时机 + 获取未联系客户."""

import os
import sys
from datetime import date, datetime, time as dtime
from excel_handler import get_this_week_contacted, load_customers, get_week_info

# Detect app directory (works both as .py and as PyInstaller .exe)
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

REMINDER_WINDOW_START = dtime(9, 0)
REMINDER_WINDOW_END = dtime(9, 15)


def _today_reminder_flag_file():
    """Return a marker filename for today's reminder state."""
    tmpdir = os.path.join(APP_DIR, ".reminder_state")
    os.makedirs(tmpdir, exist_ok=True)
    return os.path.join(tmpdir, f"reminded_{date.today().isoformat()}.txt")


def has_reminded_today():
    """Check if a reminder has already been shown today."""
    flag = _today_reminder_flag_file()
    return os.path.exists(flag)


def mark_reminded_today():
    """Record that a reminder was shown today."""
    flag = _today_reminder_flag_file()
    with open(flag, "w") as f:
        f.write("1")


def should_remind():
    """Return True if now is Mon/Fri 9:00-9:15 and not reminded yet today."""
    if has_reminded_today():
        return False
    now = datetime.now()
    if now.weekday() not in (0, 4):  # 0=Mon, 4=Fri
        return False
    current_time = now.time()
    return REMINDER_WINDOW_START <= current_time <= REMINDER_WINDOW_END


def get_reminder_info():
    """Return (is_monday, uncontacted_names, week_num, friday_date) for reminder display.
    Returns None if no reminder is needed (should call should_remind first).
    """
    today = date.today()
    is_monday = today.weekday() == 0
    customers = load_customers()
    contacted = get_this_week_contacted()
    week_num, monday, friday = get_week_info()

    uncontacted = [c["name"] for c in customers if c["name"] not in contacted]

    return {
        "is_monday": is_monday,
        "uncontacted": uncontacted,
        "total": len(customers),
        "contacted_count": len(contacted),
        "week_num": week_num,
        "friday_date": friday.strftime("%Y-%m-%d"),
    }
