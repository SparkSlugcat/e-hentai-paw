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
echo [1/5] Python     : %PY%

rem ==== 2) 找 PyInstaller：环境里有就用；没有就装到本目录 _pyi_env ====
set "PYI_HOME="
"%PY%" -m PyInstaller --version >nul 2>&1
if not errorlevel 1 set "PYI_HOME=%PYDIR%"
if not defined PYI_HOME if exist "%~dp0_pyi_env\PyInstaller" (
    set "PYI_HOME=%~dp0_pyi_env"
    set "PYTHONPATH=%~dp0_pyi_env"
)
if not defined PYI_HOME (
    echo [2/5] 本机没有 PyInstaller，装到 _pyi_env ^(约 40 MB，不进系统盘^)...
    "%PY%" -m pip install --quiet --target "%~dp0_pyi_env" pyinstaller
    if not exist "%~dp0_pyi_env\PyInstaller" goto :nopyi
    set "PYI_HOME=%~dp0_pyi_env"
    set "PYTHONPATH=%~dp0_pyi_env"
)
echo [2/5] PyInstaller : %PYI_HOME%

rem ==== 3) conda 把 tcl86t/tk86t 放在 Library\bin，必须在 PATH 里 ====
rem   漏了这两个，PyInstaller 只在日志里丢一行 WARNING，
rem   产物却是双击完全没反应（DLL load failed while importing _tkinter）
set "PATH=%PYDIR%;%PYDIR%Library\bin;%PYDIR%DLLs;%PATH%"
echo [3/5] PATH       : 已加入 %PYDIR%Library\bin

rem ==== 4) 复制到中性路径再打包 —— 这一步是为了隐私，不要删 ====
rem
rem 原理：实测（PyInstaller 6.22）打包时会把这个路径剥成**裸文件名**（EH_gui.py），
rem       所以静态 strings 本来就搜不出源码路径。这一步是**兜底**：换 PyInstaller 版本、
rem       或者以后 datas 里从项目目录取文件，构建路径就可能真的带进去。代价接近零。
rem
rem 做法：只复制"真正要打包的东西"到一个不含个人信息的路径，在那儿 build，
rem       打完把 exe 拷回来，再删掉临时目录。
rem
rem 为什么不用 %TEMP%：它就在 %USERPROFILE%\AppData\Local\Temp 下面，本身就带用户名。
rem 为什么是"本项目所在盘符的根"：项目在 D:\... 就用 D:\_pawbuild，
rem       路径里既没有用户名也没有中文目录名。
rem
rem 注意：**不要整个目录 copy**。.pawout / .ehcookie / eh_manifest.json /
rem       PROJECT_STATUS.md（含本机绝对路径）都不该靠近构建目录。
rem       下面这份清单就是"能进 exe 的全部内容"。

set "NEUTRAL=%~d0\_pawbuild\e-hentai-paw"
set "NEUTRAL_OK="
mkdir "%NEUTRAL%\assets" 2>nul
if exist "%NEUTRAL%\assets" set "NEUTRAL_OK=1"

rem 兜底：项目所在的盘写不了（只读 / 需要管理员）就退到公用目录。
rem %PUBLIC% 那个公用目录不含用户名（只有 Users 这个词），能接受。
if not defined NEUTRAL_OK (
    set "NEUTRAL=%PUBLIC%\_pawbuild\e-hentai-paw"
    mkdir "%NEUTRAL%\assets" 2>nul
    if exist "%NEUTRAL%\assets" set "NEUTRAL_OK=1"
)
if not defined NEUTRAL_OK goto :nobuilddir
echo [4/5] 构建目录   : %NEUTRAL%   ^(中性路径，不含用户名^)

copy /y "%~dp0EH_gui.py"       "%NEUTRAL%\" >nul || goto :copyfail
copy /y "%~dp0EH_scraper_v2.py" "%NEUTRAL%\" >nul || goto :copyfail
copy /y "%~dp0common.py"       "%NEUTRAL%\" >nul || goto :copyfail
copy /y "%~dp0i18n.py"         "%NEUTRAL%\" >nul || goto :copyfail
copy /y "%~dp0EHPaw.spec"      "%NEUTRAL%\" >nul || goto :copyfail
copy /y "%~dp0assets\icon.ico" "%NEUTRAL%\assets\" >nul || goto :copyfail

