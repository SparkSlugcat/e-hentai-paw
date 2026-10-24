#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_privacy.py — 扫产物里有没有本机路径 / 用户名
====================================================

打包完、以及**任何对外发布之前**跑一次。纯离线，不联网。

用法：

    python check_privacy.py dist\\EHPaw.exe
    python check_privacy.py dist\\EHPaw.exe <用户名> "D:\\项目\\e-hentai-paw"

第二个/第三个参数可选，分别是「用户名」和「项目目录」，默认从环境变量取
（USERNAME / 当前目录），所以一般直接给个文件名就够。

为什么需要它
------------
PyInstaller 会把每个模块的源码绝对路径（`co_filename`）编进 `.pyc`，`.pyc` 再被打进 exe。
在带用户名的目录（`C:\\Users\\<用户名>\\...`）里直接打包，产物就能被 `strings` 搜出
整条目录树。所以构建脚本会先把源码复制到中性路径再打（见 EHPaw.spec / 打包脚本），
这个脚本就是**最后一道验收**：万一哪天有人改回原地打包，这里会立刻拦下来。

强命中 vs 弱命中（重要）
------------------------
- **强命中** = 路径形态：反斜杠夹住用户名（`\用户名\`）、`Users\用户名`、整个项目目录串。
  这种东西不可能是压缩数据的巧合 → 直接判失败（退出码 1）。
- **弱命中** = 裸的用户名。三个字母在 36 MB 的压缩二进制里几乎必然出现几次，
  属于噪声（e621 的 icon.ico 里就出现过同样的假阳性）。只提示 + 打印上下文，不判失败。

只按字节搜三种编码（utf-8 / utf-16-le / gbk）—— `co_filename` 在 .pyc 里是 utf-8。

输出全用 ASCII：Windows 控制台是 GBK，中文夹在批处理输出里会变乱码。
"""

import os
import sys
from pathlib import Path

ENCODINGS = ("utf-8", "utf-16-le", "gbk")


def _variants(text: str):
    out = []
    for enc in ENCODINGS:
        try:
            b = text.encode(enc)
        except UnicodeEncodeError:
            continue
        if b and b not in out:
            out.append(b)
    return out


def strong_patterns(username: str, project_dir: str):
    """路径形态：一旦出现就是真的泄露。"""
    pats = []
    if username and len(username) >= 3:
        for form in ("\\%s\\" % username,        # ...\<user>\...
                     "Users\\%s" % username,     # C:\Users\<user>
                     "Users/%s" % username,      # C:/Users/<user>
                     "/%s/" % username):         # /home/<user>
            pats.extend(_variants(form))
    if project_dir:
        p = project_dir.rstrip("\\/")
        if len(p) >= 6:
            for form in (p, p.replace("\\", "/")):
                pats.extend(_variants(form))
    return pats


def weak_patterns(username: str):
    if username and len(username) >= 3:
        return _variants(username)
    return []


def scan(data: bytes, patterns, limit=5):
    """返回 [(offset, pattern_bytes)]，最多 limit 条。"""
    hits = []
    for pat in patterns:
        start = 0
        while True:
            i = data.find(pat, start)
            if i < 0:
                break
            hits.append((i, pat))
            if len(hits) >= limit:
                return hits
            start = i + len(pat)
    return hits


def context(data: bytes, off: int, span: int = 40) -> str:
    lo, hi = max(0, off - span), min(len(data), off + span)
    return "".join(chr(b) if 32 <= b < 127 else "." for b in data[lo:hi])


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: python check_privacy.py <file> [username] [project_dir]")
        return 2

    target = Path(argv[0])
    username = argv[1] if len(argv) > 1 else os.environ.get("USERNAME", "")
    project_dir = argv[2] if len(argv) > 2 else os.getcwd()

    # 批处理里 `"%~dp0"` 会踩一个坑：路径末尾的反斜杠会把结束引号转义掉，
    # 于是传进来的是 `D:\...\e-hentai-paw"`（带个尾引号）。这里兜一下，
    # 否则项目目录这一档检查会静默失效。
    project_dir = project_dir.strip().strip('"').strip()

    if not target.is_file():
        print("[privacy] file not found: %s" % target)
        return 2

    data = target.read_bytes()
    print("[privacy] file     : %s (%.1f MB)" % (target, len(data) / 1048576))
    print("[privacy] username : %s" % (username or "(none)"))
    print("[privacy] project  : %s" % project_dir)

    strong = scan(data, strong_patterns(username, project_dir))
    weak = scan(data, weak_patterns(username))

    if strong:
        print("[privacy] FAIL - %d path-like hit(s):" % len(strong))
        for off, pat in strong:
            shown = pat.decode("utf-8", "replace").encode("ascii", "replace").decode("ascii")
            print("  0x%08X  %-24s  %s" % (off, shown, context(data, off)))
        print("[privacy] -> the exe carries a local path. Do NOT ship it.")
        return 1

    if weak:
        print("[privacy] WARN - %d bare-username hit(s), likely compressed-data noise:"
              % len(weak))
        for off, _pat in weak:
            print("  0x%08X  %s" % (off, context(data, off)))
        print("[privacy] -> judge by context: real leaks have readable paths around them.")

    print("[privacy] OK  - no local path patterns found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
