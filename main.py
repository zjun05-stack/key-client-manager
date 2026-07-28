"""入口：系统托盘、定时提醒、启动管理."""

import sys
import threading

from PIL import Image, ImageDraw


def _create_tray_icon():
    """Generate a simple green checkmark icon for system tray."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Green circle background
    draw.ellipse([4, 4, size - 4, size - 4], fill=(22, 163, 74))
    # White checkmark
    points = [(18, 32), (28, 42), (46, 22)]
    draw.line(points, fill=(255, 255, 255), width=7, joint="curve")
    return img


def _show_reminder_window(root, info):
    """Show a topmost reminder popup window."""
    import tkinter as tk
    from tkinter import ttk

    win = tk.Toplevel(root)
    win.title("客户联系提醒")
    win.geometry("440x380")
    win.resizable(False, False)
    win.attributes("-topmost", True)
    win.grab_set()

    frame = ttk.Frame(win, padding=20)
    frame.pack(fill="both", expand=True)

    # Title
    if info["is_monday"]:
        title = f"📋 周一提醒 - 第 {info['week_num']} 周"
        msg = f"新的一周开始了！本周需关注以下 {info['total']} 位重点客户，请在周五前完成研究或联系。"
    else:
        title = f"⏰ 周五提醒 - 第 {info['week_num']} 周"
        remaining = info["total"] - info["contacted_count"]
        msg = f"本周即将结束！还有 {remaining} 位客户尚未联系："

    ttk.Label(frame, text=title, font=("微软雅黑", 13, "bold")).pack(anchor="w", pady=(0, 8))
    ttk.Label(frame, text=msg, font=("微软雅黑", 10), wraplength=400).pack(anchor="w")

    # List of clients needing attention
    if info["uncontacted"]:
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill="both", expand=True, pady=(10, 10))
        listbox = tk.Listbox(list_frame, font=("微软雅黑", 10), height=8)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        for name in info["uncontacted"]:
            listbox.insert("end", f"  • {name}")
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # Dismiss button
    ttk.Button(win, text="知道了", command=win.destroy, width=14).pack(pady=(8, 0))

    # Play system sound on Windows
    try:
        import winsound
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except ImportError:
        pass  # Not on Windows


class App:
    """Main application: ties together GUI, tray, and reminder timer."""

    def __init__(self):
        self.root = None
        self.tray_icon = None
        self.main_window = None
        self.check_interval = 5 * 60 * 1000  # 5 minutes in ms

    def run(self):
        import tkinter as tk
        from gui import MainWindow
        import pystray

        self.root = tk.Tk()

        # Build main window
        self.main_window = MainWindow(self.root, on_close_callback=self._minimize_to_tray)

        # Build tray icon
        icon_img = _create_tray_icon()
        menu = pystray.Menu(
            pystray.MenuItem("显示主窗口", self._show_window, default=True),
            pystray.MenuItem("手动检查提醒", self._manual_check),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出程序", self._quit_app),
        )
        self.tray_icon = pystray.Icon("client_manager", icon_img, "业务员重点客户管理", menu)

        # Start tray in background thread
        tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        tray_thread.start()

        # Show window or start minimized
        if "--silent" in sys.argv:
            self.root.withdraw()
        else:
            self.root.deiconify()

        # Start reminder checker
        self._start_reminder_timer()

        # Check reminder on startup (in case PC was off at 9:00)
        self.root.after(2000, self._check_reminder)

        self.root.mainloop()

    def _minimize_to_tray(self):
        """Hide window to system tray."""
        self.root.withdraw()

    def _show_window(self, *_):
        """Restore window from tray."""
        self.main_window.show()

    def _manual_check(self, *_):
        """Manually trigger a reminder check."""
        self.root.after(0, self._check_reminder)

    def _start_reminder_timer(self):
        """Schedule periodic reminder checks."""
        self._check_reminder()
        self.root.after(self.check_interval, self._start_reminder_timer)

    def _check_reminder(self):
        """Check if a reminder should be shown, and show it."""
        from reminder import should_remind, get_reminder_info, mark_reminded_today
        if should_remind():
            info = get_reminder_info()
            mark_reminded_today()
            _show_reminder_window(self.root, info)

    def _quit_app(self, *_):
        """Fully exit the application."""
        if self.tray_icon:
            self.tray_icon.stop()
        if self.root:
            self.root.destroy()


def main():
    App().run()


if __name__ == "__main__":
    main()
