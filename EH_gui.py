#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EH_gui.py — e-hentai-paw 图形界面（tkinter）
======================================================
给 EH_scraper_v2.py 套的壳。跟 felinepaw_gui.py / pixivpaw_gui.py 同一个套路：

    表单收集参数 → 拼成命令行 → subprocess 起子进程跑 EH_scraper_v2.py
                  → 流式读它的输出，刷到下面的日志框。

单站点，所以字段比多站点的 felinepaw 更少、更聚焦。

运行：python EH_gui.py
自检（无窗口、不联网、不起子进程）：python EH_gui.py --selftest
"""

import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRAPER = HERE / "EH_scraper_v2.py"

# 三个互斥的入口：标签搜索 / 单画廊 URL / 从名单挑（--from-manifest）
MODES = ["标签搜索", "单画廊(URL)", "从名单挑"]


class EHGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("e-hentai-paw 下载器")
        root.geometry("720x600")
        self.queue = queue.Queue()
        self.proc = None
        self._build_ui()
        # 每 100ms 轮询一次：把队列里的日志刷进文本框，并检查子进程是否结束
        root.after(100, self._poll)

    # ------------------------------------------------------------
    # 界面搭建
    # ------------------------------------------------------------
    def _build_ui(self):
        bar = ttk.LabelFrame(self.root, text=" 任务参数 ")
        bar.pack(fill="x", padx=10, pady=8)

        # row 0：模式
        ttk.Label(bar, text="模式:").grid(row=0, column=0, padx=(8, 2), pady=6, sticky="e")
        self.mode_var = tk.StringVar(value=MODES[0])
        mode_cb = ttk.Combobox(bar, textvariable=self.mode_var, values=MODES,
                               state="readonly", width=14)
        mode_cb.grid(row=0, column=1, padx=2, pady=6, sticky="w")
        mode_cb.bind("<<ComboboxSelected>>", lambda e: self._on_mode())

        # row 1：标签（搜索模式用）
        ttk.Label(bar, text="标签(--tags):").grid(row=1, column=0, padx=(8, 2), pady=6, sticky="e")
        self.tags_var = tk.StringVar()
        self.tags_entry = ttk.Entry(bar, textvariable=self.tags_var, width=50)
        self.tags_entry.grid(row=1, column=1, columnspan=3, sticky="we", pady=6)

        # row 2：画廊 URL（单画廊模式用）
        ttk.Label(bar, text="画廊URL:").grid(row=2, column=0, padx=(8, 2), pady=6, sticky="e")
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(bar, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=2, column=1, columnspan=3, sticky="we", pady=6)

        # row 3：名单文件（从名单挑模式用）
        ttk.Label(bar, text="名单文件(--from-manifest):").grid(
            row=3, column=0, padx=(8, 2), pady=6, sticky="e")
        self.from_manifest_var = tk.StringVar()
        self.mf_entry = ttk.Entry(bar, textvariable=self.from_manifest_var, width=42)
        self.mf_entry.grid(row=3, column=1, columnspan=2, sticky="we", pady=6)
        ttk.Button(bar, text="浏览...", command=self._pick_manifest).grid(
            row=3, column=3, padx=4, pady=6)

        # row 4：输出目录
        ttk.Label(bar, text="输出目录(--output):").grid(
            row=4, column=0, padx=(8, 2), pady=6, sticky="e")
        self.out_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.out_var, width=42).grid(
            row=4, column=1, columnspan=2, sticky="we", pady=6)
        ttk.Button(bar, text="浏览...", command=self._pick_dir).grid(
            row=4, column=3, padx=4, pady=6)

        # row 5：数量限制 + 挑序号
        ttk.Label(bar, text="数量(--limit):").grid(row=5, column=0, padx=(8, 2), pady=6, sticky="e")
        self.limit_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.limit_var, width=10).grid(
            row=5, column=1, sticky="w", pady=6)
        ttk.Label(bar, text="挑序号(--pick):").grid(
            row=5, column=2, padx=(12, 2), pady=6, sticky="e")
        self.pick_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.pick_var, width=12).grid(
            row=5, column=3, sticky="w", pady=6)

        # row 6：每画廊限张 + 保存名单文件名
        ttk.Label(bar, text="每画廊限张(--pages):").grid(
            row=6, column=0, padx=(8, 2), pady=6, sticky="e")
        self.pages_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.pages_var, width=10).grid(
            row=6, column=1, sticky="w", pady=6)
        ttk.Label(bar, text="保存名单(--manifest):").grid(
            row=6, column=2, padx=(12, 2), pady=6, sticky="e")
        self.manifest_out_var = tk.StringVar(value="eh_manifest.json")
        ttk.Entry(bar, textvariable=self.manifest_out_var, width=14).grid(
            row=6, column=3, sticky="w", pady=6)

        # row 7：线程 / 延迟 / 冷却
        ttk.Label(bar, text="线程:").grid(row=7, column=0, padx=(8, 2), pady=6, sticky="e")
        self.workers_var = tk.StringVar(value="4")
        ttk.Entry(bar, textvariable=self.workers_var, width=6).grid(
            row=7, column=1, sticky="w", pady=6)
        opts = ttk.Frame(bar)
        opts.grid(row=7, column=2, columnspan=2, sticky="w", padx=(12, 2))
        ttk.Label(opts, text="延迟:").pack(side="left")
        self.delay_var = tk.StringVar(value="1.0")
        ttk.Entry(opts, textvariable=self.delay_var, width=6).pack(side="left", padx=(2, 10))
        ttk.Label(opts, text="冷却:").pack(side="left")
        self.cooldown_var = tk.StringVar(value="20")
        ttk.Entry(opts, textvariable=self.cooldown_var, width=6).pack(side="left", padx=(2, 0))

        # row 8：代理
        ttk.Label(bar, text="代理(--proxy):").grid(row=8, column=0, padx=(8, 2), pady=6, sticky="e")
        self.proxy_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.proxy_var, width=50).grid(
            row=8, column=1, columnspan=3, sticky="we", pady=6)

        # row 9：三个勾选框
        opts2 = ttk.Frame(bar)
        opts2.grid(row=9, column=0, columnspan=4, sticky="w", padx=8, pady=2)
        self.dry_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts2, text="只列名单(--dry-run)",
                        variable=self.dry_var).pack(side="left")
        self.force_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts2, text="重新下载(--force)",
                        variable=self.force_var).pack(side="left", padx=(10, 0))
        self.no_preflight_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts2, text="跳过预检(--no-preflight)",
                        variable=self.no_preflight_var).pack(side="left", padx=(10, 0))

        # row 10：提示
        ttk.Label(bar, text="提示：代理/输出目录/数量等留空 = 用脚本默认；标签语法如 "
                            "language:chinese$ / female:feline / -male:feline（空格分隔多个）；"
                            "--limit 搜索模式作用于画廊、单画廊模式作用于图片；"
                            "「挑序号」「每画廊限张」「只列名单」主要用于搜索流程",
                  foreground="gray", wraplength=680, justify="left"
                  ).grid(row=10, column=0, columnspan=4, padx=8, pady=(2, 6), sticky="w")
        bar.columnconfigure(1, weight=1)

        # 控制行
        act = ttk.Frame(self.root)
        act.pack(fill="x", padx=10, pady=4)
        self.start_btn = ttk.Button(act, text="▶ 开始", command=self._start)
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(act, text="■ 停止", command=self._stop, state="disabled")
        self.stop_btn.pack(side="left", padx=8)
        self.status_var = tk.StringVar(value="空闲")
        ttk.Label(act, textvariable=self.status_var).pack(side="left", padx=12)

        # 日志区
        logf = ttk.LabelFrame(self.root, text=" 运行日志 ")
        logf.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.log_text = tk.Text(logf, wrap="word", state="disabled",
                                font=("Microsoft YaHei UI", 9))
        sb = ttk.Scrollbar(logf, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

        self._on_mode()

    # ------------------------------------------------------------
    # 交互
    # ------------------------------------------------------------
    def _on_mode(self):
        """切换模式时，把不相干的入口框灰掉。"""
        mode = self.mode_var.get()
        if mode == "标签搜索":
            self.tags_entry.config(state="normal")
            self.url_entry.config(state="disabled")
            self.mf_entry.config(state="disabled")
        elif mode == "单画廊(URL)":
            self.tags_entry.config(state="disabled")
            self.url_entry.config(state="normal")
            self.mf_entry.config(state="disabled")
        else:  # 从名单挑
            self.tags_entry.config(state="disabled")
            self.url_entry.config(state="disabled")
            self.mf_entry.config(state="normal")

    def _pick_dir(self):
        d = filedialog.askdirectory(title="选择输出目录")
        if d:
            self.out_var.set(d)

    def _pick_manifest(self):
        f = filedialog.askopenfilename(title="选择名单文件", filetypes=[("JSON", "*.json"),
                                                                       ("所有文件", "*.*")])
        if f:
            self.from_manifest_var.set(f)

    # ------------------------------------------------------------
    # 命令拼装
    # ------------------------------------------------------------
    def _build_args(self):
        """把表单拼成 EH_scraper_v2.py 的参数列表（不含 python/脚本名）。"""
        argv = []
        mode = self.mode_var.get()

        if mode == "标签搜索":
            tags = self.tags_var.get().strip()
            if not tags:
                raise ValueError("标签搜索模式需要填写标签(--tags)")
            argv += ["--tags", tags]
        elif mode == "单画廊(URL)":
            url = self.url_var.get().strip()
            if not url:
                raise ValueError("单画廊模式需要填写画廊 URL")
            argv += [url]
        else:  # 从名单挑
            mf = self.from_manifest_var.get().strip()
            if not mf:
                raise ValueError("从名单模式需要选择名单文件(--from-manifest)")
            argv += ["--from-manifest", mf]

        # 通用参数
        if self.out_var.get().strip():
            argv += ["--output", self.out_var.get().strip()]
        if self.limit_var.get().strip():
            argv += ["--limit", self.limit_var.get().strip()]
        if self.pick_var.get().strip():
            argv += ["--pick", self.pick_var.get().strip()]
        if self.pages_var.get().strip():
            argv += ["--pages", self.pages_var.get().strip()]
        # --manifest 只在 dry-run 时用于「把名单存到哪」，非 dry-run 下传了也会被忽略
        if self.dry_var.get():
            argv += ["--dry-run"]
            if self.manifest_out_var.get().strip():
                argv += ["--manifest", self.manifest_out_var.get().strip()]
        if self.workers_var.get().strip():
            argv += ["--workers", self.workers_var.get().strip()]
        if self.delay_var.get().strip():
            argv += ["--delay", self.delay_var.get().strip()]
        if self.cooldown_var.get().strip():
            argv += ["--cooldown", self.cooldown_var.get().strip()]
        if self.force_var.get():
            argv += ["--force"]
        if self.proxy_var.get().strip():
            argv += ["--proxy", self.proxy_var.get().strip()]
        if self.no_preflight_var.get():
            argv += ["--no-preflight"]
        return argv

    # ------------------------------------------------------------
    # 运行控制
    # ------------------------------------------------------------
    def _log(self, msg):
        self.queue.put(str(msg))

    def _poll(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                self.log_text.configure(state="normal")
                self.log_text.insert("end", msg + "\n")
                self.log_text.see("end")
                self.log_text.configure(state="disabled")
        except queue.Empty:
            pass
        if self.proc is not None and self.proc.poll() is not None:
            self._on_done(self.proc.returncode)
            self.proc = None
        self.root.after(100, self._poll)

    def _start(self):
        if self.proc is not None and self.proc.poll() is None:
            messagebox.showinfo("提示", "任务正在运行中")
            return
        if not SCRAPER.exists():
            messagebox.showerror("错误", f"找不到 {SCRAPER.name}，请确认它在同一目录。")
            return
        try:
            args = self._build_args()
        except ValueError as e:
            messagebox.showwarning("参数错误", str(e))
            return

        cmd = [sys.executable, str(SCRAPER)] + args
        self._log(">>> " + " ".join(cmd))
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     text=True, encoding="utf-8", errors="replace", bufsize=1,
                                     cwd=str(HERE))
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_var.set("运行中...")
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self):
        try:
            for line in self.proc.stdout:
                self._log(line.rstrip("\n"))
        except Exception:
            pass

    def _on_done(self, code):
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set(f"完成（退出码 {code}）")
        self._log(f"[进程结束，退出码 {code}]")

    def _stop(self):
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            self.status_var.set("正在停止...")
            self._log("已请求停止")


def selftest():
    """无窗口自检：验证 tkinter 可用、组件能构建、命令拼装正确（不联网、不起子进程）。"""
    print("=== EH_gui selftest ===")
    root = tk.Tk()
    root.withdraw()
    gui = EHGUI(root)

    # 1) 标签搜索
    gui.mode_var.set("标签搜索")
    gui._on_mode()
    gui.tags_var.set("language:chinese$ female:feline")
    gui.limit_var.set("10")
    gui.dry_var.set(True)
    cmd = gui._build_args()
    print("搜索模式:", cmd)
    assert "--tags" in cmd and "--dry-run" in cmd and "--limit" in cmd

    # 2) 单画廊
    gui.mode_var.set("单画廊(URL)")
    gui._on_mode()
    gui.url_var.set("https://e-hentai.org/g/3817181/3b0370c5a1/")
    gui.dry_var.set(False)
    gui.pick_var.set("2-4,7")
    cmd2 = gui._build_args()
    print("单画廊模式:", cmd2)
    assert "https://e-hentai.org/g/3817181/3b0370c5a1/" in cmd2 and "--pick" in cmd2

    # 3) 从名单挑
    gui.mode_var.set("从名单挑")
    gui._on_mode()
    gui.from_manifest_var.set("eh_manifest.json")
    cmd3 = gui._build_args()
    print("从名单模式:", cmd3)
    assert "--from-manifest" in cmd3

    # 4) 缺参数要报 ValueError
    gui.mode_var.set("标签搜索")
    gui._on_mode()
    gui.tags_var.set("")
    try:
        gui._build_args()
        raise AssertionError("标签搜索漏填标签却没有报错")
    except ValueError:
        pass

    root.destroy()
    print("OK：窗口构建 + 命令拼装全部通过。")
    return 0


def _apply_icon(root):
    ico = HERE / "assets" / "icon.ico"
    if ico.exists():
        try:
            root.iconbitmap(str(ico))
        except Exception:
            pass


def main():
    if "--selftest" in sys.argv:
        return selftest()
    root = tk.Tk()
    _apply_icon(root)
    EHGUI(root)
    root.mainloop()


if __name__ == "__main__":
    sys.exit(main())
