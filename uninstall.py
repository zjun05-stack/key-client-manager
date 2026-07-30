"""卸载程序：清除开机自启、桌面快捷方式，可选删除程序文件."""

import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk, messagebox


def uninstall():
    root = tk.Tk()
    root.title("业务员重点客户管理 - 卸载")
    root.geometry("440x320")
    root.resizable(False, False)
    # Safe window centering
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"+{x}+{y}")

    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="业务员重点客户管理", font=("Microsoft YaHei", 13, "bold")).pack(pady=(0, 4))
    ttk.Label(frame, text="卸载程序将执行以下操作：", font=("Microsoft YaHei", 10)).pack(anchor="w", pady=(8, 4))

    info_frame = ttk.Frame(frame)
    info_frame.pack(anchor="w", padx=(12, 0))

    ttk.Label(info_frame, text="1. 移除开机自启设置", font=("Microsoft YaHei", 10)).pack(anchor="w")
    ttk.Label(info_frame, text="2. 删除桌面快捷方式", font=("Microsoft YaHei", 10)).pack(anchor="w")
    ttk.Label(info_frame, text="3. 停止正在运行的程序（如有）", font=("Microsoft YaHei", 10)).pack(anchor="w")

    delete_var = tk.BooleanVar(value=False)
    delete_check = ttk.Checkbutton(info_frame, text="同时删除程序文件夹及所有数据（含联系记录）",
                                   variable=delete_var)
    delete_check.pack(anchor="w", pady=(8, 0))

    result_text = tk.Text(frame, height=6, font=("Microsoft YaHei", 9), relief="flat", bg="#f5f5f5")
    result_text.pack(fill="both", expand=True, pady=(8, 0))

    def do_uninstall():
        startup_dir = os.path.join(os.environ["APPDATA"],
                                   r"Microsoft\Windows\Start Menu\Programs\Startup")
        startup_vbs = os.path.join(startup_dir, "业务员重点客户管理.vbs")
        desktop_lnk = os.path.join(os.environ["USERPROFILE"], "Desktop", "业务员重点客户管理.lnk")
        results = []

        # 1. Remove startup shortcut
        try:
            if os.path.exists(startup_vbs):
                os.remove(startup_vbs)
                results.append("[OK] 已移除开机自启")
            else:
                results.append("[OK] 开机自启不存在，跳过")
        except Exception as e:
            results.append(f"[失败] 移除开机自启: {e}")

        # 2. Remove desktop shortcut
        try:
            if os.path.exists(desktop_lnk):
                os.remove(desktop_lnk)
                results.append("[OK] 已删除桌面快捷方式")
            else:
                results.append("[OK] 桌面快捷方式不存在，跳过")
        except Exception as e:
            results.append(f"[失败] 删除桌面快捷方式: {e}")

        # 3. Kill running processes
        try:
            os.system("taskkill /f /im 客户管理.exe >nul 2>&1")
            os.system("taskkill /f /im pythonw.exe /fi \"WINDOWTITLE eq *业务员*\" >nul 2>&1")
            results.append("[OK] 已停止运行中的程序")
        except Exception:
            results.append("[OK] 无需停止进程")

        # 4. Optionally delete program folder
        if delete_var.get():
            if getattr(sys, "frozen", False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(os.path.abspath(__file__))
            result_text.delete("1.0", "end")
            result_text.insert("end", "\n".join(results) + "\n\n正在删除程序文件夹...")
            root.update()
            try:
                # Only delete if we're in a folder named appropriately
                folder_name = os.path.basename(app_dir)
                shutil.rmtree(app_dir, ignore_errors=True)
                results.append("[OK] 已删除程序文件夹")
            except Exception as e:
                results.append(f"[失败] 删除程序文件夹: {e}\n请手动删除: {app_dir}")

        result_text.delete("1.0", "end")
        result_text.insert("end", "\n".join(results))
        result_text.insert("end", "\n\n卸载完成！可关闭此窗口。")
        uninstall_btn.config(state="disabled")
        delete_check.config(state="disabled")

    # Buttons
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(pady=(12, 0))
    uninstall_btn = ttk.Button(btn_frame, text="开始卸载", command=do_uninstall, width=14)
    uninstall_btn.pack(side="left", padx=(0, 8))
    ttk.Button(btn_frame, text="取消", command=root.destroy, width=10).pack(side="left")

    root.mainloop()


if __name__ == "__main__":
    uninstall()
