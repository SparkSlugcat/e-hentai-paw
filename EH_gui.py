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

import i18n

HERE = Path(__file__).resolve().parent
SCRAPER = HERE / "EH_scraper_v2.py"

# ---------------------------------------------------------------
# 打包（PyInstaller）相关
# ---------------------------------------------------------------
# 源码态：__file__ 在项目目录，sys.executable 是 python.exe。
# 打包后：__file__ 在 %TEMP%\_MEIxxxx（每次启动解压一次、退出即删），
#         sys.executable 是 EHPaw.exe 自己 —— 磁盘上**没有** EH_scraper_v2.py，
#         也没有 python.exe 可以拿来起子进程。
# 所以 packaged 时改成「自己起自己」：EHPaw.exe --run-scraper <原来的参数>，
# 第二个实例的 main() 看到这个标志就只跑抓取器、不开窗口。
FROZEN = bool(getattr(sys, "frozen", False))
FROZEN_FLAG = "--run-scraper"
# 用户眼里的"程序在哪"：打包后是 exe 所在目录，而不是临时解压目录
APP_DIR = Path(sys.executable).resolve().parent if FROZEN else HERE


def mode_labels():
    """三个互斥的入口：标签搜索 / 单画廊 URL / 从名单挑（--from-manifest）。

    顺序固定不变 —— 切语言后按 index 复原选择，不靠文案字符串匹配。
    """
    return [i18n.t("gui_mode_tags"), i18n.t("gui_mode_gallery"),
            i18n.t("gui_mode_manifest")]


MODES = mode_labels()

#: 站点是专有名词，中英都不翻译，所以直接用固定字面量 + index 定位。
#: 表站在前（默认），里站在后。
SITES = ("e-hentai", "exhentai")


class EHGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.geometry("720x640")
        self.queue = queue.Queue()
        self.proc = None
        self._mode_idx = 0                       # 当前模式下标（切语言靠它复原）
        self._status_key, self._status_kw = "gui_status_idle", {}
        self._init_vars()
        self._build_ui()
        # 每 100ms 轮询一次：把队列里的日志刷进文本框，并检查子进程是否结束
        root.after(100, self._poll)

    # ------------------------------------------------------------
    # 变量只建一次：重建界面时复用，用户已填的值自动保留
    # ------------------------------------------------------------
    def _init_vars(self):
        self.lang_var = tk.StringVar(
            value=i18n.LANG_NAMES[0 if i18n.get_lang() == "zh" else 1])
        self.mode_var = tk.StringVar(value=mode_labels()[self._mode_idx])
        self.tags_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.from_manifest_var = tk.StringVar()
        self.out_var = tk.StringVar()
        self.limit_var = tk.StringVar()
        self.pick_var = tk.StringVar()
        self.pages_var = tk.StringVar()
        self.manifest_out_var = tk.StringVar(value="eh_manifest.json")
        #: 站点 / cookie：里站入口。cookie 留空 = 让脚本自己找 .ehcookie（推荐）
        self.site_var = tk.StringVar(value=SITES[0])
        self.cookie_file_var = tk.StringVar()
        self.workers_var = tk.StringVar(value="4")
        self.delay_var = tk.StringVar(value="1.0")
        self.cooldown_var = tk.StringVar(value="20")
        self.proxy_var = tk.StringVar()
        self.dry_var = tk.BooleanVar(value=False)
        self.force_var = tk.BooleanVar(value=False)
        self.no_preflight_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value=i18n.t(self._status_key))

    # ------------------------------------------------------------
    # 界面搭建
    # ------------------------------------------------------------
    def _build_ui(self):
        # 先取回日志框现有文本 + 按钮状态，重建后原样恢复（历史日志不重译）
        old_log = ""
        if getattr(self, "log_text", None) is not None:
            old_log = self.log_text.get("1.0", "end-1c")
        start_state = self.start_btn.cget("state") if hasattr(self, "start_btn") else "normal"
        stop_state = self.stop_btn.cget("state") if hasattr(self, "stop_btn") else "disabled"
        for name in ("_lang_bar", "_bar_frame", "_act_frame", "_log_frame"):
            w = getattr(self, name, None)
            if w is not None:
                w.destroy()
                setattr(self, name, None)

        self.root.title(i18n.t("gui_title"))

        # 顶部小横条：语言下拉框靠右，不占用参数区的 grid 编号
        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=(8, 0))
        self._lang_bar = top
        self.lang_var.set(i18n.LANG_NAMES[0 if i18n.get_lang() == "zh" else 1])
        lang_cb = ttk.Combobox(top, textvariable=self.lang_var, width=9,
                               state="readonly", values=list(i18n.LANG_NAMES))
        lang_cb.pack(side="right")
        lang_cb.bind("<<ComboboxSelected>>", self._on_lang_change)
        ttk.Label(top, text=i18n.t("gui_lang_label")).pack(side="right", padx=(0, 4))

        bar = ttk.LabelFrame(self.root, text=i18n.t("gui_params"))
        bar.pack(fill="x", padx=10, pady=8)
        self._bar_frame = bar

        # row 0：模式
        ttk.Label(bar, text=i18n.t("gui_mode_label")).grid(
            row=0, column=0, padx=(8, 2), pady=6, sticky="e")
        modes = mode_labels()
        self.mode_var.set(modes[self._mode_idx])
        self.mode_cb = ttk.Combobox(bar, textvariable=self.mode_var, values=modes,
                                    state="readonly", width=14)
        self.mode_cb.grid(row=0, column=1, padx=2, pady=6, sticky="w")
        self.mode_cb.current(self._mode_idx)
        self.mode_cb.bind("<<ComboboxSelected>>", lambda e: self._on_mode())

        # row 0 右半：站点（表站 / 里站）。放在模式旁边，因为它和"这次要访问哪儿"同类
        ttk.Label(bar, text=i18n.t("gui_site_label")).grid(
            row=0, column=2, padx=(14, 2), pady=6, sticky="e")
        self.site_cb = ttk.Combobox(bar, textvariable=self.site_var, values=list(SITES),
                                    state="readonly", width=11)
        self.site_cb.grid(row=0, column=3, padx=2, pady=6, sticky="w")
        self.site_cb.current(self._site_index())

        # row 1：标签（搜索模式用）
        ttk.Label(bar, text=i18n.t("gui_tags_label")).grid(
            row=1, column=0, padx=(8, 2), pady=6, sticky="e")
        self.tags_entry = ttk.Entry(bar, textvariable=self.tags_var, width=50)
        self.tags_entry.grid(row=1, column=1, columnspan=3, sticky="we", pady=6)

        # row 2：画廊 URL（单画廊模式用）
        ttk.Label(bar, text=i18n.t("gui_url_label")).grid(
            row=2, column=0, padx=(8, 2), pady=6, sticky="e")
        self.url_entry = ttk.Entry(bar, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=2, column=1, columnspan=3, sticky="we", pady=6)

        # row 3：名单文件（从名单挑模式用）
        ttk.Label(bar, text=i18n.t("gui_manifest_in_label")).grid(
            row=3, column=0, padx=(8, 2), pady=6, sticky="e")
        self.mf_entry = ttk.Entry(bar, textvariable=self.from_manifest_var, width=42)
        self.mf_entry.grid(row=3, column=1, columnspan=2, sticky="we", pady=6)
        ttk.Button(bar, text=i18n.t("gui_browse"), command=self._pick_manifest).grid(
            row=3, column=3, padx=4, pady=6)

        # row 4：输出目录
        ttk.Label(bar, text=i18n.t("gui_output_label")).grid(
            row=4, column=0, padx=(8, 2), pady=6, sticky="e")
        ttk.Entry(bar, textvariable=self.out_var, width=42).grid(
            row=4, column=1, columnspan=2, sticky="we", pady=6)
        ttk.Button(bar, text=i18n.t("gui_browse"), command=self._pick_dir).grid(
            row=4, column=3, padx=4, pady=6)

        # row 5：数量限制 + 挑序号
        ttk.Label(bar, text=i18n.t("gui_limit_label")).grid(
            row=5, column=0, padx=(8, 2), pady=6, sticky="e")
        ttk.Entry(bar, textvariable=self.limit_var, width=10).grid(
            row=5, column=1, sticky="w", pady=6)
        ttk.Label(bar, text=i18n.t("gui_pick_label")).grid(
            row=5, column=2, padx=(12, 2), pady=6, sticky="e")
        ttk.Entry(bar, textvariable=self.pick_var, width=12).grid(
            row=5, column=3, sticky="w", pady=6)

        # row 6：每画廊限张 + 保存名单文件名
        ttk.Label(bar, text=i18n.t("gui_pages_label")).grid(
            row=6, column=0, padx=(8, 2), pady=6, sticky="e")
        ttk.Entry(bar, textvariable=self.pages_var, width=10).grid(
            row=6, column=1, sticky="w", pady=6)
        ttk.Label(bar, text=i18n.t("gui_manifest_out_label")).grid(
            row=6, column=2, padx=(12, 2), pady=6, sticky="e")
        ttk.Entry(bar, textvariable=self.manifest_out_var, width=14).grid(
            row=6, column=3, sticky="w", pady=6)

        # row 7：线程 / 延迟 / 冷却
        ttk.Label(bar, text=i18n.t("gui_workers_label")).grid(
            row=7, column=0, padx=(8, 2), pady=6, sticky="e")
        ttk.Entry(bar, textvariable=self.workers_var, width=6).grid(
            row=7, column=1, sticky="w", pady=6)
        opts = ttk.Frame(bar)
        opts.grid(row=7, column=2, columnspan=2, sticky="w", padx=(12, 2))
        ttk.Label(opts, text=i18n.t("gui_delay_label")).pack(side="left")
        ttk.Entry(opts, textvariable=self.delay_var, width=6).pack(side="left", padx=(2, 10))
        ttk.Label(opts, text=i18n.t("gui_cooldown_label")).pack(side="left")
        ttk.Entry(opts, textvariable=self.cooldown_var, width=6).pack(side="left", padx=(2, 0))

        # row 8：代理
        ttk.Label(bar, text=i18n.t("gui_proxy_label")).grid(
            row=8, column=0, padx=(8, 2), pady=6, sticky="e")
        ttk.Entry(bar, textvariable=self.proxy_var, width=50).grid(
            row=8, column=1, columnspan=3, sticky="we", pady=6)

        # row 9：cookie 文件（里站用；留空 = 脚本自己找 .ehcookie）
        ttk.Label(bar, text=i18n.t("gui_cookie_file_label")).grid(
            row=9, column=0, padx=(8, 2), pady=6, sticky="e")
        ttk.Entry(bar, textvariable=self.cookie_file_var, width=42).grid(
            row=9, column=1, columnspan=2, sticky="we", pady=6)
        ttk.Button(bar, text=i18n.t("gui_browse"), command=self._pick_cookie_file).grid(
            row=9, column=3, padx=4, pady=6)

        # row 10：三个勾选框
        opts2 = ttk.Frame(bar)
        opts2.grid(row=10, column=0, columnspan=4, sticky="w", padx=8, pady=2)
        ttk.Checkbutton(opts2, text=i18n.t("gui_dry_run"),
                        variable=self.dry_var).pack(side="left")
        ttk.Checkbutton(opts2, text=i18n.t("gui_force"),
                        variable=self.force_var).pack(side="left", padx=(10, 0))
        ttk.Checkbutton(opts2, text=i18n.t("gui_no_preflight"),
                        variable=self.no_preflight_var).pack(side="left", padx=(10, 0))

        # row 11：提示
        ttk.Label(bar, text=i18n.t("gui_hint"),
                  foreground="gray", wraplength=680, justify="left"
                  ).grid(row=11, column=0, columnspan=4, padx=8, pady=(2, 6), sticky="w")
        bar.columnconfigure(1, weight=1)

        # 控制行
        act = ttk.Frame(self.root)
        act.pack(fill="x", padx=10, pady=4)
        self._act_frame = act
        self.start_btn = ttk.Button(act, text=i18n.t("gui_start"), command=self._start)
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(act, text=i18n.t("gui_stop"), command=self._stop,
                                   state="disabled")
        self.stop_btn.pack(side="left", padx=8)
        ttk.Label(act, textvariable=self.status_var).pack(side="left", padx=12)

        # 日志区
        logf = ttk.LabelFrame(self.root, text=i18n.t("gui_log_frame"))
        logf.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._log_frame = logf
        self.log_text = tk.Text(logf, wrap="word", state="disabled",
                                font=("Microsoft YaHei UI", 9))
        sb = ttk.Scrollbar(logf, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

        self._on_mode()

        # 恢复日志文本 / 按钮状态 / 状态栏（都按当前语言重新渲染，历史日志不动）
        if old_log:
            self.log_text.configure(state="normal")
            self.log_text.insert("1.0", old_log)
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        self.start_btn.config(state=start_state)
        self.stop_btn.config(state=stop_state)
        self.status_var.set(i18n.t(self._status_key, **self._status_kw))

    # ------------------------------------------------------------
    # 交互
    # ------------------------------------------------------------
    def _on_lang_change(self, event=None):
        new = "zh" if self.lang_var.get() == i18n.LANG_NAMES[0] else "en"
        if new == i18n.get_lang():
            return
        i18n.set_lang(new)          # 同时写偏好
        self._build_ui()            # 重建
        self._log(i18n.t("gui_lang_switched",
                         lang=i18n.LANG_NAMES[0 if new == "zh" else 1]))

    def _set_status(self, key, **kw):
        """状态栏按 key 存，重建界面后能用新语言重渲染。"""
        self._status_key, self._status_kw = key, kw
        self.status_var.set(i18n.t(key, **kw))

    def _mode_index(self):
        """当前模式的 index（Combobox 只读，index 才是切语言后可靠的标识）。"""
        idx = self.mode_cb.current() if getattr(self, "mode_cb", None) is not None else -1
        if 0 <= idx < len(mode_labels()):
            self._mode_idx = idx
        return self._mode_idx

    def _site_index(self):
        """当前站点的 index：0=表站 1=里站。

        站点名是专有名词，中英一样，但同样用 index 判断 —— 以后要加第三个站
        （比如里站的某个镜像）时，不用回来改判断逻辑。
        """
        v = (self.site_var.get() or "").strip().lower()
        return 1 if v.startswith("ex") else 0

    def _select_mode(self, idx):
        """按 index 选模式（自检用；不依赖当前语言下的文案）。"""
        self._mode_idx = idx
        self.mode_var.set(mode_labels()[idx])
        self.mode_cb.current(idx)
        self._on_mode()

    def _on_mode(self):
        """切换模式时，把不相干的入口框灰掉。"""
        idx = self._mode_index()
        if idx == 0:                 # 标签搜索
            self.tags_entry.config(state="normal")
            self.url_entry.config(state="disabled")
            self.mf_entry.config(state="disabled")
        elif idx == 1:               # 单画廊(URL)
            self.tags_entry.config(state="disabled")
            self.url_entry.config(state="normal")
            self.mf_entry.config(state="disabled")
        else:                        # 从名单挑
            self.tags_entry.config(state="disabled")
            self.url_entry.config(state="disabled")
            self.mf_entry.config(state="normal")

    def _pick_dir(self):
        d = filedialog.askdirectory(title=i18n.t("gui_dlg_output_dir"))
        if d:
            self.out_var.set(d)

    def _pick_manifest(self):
        f = filedialog.askopenfilename(title=i18n.t("gui_dlg_manifest_file"),
                                       filetypes=[("JSON", "*.json"),
                                                  (i18n.t("gui_filetype_all"), "*.*")])
        if f:
            self.from_manifest_var.set(f)

    def _pick_cookie_file(self):
        f = filedialog.askopenfilename(
            title=i18n.t("gui_dlg_cookie_file"),
            filetypes=[(i18n.t("gui_filetype_cookie"), "*.txt *.ehcookie"),
                       (i18n.t("gui_filetype_all"), "*.*")])
        if f:
            self.cookie_file_var.set(f)

    # ------------------------------------------------------------
    # 命令拼装
    # ------------------------------------------------------------
    def _build_args(self):
        """把表单拼成 EH_scraper_v2.py 的参数列表（不含 python/脚本名）。"""
        argv = []
        idx = self._mode_index()

        if idx == 0:                     # 标签搜索
            tags = self.tags_var.get().strip()
            if not tags:
                raise ValueError(i18n.t("gui_err_need_tags"))
            argv += ["--tags", tags]
        elif idx == 1:                   # 单画廊(URL)
            url = self.url_var.get().strip()
            if not url:
                raise ValueError(i18n.t("gui_err_need_url"))
            argv += [url]
        else:                            # 从名单挑
            mf = self.from_manifest_var.get().strip()
            if not mf:
                raise ValueError(i18n.t("gui_err_need_manifest"))
            argv += ["--from-manifest", mf]

        # 通用参数
        # --site 只在选了里站时才传：表站是默认值，传了反而会盖掉「按 URL 域名自动切站」
        if self._site_index() == 1:
            argv += ["--site", SITES[1]]
        if self.cookie_file_var.get().strip():
            argv += ["--cookie-file", self.cookie_file_var.get().strip()]
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
            messagebox.showinfo(i18n.t("gui_msg_running_title"), i18n.t("gui_msg_running"))
            return
        if not FROZEN and not SCRAPER.exists():
            messagebox.showerror(i18n.t("gui_err_title"),
                                 i18n.t("gui_err_scraper_missing", name=SCRAPER.name))
            return
        try:
            args = self._build_args()
        except ValueError as e:
            messagebox.showwarning(i18n.t("gui_err_args_title"), str(e))
            return

        # 源码态：python.exe EH_scraper_v2.py <args>
        # 打包态：EHPaw.exe --run-scraper <args>（自调用分派，见 main()）
        if FROZEN:
            cmd = [sys.executable, FROZEN_FLAG] + args
        else:
            cmd = [sys.executable, str(SCRAPER)] + args
        self._log(">>> " + " ".join(cmd))
        # 子进程靠 PAW_LANG 决定日志语言；必须复制 os.environ，否则丢 PATH
        env = os.environ.copy()
        env[i18n.LANG_ENV] = i18n.get_lang()
        # 打包后 common.local_out_root() 读不到项目根的 .pawout（它的 __file__ 在临时解压目录），
        # 会退化到 Path(".") —— 那是 _MEIPASS，图片解完随程序退出一起消失。
        # 所以这里按「exe 旁边的 .pawout」→「exe 旁边的 downloads\」的顺序兜底，
        # 走 local_out_root() 的第一优先级环境变量，不用改 common.py。
        if FROZEN and not env.get("PAW_OUT_DIR") and not self.out_var.get().strip():
            env["PAW_OUT_DIR"] = str(_packaged_out_root())
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     text=True, encoding="utf-8", errors="replace", bufsize=1,
                                     cwd=str(APP_DIR), env=env)
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self._set_status("gui_status_running")
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
        self._set_status("gui_status_done", code=code)
        self._log(i18n.t("gui_proc_exit", code=code))

    def _stop(self):
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            self._set_status("gui_status_stopping")
            self._log(i18n.t("gui_stop_requested"))


