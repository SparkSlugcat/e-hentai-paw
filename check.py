#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""e-hentai-paw 网络预检 —— 单独跑一次链路体检，不下载任何东西。

它做的事和 EH_scraper_v2.py 发包前那一次 `Preflight` 完全一样，
只是独立成一个入口，方便排查"是不是 Clash 没开 / 节点不通"：

    第 1 段  探本地 Clash 端口（7897 / 7890 / 7891）
    第 2 段  用探到的代理去访问 https://e-hentai.org，看拿到什么状态码

用法：

    python check.py                 # 自动探测本地 Clash 端口
    python check.py --proxy off     # 强制直连（境外网络 / TUN 模式）
    python check.py --proxy http://127.0.0.1:7897

退出码：0 = 链路通，1 = 不通（输出里会说明是哪一段坏的）。
"""

import argparse
import os
import sys

# 让脚本在任何工作目录下都能找到同目录的 EH_scraper_v2.py / common.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import common
from EH_scraper_v2 import SITE, resolve_proxy


def main():
    ap = argparse.ArgumentParser(description="e-hentai-paw 网络预检（不发包下载）")
    ap.add_argument("--proxy", default=None,
                    help="留空 = 自动探测本地 Clash 端口；off = 直连；或写完整 URL")
    args = ap.parse_args()

    proxy, note = resolve_proxy(args.proxy)
    if note:
        print(note)
    print("本次实际使用: %s" % (proxy or "直连（没有代理）"))

    pf = common.check_proxy(proxy, SITE)
    level = "OK" if pf.ok else ("FAILED" if pf.fatal else "WARN")
    print("Preflight e-hentai: %s (%.1fs) - %s" % (level, pf.elapsed, pf.message))
    if pf.hint:
        print("  %s" % pf.hint)
    return 0 if pf.ok else 1


if __name__ == "__main__":
    sys.exit(main())
