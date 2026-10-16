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
rem  自动定位 py39 环境，不依赖 PATH 里的 python（定位顺序见下）。
rem  本文件不含任何绝对路径 / 用户名，换机器不用改。
rem
rem  参数 silent：连"出错要按任意键"都免了。只有
rem  「启动GUI(无窗口).vbs」会传这个 —— 它把本文件跑在一个隐藏的
rem  cmd 里，那里头的 pause 会永远挂着，表现成"双击了但什么都没
rem  发生"，是最难查的那种失败。日常双击本文件不用传参数。
rem
rem  ★ 想双击彻底不闪命令行窗口 → 双击「启动GUI(无窗口).vbs」。
rem ============================================================

set "SILENT="
if /i "%~1"=="silent" set "SILENT=1"

rem ==== 自动定位 Python 环境 ====
rem    1) PYTHON_EXE 环境变量（想手动指定就用它）
rem    2) %USERPROFILE% 下 conda 的 py39（miniconda3 / anaconda3）
rem    3) %LOCALAPPDATA% 下 miniconda3 / anaconda3
rem    4) 当前已激活的 conda 环境 %CONDA_PREFIX%
rem    5) PATH 里第一个 python
set "PY="
if defined PYTHON_EXE if exist "%PYTHON_EXE%" set "PY=%PYTHON_EXE%"
if not defined PY if exist "%USERPROFILE%\miniconda3\envs\py39\python.exe" set "PY=%USERPROFILE%\miniconda3\envs\py39\python.exe"
if not defined PY if exist "%USERPROFILE%\anaconda3\envs\py39\python.exe" set "PY=%USERPROFILE%\anaconda3\envs\py39\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\miniconda3\envs\py39\python.exe" set "PY=%LOCALAPPDATA%\miniconda3\envs\py39\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Continuum\anaconda3\envs\py39\python.exe" set "PY=%LOCALAPPDATA%\Continuum\anaconda3\envs\py39\python.exe"
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
echo 没有找到可用的 Python 环境（tkinter 是 Python 自带，无需额外依赖）。
echo.
echo 两种指定办法（任选其一）：
echo   1) 在命令行先 set PYTHON_EXE=你的\python.exe 再跑本文件
echo   2) 建一个名为 py39 的 conda 环境，脚本会自动找到它
echo.
if not defined SILENT pause
exit /b 1
