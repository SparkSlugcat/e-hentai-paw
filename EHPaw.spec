# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — e-hentai-paw（单文件 GUI exe）

构建（在本目录下执行，**这三个环境变量一个都不能少**）：

    set PYTHONPATH=<放 PyInstaller 的目录>
    set PATH=<env>\\Library\\bin;<env>\\DLLs;%PATH%
    python -m PyInstaller --noconfirm --clean EHPaw.spec

为什么不直接双击 build_exe.bat 就行：本文件已经替 bat 兜住了环境探测，
但如果要手打，PATH 那行漏了就会打出「双击没反应」的 exe（conda 把
tcl86t.dll / tk86t.dll 放在 <env>\\Library\\bin，不在 DLLs）。
"""

import os
import sys
from PyInstaller.utils.hooks import collect_all

HERE = os.path.abspath(SPECPATH)          # .../e-hentai-paw
ICON = os.path.join(HERE, "assets", "icon.ico")

datas = [(ICON, "assets")]
binaries = []

# EH_gui 里 `import EH_scraper_v2` 写在函数内部（自调用分派分支），
# 虽然 PyInstaller 的 AST 扫描通常能找到，仍显式声明，避免漏收。
hiddenimports = ["EH_scraper_v2", "common", "i18n", "lxml", "lxml.etree"]

# ---- conda 专用补丁：tcl/tk 的 DLL 在 <env>\Library\bin，不在 <env>\DLLs\ ----
# 不带这两个，打包时只会出一行 WARNING，产物却是双击完全没反应：
#   ImportError: DLL load failed while importing _tkinter
# 用 sys.prefix 定位，不写死本机路径 —— 换台机器打包也能用。
_ENV_LIB_BIN = os.path.join(sys.prefix, "Library", "bin")
for _dll in ("tcl86t.dll", "tk86t.dll", "ffi-8.dll"):
    _p = os.path.join(_ENV_LIB_BIN, _dll)
    if os.path.exists(_p):
        binaries.append((_p, "."))
    else:
        print("[spec] WARNING: %s 不存在，打出来的 exe 可能起不来" % _p)

# requests 带证书包（cacert.pem）等数据文件，必须整包收
_tmp = collect_all("requests")
datas += _tmp[0]
binaries += _tmp[1]
hiddenimports += _tmp[2]

a = Analysis(
    [os.path.join(HERE, "EH_gui.py")],
    pathex=[HERE],          # i18n / common / EH_scraper_v2 都在同目录
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="EHPaw",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,              # GUI 程序，不要黑窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[ICON],
)