def selftest():
    """无窗口自检：验证 tkinter 可用、组件能构建、命令拼装正确（不联网、不起子进程）。"""
    print("=== EH_gui selftest ===")
    print("frozen=%s | python=%s | script_dir=%s" % (FROZEN, sys.version.split()[0], APP_DIR))
    if FROZEN:
        print("_MEIPASS=%s" % getattr(sys, "_MEIPASS", None))
        # 关键验证：抓取器作为一个模块真的被打进 exe 了吗（自调用分支靠它）
        try:
            _m = __import__("EH_scraper_v2")
            print("scraper_module=%s | main=%s"
                  % (getattr(_m, "__file__", "?"), callable(getattr(_m, "main", None))))
        except Exception as exc:
            print("scraper_module 导入失败: %r" % (exc,))
    root = tk.Tk()
    root.withdraw()
    gui = EHGUI(root)

    # 1) 标签搜索
    gui._select_mode(0)
    gui.tags_var.set("language:chinese$ female:cat")
    gui.limit_var.set("10")
    gui.dry_var.set(True)
    cmd = gui._build_args()
    print(i18n.t("gui_selftest_search"), cmd)
    assert "--tags" in cmd and "--dry-run" in cmd and "--limit" in cmd

    # 2) 单画廊
    gui._select_mode(1)
    gui.url_var.set("https://e-hentai.org/g/123456/abcdef1234/")
    gui.dry_var.set(False)
    gui.pick_var.set("2-4,7")
    cmd2 = gui._build_args()
    print(i18n.t("gui_selftest_gallery"), cmd2)
    assert "https://e-hentai.org/g/123456/abcdef1234/" in cmd2 and "--pick" in cmd2

    # 2.5 里站：必须带上 --site exhentai，表站则**不能**带（否则会盖掉 URL 自动切站）
    gui.site_var.set(SITES[1])
    gui.cookie_file_var.set(".ehcookie")
    cmd2b = gui._build_args()
    print(i18n.t("gui_selftest_site"), cmd2b)
    assert "--site" in cmd2b and "exhentai" in cmd2b and "--cookie-file" in cmd2b
    gui.site_var.set(SITES[0])
    gui.cookie_file_var.set("")
    cmd2c = gui._build_args()
    print(i18n.t("gui_selftest_public"), cmd2c)
    assert "--site" not in cmd2c and "--cookie-file" not in cmd2c


    # 3) 从名单挑
    gui._select_mode(2)
    gui.from_manifest_var.set("eh_manifest.json")
    cmd3 = gui._build_args()
    print(i18n.t("gui_selftest_manifest"), cmd3)
    assert "--from-manifest" in cmd3

    # 4) 缺参数要报 ValueError
    gui._select_mode(0)
    gui.tags_var.set("")
    try:
        gui._build_args()
        raise AssertionError(i18n.t("gui_selftest_assert_tags"))
    except ValueError:
        pass

    # 5) 语言切换：顶部那个「语言:」标签必须跟着变
    #    这条专门防一种回归 —— 标签如果只在启动时算一次、重建界面时不重算，
    #    就会出现「切到中文了，标签还是 Language:」这种半中半英的界面。
    _orig_lang = i18n.get_lang()
    for _lang, _expect in (("zh", "语言:"), ("en", "Language:")):
        i18n.set_lang(_lang, persist=False)
        gui._build_ui()
        root.update_idletasks()
        _labels = [w.cget("text") for w in gui._lang_bar.winfo_children()
                   if w.winfo_class() == "TLabel"]
        _combo = [w.get() for w in gui._lang_bar.winfo_children()
                  if w.winfo_class() == "TCombobox"]
        print(i18n.t("gui_selftest_lang"), _lang, _labels, _combo)
        assert _expect in _labels, "语言标签没跟着切: %s -> %r" % (_lang, _labels)
        assert _combo and _combo[0] == i18n.LANG_NAMES[0 if _lang == "zh" else 1], \
            "语言下拉框没跟着切: %s -> %r" % (_lang, _combo)
    i18n.set_lang(_orig_lang, persist=False)
    gui._build_ui()

    root.destroy()
    print(i18n.t("gui_selftest_ok"))
    return 0