rem ==== 5) 在中性路径里打包，产物拷回来，然后做隐私自检 ====
echo [5/5] 开始打包，约 1-2 分钟...
echo.
pushd "%NEUTRAL%"
"%PY%" -m PyInstaller --noconfirm --clean EHPaw.spec
set "RC=%errorlevel%"
popd

if not "%RC%"=="0" goto :buildfail
if not exist "%NEUTRAL%\dist\EHPaw.exe" goto :buildfail

if not exist "%~dp0dist" mkdir "%~dp0dist"
copy /y "%NEUTRAL%\dist\EHPaw.exe" "%~dp0dist\EHPaw.exe" >nul || goto :copyfail

rem 自检：exe 里不该出现本机路径。判据在 check_privacy.py 里，分两档：
rem   路径形态（反斜杠夹住用户名、Users+用户名、整个项目目录） -> 判失败，退出码 1
rem   裸用户名                        -> 只告警：三个字母在 36 MB 压缩数据里
rem                                                   压缩数据里几乎必然出现，是噪声
rem %USERNAME% / %~dp0 都是运行时展开的，批处理文件本身不含这两个值。
rem 批处理陷阱："%~dp0" 末尾带反斜杠，直接写成 "%~dp0" 会把结束引号转义掉，
rem 传进 Python 的会变成 D://...//e-hentai-paw" （多个尾引号）。先去掉尾斜杠。
set "PROJ=%~dp0"
if "%PROJ:~-1%"=="\" set "PROJ=%PROJ:~0,-1%"
"%PY%" "%~dp0check_privacy.py" "dist\EHPaw.exe" "%USERNAME%" "%PROJ%"
if errorlevel 1 goto :privacyleak

rem NEUTRAL 是 ...\_pawbuild\e-hentai-paw，删完还会剩一个空的 _pawbuild，
rem 顺手把它也收掉（%NEUTRAL%\.. 只在空的时候才删得掉，不会误删别的东西）。
rmdir /s /q "%NEUTRAL%" 2>nul
for %%I in ("%NEUTRAL%\..") do rmdir /q "%%~fI" 2>nul
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

:privacyleak
echo.
echo !! 隐私自检没过 —— exe 里出现了本机用户名或本项目路径。
echo    上面的 LEAK: [...] 就是命中的字符串。
echo    本脚本已经在中性路径里打包，正常不该出现；出现说明有文件漏了拷贝链路，
echo    或者 spec 里写死了绝对路径。构建目录先留着，方便你查：
echo      %NEUTRAL%
echo.
if not defined SILENT pause
exit /b 1

:copyfail
echo.
echo 复制源码到构建目录失败：%NEUTRAL%
echo 先确认那个目录能写、磁盘没满。
if not defined SILENT pause
exit /b 1

:nobuilddir
echo.
echo 建不出构建目录（试过 %~d0\_pawbuild 和 %PUBLIC%\_pawbuild）。
echo 手动指定一个不含用户名、不含中文的目录再跑，例如：
echo   set PAW_BUILD_DIR=D:\_pawbuild
echo   （本脚本暂不支持该变量，也可以直接改脚本第 4 步的 NEUTRAL）
if not defined SILENT pause
exit /b 1

:buildfail
echo.
echo 打包失败 —— 看上面 PyInstaller 的报错。
echo 最常见三条：
echo   * 日志里有 "could not resolve 'tcl86t.dll'"  -^> [3/5] 那步的 PATH 没生效
echo   * 报 PermissionError                          -^> 旧的 EHPaw.exe 还在跑，先关掉
echo   * 提示 spec 找不到 assets\icon.ico             -^> 图标没拷进构建目录
echo.
echo 构建目录（留着方便排查）：%NEUTRAL%
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
