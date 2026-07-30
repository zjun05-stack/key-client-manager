"""主窗口 UI：客户列表、标记联系、联系记录查看."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from excel_handler import (
    load_customers,
    get_this_week_contacted,
    get_last_contact_date,
    add_contact_record,
    get_contact_records,
    get_week_info,
)


class MarkContactDialog(tk.Toplevel):
    """弹窗：标记客户已联系."""

    def __init__(self, parent, customer_name):
        super().__init__(parent)
        self.customer_name = customer_name
        self.result = None

        self.title(f"标记联系 - {customer_name}")
        self.geometry("380x240")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _build_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        # Customer name
        ttk.Label(frame, text=f"客户：{self.customer_name}", font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", pady=(0, 12))

        # Contact method
        ttk.Label(frame, text="联系方式：", font=("Microsoft YaHei", 10)).pack(anchor="w")
        self.method_var = tk.StringVar(value="电话")
        methods = ["电话", "拜访", "微信", "邮件", "其他"]
        combo = ttk.Combobox(frame, textvariable=self.method_var, values=methods, state="readonly", width=20)
        combo.pack(anchor="w", pady=(2, 10))

        # Notes
        ttk.Label(frame, text="备注：", font=("Microsoft YaHei", 10)).pack(anchor="w")
        self.notes_text = tk.Text(frame, height=3, width=40, font=("Microsoft YaHei", 10))
        self.notes_text.pack(anchor="w", pady=(2, 12))

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(anchor="e")
        ttk.Button(btn_frame, text="确认", command=self._on_confirm, width=10).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="取消", command=self._on_cancel, width=10).pack(side="left")

    def _on_confirm(self):
        self.result = {
            "method": self.method_var.get(),
            "notes": self.notes_text.get("1.0", "end-1c").strip(),
        }
        self.destroy()

    def _on_cancel(self):
        self.destroy()


class ContactHistoryWindow(tk.Toplevel):
    """弹窗：查看联系历史记录."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("联系记录")
        self.geometry("750x450")
        self.transient(parent)
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="both", expand=True)

        columns = ("序号", "客户名称", "联系方式", "联系日期", "备注")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=18)
        self.tree.column("序号", width=50, anchor="center")
        self.tree.column("客户名称", width=180, anchor="w")
        self.tree.column("联系方式", width=100, anchor="center")
        self.tree.column("联系日期", width=110, anchor="center")
        self.tree.column("备注", width=280, anchor="w")
        for col in columns:
            self.tree.heading(col, text=col)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        records = get_contact_records()
        for i, r in enumerate(records, 1):
            date_str = r["date"].strftime("%Y-%m-%d") if r["date"] else ""
            self.tree.insert("", "end", values=(r["index"] or i, r["name"], r["method"], date_str, r["notes"]))


class MainWindow:
    """主窗口."""

    def __init__(self, root, on_close_callback=None):
        self.root = root
        self.on_close_callback = on_close_callback  # Called when window is closed (minimize to tray)

        root.title("业务员重点客户管理")
        root.geometry("700x620")
        root.minsize(640, 500)

        self._build_ui()
        self._refresh()

        # Override close button → minimize to tray
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # ── Top: week info & progress ──
        top_frame = ttk.Frame(self.root, padding=(12, 10, 12, 6))
        top_frame.pack(fill="x")

        week_num, monday, friday = get_week_info()
        self.week_label = ttk.Label(top_frame, text="", font=("Microsoft YaHei", 11, "bold"))
        self.week_label.pack(side="left")

        self.progress_label = ttk.Label(top_frame, text="", font=("Microsoft YaHei", 11))
        self.progress_label.pack(side="right")

        self.progress = ttk.Progressbar(top_frame, length=200, mode="determinate", maximum=20)
        self.progress.pack(side="right", padx=(0, 10))
        self.progress_label.pack(side="right", padx=(0, 5))

        # ── Separator ──
        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=10)

        # ── Middle: customer table ──
        mid_frame = ttk.Frame(self.root, padding=(12, 6))
        mid_frame.pack(fill="both", expand=True)

        columns = ("序号", "客户名称", "本周状态", "最近联系")
        self.tree = ttk.Treeview(mid_frame, columns=columns, show="headings", height=22, selectmode="browse")
        self.tree.column("序号", width=60, anchor="center")
        self.tree.column("客户名称", width=280, anchor="w")
        self.tree.column("本周状态", width=100, anchor="center")
        self.tree.column("最近联系", width=120, anchor="center")
        for col in columns:
            self.tree.heading(col, text=col)

        tree_scroll = ttk.Scrollbar(mid_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        # Bind double-click to mark
        self.tree.bind("<Double-1>", lambda e: self._mark_contacted())
        # Bind right-click context menu
        self.tree.bind("<Button-3>", self._on_right_click)

        # ── Bottom: action buttons ──
        bottom_frame = ttk.Frame(self.root, padding=(12, 6, 12, 12))
        bottom_frame.pack(fill="x")

        ttk.Button(bottom_frame, text="标记已联系", command=self._mark_contacted, width=14).pack(side="left", padx=(0, 8))
        ttk.Button(bottom_frame, text="查看联系记录", command=self._show_history, width=14).pack(side="left")
        ttk.Button(bottom_frame, text="刷新", command=self._refresh, width=10).pack(side="right")

        # Status tags for treeview
        self.tree.tag_configure("contacted", foreground="#16a34a")
        self.tree.tag_configure("uncontacted", foreground="#dc2626")

    # ── Public methods ──

    def _refresh(self, *_):
        """Reload all data from Excel and update display."""
        customers = load_customers()
        contacted = get_this_week_contacted()
        week_num, monday, friday = get_week_info()

        # Update top bar
        self.week_label.config(text=f"第 {week_num} 周（{monday.strftime('%m/%d')} - {friday.strftime('%m/%d')}）")
        count = len(contacted)
        total = len(customers)
        self.progress["value"] = count
        self.progress_label.config(text=f"本周已完成: {count}/{total}")

        # Update tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        for c in customers:
            name = c["name"]
            is_contacted = name in contacted
            last_date = get_last_contact_date(name)
            date_str = last_date.strftime("%m-%d") if last_date else "-"
            status = "✓ 已联系" if is_contacted else "✗ 未联系"
            tag = "contacted" if is_contacted else "uncontacted"

            self.tree.insert("", "end", values=(c["index"], name, status, date_str), tags=(tag,))

    def _mark_contacted(self):
        """Open dialog to mark selected customer as contacted."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先在表格中选择一个客户")
            return
        values = self.tree.item(selection[0], "values")
        name = values[1]

        dialog = MarkContactDialog(self.root, name)
        self.root.wait_window(dialog)

        if dialog.result:
            add_contact_record(name, dialog.result["method"], date.today(), dialog.result["notes"])
            self._refresh()
            # If all 20 contacted on Friday, show congrats
            contacted = get_this_week_contacted()
            if len(contacted) >= 20:
                messagebox.showinfo("恭喜", "本周所有重点客户已全部联系完毕！")

    def _on_right_click(self, event):
        """Right-click context menu on a row."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="标记已联系", command=self._mark_contacted)
            menu.post(event.x_root, event.y_root)

    def _show_history(self):
        """Open contact history window."""
        ContactHistoryWindow(self.root)

    def _on_close(self):
        """Close button → minimize to system tray instead of exiting."""
        if self.on_close_callback:
            self.on_close_callback()
        else:
            self.root.withdraw()

    def show(self):
        """Restore and bring window to front."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self._refresh()