def _packaged_out_root():
    """打包后「默认下载到哪」：exe 旁边的 `.pawout`（有就用）> exe 旁边的 `downloads\\`。

    为什么不能靠 `common.local_out_root()` 自己找：它用 `common.__file__` 定位项目根的
    `.pawout`，而打包后那指向 `%TEMP%\\_MEIxxxx` —— 用户放 `.pawout` 只可能放在 exe 旁边。

    **这就是「日常版 / 发布版」的实际落点**：同一个 exe，旁边放一行路径的 `.pawout`
    就是自己的固定下载目录；不放就是干净的 `downloads\\`。不用打两个二进制。
    """
    cfg = APP_DIR / ".pawout"
    try:
        for line in cfg.read_text(encoding="utf-8-sig").splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                return Path(s).expanduser()
    except OSError:
        pass
    return APP_DIR / "downloads"


def _apply_icon(root):
    ico = HERE / "assets" / "icon.ico"
    if ico.exists():
        try:
            root.iconbitmap(str(ico))
        except Exception:
            pass


def _run_scraper(argv):
    """打包后的「抓取器分支」：`EHPaw.exe --run-scraper <args>`。

    这个进程是被 GUI 起来的后台子进程，不开窗口，只把 EH_scraper_v2 当模块
    跑一遍。stdout 已被父进程接成管道，print 的内容会流回 GUI 的日志框。
    """
    # windowed exe 在既无控制台、又无管道时 sys.stdout 会是 None，print() 直接
    # AttributeError。正常经 Popen(stdout=PIPE) 起的进程句柄有效、走不到这里；
    # 这个兜底只是保证「宁可没日志，也不崩」。
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = sys.stdout
    import EH_scraper_v2
    try:
        return EH_scraper_v2.main(argv)
    except SystemExit as exc:            # argparse 的 --help / 参数错误走这里
        return exc.code if isinstance(exc.code, int) else 0


def main():
    # 必须在 --selftest 之前：这是「同一个 exe 的第二个实例」的入口
    if sys.argv[1:2] == [FROZEN_FLAG]:
        return _run_scraper(sys.argv[2:])
    if "--selftest" in sys.argv:
        return selftest()
    root = tk.Tk()
    _apply_icon(root)
    EHGUI(root)
    root.mainloop()


if __name__ == "__main__":
    sys.exit(main())
