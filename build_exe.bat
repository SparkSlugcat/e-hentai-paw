@echo off
chcp 936 >nul 2>&1
cd /d "%~dp0"

rem 第一行 chcp 的理由：本文件按 GBK 存，而 cmd 用系统 ANSI 代码页（本机 936）
rem 解析，所以中文 echo 正常。若某天把终端改成 UTF-8，这行是保险。

set "SILENT="
if /i "%~1"=="silent" set "SILENT=1"

echo ============================================================
echo  e-hentai-paw 打包器  ->  dist\EHPaw.exe
echo ============================================================
echo.

rem ==== 1) 找 Python：不猜环境名，扫 envs 并试导入本项目真实依赖 ====
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

if not exist "%PY%" goto :nopython
echo [1/4] Python     : %PY%

rem ==== 2) 找 PyInstaller：环境里有就用；没有就装到本目录 _pyi_env ====
set "PYI_HOME="
"%PY%" -m PyInstaller --version >nul 2>&1
if not errorlevel 1 set "PYI_HOME=%PYDIR%"
if not defined PYI_HOME if exist "%~dp0_pyi_env\PyInstaller" (
    set "PYI_HOME=%~dp0_pyi_env"
    set "PYTHONPATH=%~dp0_pyi_env"
)
if not defined PYI_HOME (
    echo [2/4] 本机没有 PyInstaller，装到 _pyi_env ^(约 40 MB，不进系统盘^)...
    "%PY%" -m pip install --quiet --target "%~dp0_pyi_env" pyinstaller
    if not exist "%~dp0_pyi_env\PyInstaller" goto :nopyi
    set "PYI_HOME=%~dp0_pyi_env"
    set "PYTHONPATH=%~dp0_pyi_env"
)
echo [2/4] PyInstaller : %PYI_HOME%

rem ==== 3) conda 把 tcl86t/tk86t 放在 Library\bin，必须在 PATH 里 ====
rem   漏了这两个，PyInstaller 只在日志里丢一行 WARNING，
rem   产物却是双击完全没反应（DLL load failed while importing _tkinter）
set "PATH=%PYDIR%;%PYDIR%Library\bin;%PYDIR%DLLs;%PATH%"
echo [3/4] PATH       : 已加入 %PYDIR%Library\bin

rem ==== 4) 打包 ====
echo [4/4] 开始打包，约 1-2 分钟...
echo.
"%PY%" -m PyInstaller --noconfirm --clean EHPaw.spec
if errorlevel 1 goto :buildfail
if not exist "dist\EHPaw.exe" goto :buildfail

echo.
echo ------------------------------------------------------------
for %%F in ("dist\EHPaw.exe") do echo  产物: %%~fF
for %%F in ("dist\EHPaw.exe") do echo  体积: %%~zF 字节
echo ------------------------------------------------------------
echo.
echo 接下来三步验证，缺一不可：
echo.
echo   1^) 离线自检，应打出 frozen=True 和 "OK：窗口构建 + 命令拼装全部通过"
echo        dist\EHPaw.exe --selftest
echo.
echo   2^) 自调用分派通不通，应打出 usage 而不是弹窗口
echo        dist\EHPaw.exe --run-scraper --help
echo.
echo   3^) 双击 dist\EHPaw.exe，界面能开、能跑一次 dry-run
echo.
if not defined SILENT pause
exit /b 0

:buildfail
echo.
echo 打包失败 —— 看上面 PyInstaller 的报错。
echo 最常见两条：
echo   * 日志里有 "could not resolve 'tcl86t.dll'"  -^> [3/4] 那步的 PATH 没生效
echo   * 报 PermissionError                          -^> 旧的 EHPaw.exe 还在跑，先关掉
echo.
if not defined SILENT pause
exit /b 1

:nopyi
echo.
echo PyInstaller 装不上（多半是没网）。手动装：
echo   "%PY%" -m pip install --target "%~dp0_pyi_env" pyinstaller
echo.
if not defined SILENT pause
exit /b 1

:nopython
echo.
echo 没有找到可用 Python（本项目要 requests + lxml；tkinter 是 Python 自带）。
echo.
echo 两种指定办法（任选其一）：
echo   1) 把任意 python.exe 的完整路径配给 PYTHON_EXE 环境变量
echo      setx PYTHON_EXE "C:/你的/python.exe"
echo   2) 在 conda 的 envs 里建个环境、装好上面这些库（名字随意），本脚本会扫到
echo.
if not defined SILENT pause
exit /b 1
