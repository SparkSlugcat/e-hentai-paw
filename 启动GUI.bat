@echo off
chcp 936 >nul 2>&1
cd /d "%~dp0"

rem 第一行 chcp 的理由：本机系统 ANSI 代码页 = 936，这个文件也按
rem GBK 存（跟 pixivpaw 那份 启动.bat 一致），所以 cmd 默认就能正确
rem 解析下面的中文。万一哪天把终端改成 UTF-8 代码页，cmd 会拿
rem UTF-8 去解这份 GBK 文件、中文 echo 全变乱码 —— 这行是保险。

rem ============================================================
rem  e-hentai-paw GUI 启动器 —— 双击直接打开图形界面
rem
rem  自动定位能用的 Python 环境（扫 conda 的 envs），不依赖 PATH 里的 python。
rem  本文件不含任何绝对路径 / 用户名，换机器不用改。
rem
rem  参数 silent：连"出错要按任意键"都免了（保留兼容，日常可不传）。
rem ============================================================

set "SILENT="
if /i "%~1"=="silent" set "SILENT=1"

rem ==== 自动定位 Python 环境（本文件不含任何绝对路径 / 用户名）====
rem  按顺序取第一个【真能用】的：
rem    1) 环境变量 PYTHON_EXE —— 想手动指定就用它（指向哪里就信哪里）
rem    2) conda 的 envs 目录 —— 不猜环境名：挨个试一次导入，
rem       缺库的环境会被自动跳过（试的就是本项目真实依赖）
rem    3) 当前已激活的 conda 环境 %CONDA_PREFIX%
rem    4) PATH 里第一个 python
rem  换机器、换环境都不用改这个文件。
set "PY="
if defined PYTHON_EXE if exist "%PYTHON_EXE%" set "PY=%PYTHON_EXE%"
for %%R in ("%USERPROFILE%\miniconda3" "%USERPROFILE%\anaconda3" "%LOCALAPPDATA%\miniconda3" "%LOCALAPPDATA%\Continuum\anaconda3") do (
    for /d %%D in ("%%~R\envs\*") do if not defined PY if exist "%%~D\python.exe" (
        "%%~D\python.exe" -c "import requests, lxml" >nul 2>&1 && set "PY=%%~D\python.exe"
    )
)
if not defined PY if defined CONDA_PREFIX if exist "%CONDA_PREFIX%\python.exe" set "PY=%CONDA_PREFIX%\python.exe"
if not defined PY for /f "delims=" %%I in ('where python 2^>nul') do if not defined PY set "PY=%%I"
if defined PY for %%I in ("%PY%") do set "PYDIR=%%~dpI"
set "PYW=%PYDIR%pythonw.exe"

if not exist "%PY%"  goto :nopython
if not exist "%PYW%" goto :nopython

rem 先做一次导入自检。pythonw 启动失败是【静默】的——双击后
rem "什么都没发生"是最难查的那种故障，所以起之前先测一发，
rem 有问题就让 python 把 traceback 打到这个窗口里。
"%PY%" -c "import EH_gui" >nul 2>&1
if errorlevel 1 goto :importfail

start "" "%PYW%" "%~dp0EH_gui.py"
exit /b 0

:importfail
echo.
echo 启动失败，下面是原因：
echo.
"%PY%" -c "import EH_gui"
echo.
if not defined SILENT pause
exit /b 1

:nopython
echo.
echo 没有找到可用的 Python 环境（脚本要 requests / lxml；tkinter 是 Python 自带）。
echo.
echo 两种指定办法（任选其一）：
echo   1) 把任意 python.exe 的完整路径配给 PYTHON_EXE 环境变量（永久）
echo     命令: setx PYTHON_EXE "C:\你的\python.exe"
echo     注意: setx 写注册表,新开 cmd 才生效;先用 set 试一次也行
echo   2) 在 conda 的 envs 里建个环境、装好上面这些库（名字随意），脚本会扫到它
echo.
if not defined SILENT pause
exit /b 1
