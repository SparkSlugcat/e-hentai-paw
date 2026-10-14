@echo off
chcp 936 >nul 2>&1
cd /d "%~dp0"

rem 第一行 chcp 的理由：本机系统 ANSI 代码页 = 936，这个文件也按 GBK 存，
rem 所以 cmd 默认就能正确解析下面的中文。万一哪天把终端改成 UTF-8 代码页，
rem cmd 会拿 UTF-8 去解这份 GBK 文件、中文 echo 全变乱码 —— 这行是保险。
rem （改本文件请用能选编码的编辑器存成 GBK；存成 UTF-8 会全乱。）

rem ============================================================
rem  e-hentai-paw 启动器
rem
rem  ★ 这是一个纯 CLI 工具，没有图形界面 —— 所以双击本文件
rem    会开一个命令行窗口，菜单就在里面。别关窗口，那是本体。
rem
rem  python 写死 py39 的绝对路径，不依赖 PATH：本机 PATH 里排第一的
rem  python 是 3.13，没装本项目要的 requests / lxml。
rem
rem  支持带参数直达（方便做桌面快捷方式）：
rem      启动.bat check    只跑网络预检
rem      启动.bat search   直接进标签搜索
rem      启动.bat shell    直接进命令行模式
rem ============================================================

set "PY39=%USERPROFILE%\miniconda3\envs\py39"
set "PY=%PY39%\python.exe"

rem py39 放进 PATH，这样进了命令行模式可以直接敲 python
set "PATH=%PY39%;%PY39%\Scripts;%PATH%"

if not exist "%PY%" goto :nopython

rem 依赖自检。缺库时 python 会直接抛 traceback，不如提前说人话。
"%PY%" -c "import requests, lxml" >nul 2>&1
if errorlevel 1 goto :nodelib

rem ---- 带参数直达 ----
rem 注意：这里必须用括号块。写成 `if cond set X=1 & goto :y` 的话，
rem 那个 goto 是【无条件】执行的（& 只是命令分隔符，不属于 if），
rem 结果就是不管传什么参数都跳到第一个分支。
if /i "%~1"=="check" (
    goto :check
)
if /i "%~1"=="search" (
    goto :search
)
if /i "%~1"=="shell" (
    goto :shell
)

:menu
cls
echo ============================================================
echo    e-hentai-paw   工具箱
echo    目标站 https://e-hentai.org
echo    %~dp0
echo ============================================================
echo.
echo    [1]  标签搜索 。。。 先看名单，不下载（dry-run）
echo    [2]  挑着下 。。。。。。 从名单里按序号下（2-4,7）
echo    [3]  单画廊下载 。。。。 粘一个画廊 URL
echo.
echo    [4]  网络预检 。。。。 Clash / 节点是否就绪
echo    [5]  打开下载文件夹
echo    [6]  打开说明文档 。。。 README.md
echo    [7]  命令行模式 。。。。 python 已就绪
echo.
echo    [0]  退出
echo.
set "ch="
set /p "ch=  输入序号后回车（直接回车 = 1）："
rem set /p 在遇到 EOF 时（被别的脚本调用、输入被重定向）不会改变 ch，
rem 于是 ch 保持"未定义"——这时直接退出。不加这行的话，下面的
rem `if "%ch%"=="" set "ch=1"` 会把它当成"用户直接回车"而进入搜索，
rem 搜索又读到 EOF，回到菜单，无限刷屏。
if not defined ch exit /b 0
if "%ch%"=="" set "ch=1"

if "%ch%"=="1" goto :search
if "%ch%"=="2" goto :picks
if "%ch%"=="3" goto :gallery
if "%ch%"=="4" goto :check
if "%ch%"=="5" goto :opendir
if "%ch%"=="6" goto :opendoc
if "%ch%"=="7" goto :shell
if "%ch%"=="0" exit /b 0
goto :menu


:search
cls
echo ============================================================
echo   标签搜索 —— 只拉名单，不下载
echo ------------------------------------------------------------
echo    标签怎么写（空格分隔多个）：
echo      language:chinese$            只要中文（$ = 精确匹配）
echo      language:chinese$ female:feline
echo      language:chinese$ -male:feline  排除 male:feline 这个标签
echo      ~feline                        模糊匹配
echo ============================================================
echo.
set "tags="
set /p "tags=  标签（直接回车取消）："
if "%tags%"=="" goto :menu
set "limit="
set /p "limit=  最多收几个画廊（直接回车 = 30）："
if "%limit%"=="" set "limit=30"
echo.
echo 正在搜索，请稍候...
echo.
"%PY%" "%~dp0EH_scraper_v2.py" --tags "%tags%" --limit %limit% --dry-run
echo.
pause
goto :menu


:picks
cls
if not exist "%~dp0eh_manifest.json" goto :no_manifest
echo ============================================================
echo   挑着下 —— 从名单里按序号下
echo ------------------------------------------------------------
echo   下面是当前名单。表格里的 # 就是 --pick 要写的数字。
echo ============================================================
echo.
"%PY%" "%~dp0EH_scraper_v2.py" --from-manifest "%~dp0eh_manifest.json" --dry-run
echo.
echo ------------------------------------------------------------
echo   写 2-4,7 只下第 2、3、4、7 个；写 3- 从第 3 个到末尾；
echo   写 all 全下。直接回车 = 取消。
echo ------------------------------------------------------------
set "pick="
set /p "pick=  序号："
if "%pick%"=="" goto :menu
set "pages="
set /p "pages=  每个画廊最多下几张图（直接回车 = 全部）："
set "PAGESARG="
if not "%pages%"=="" set "PAGESARG=--pages %pages%"
echo.
"%PY%" "%~dp0EH_scraper_v2.py" --from-manifest "%~dp0eh_manifest.json" --pick "%pick%" %PAGESARG%
echo.
pause
goto :menu


:gallery
cls
echo ============================================================
echo   单画廊下载 —— 粘一个画廊 URL
echo   例：https://e-hentai.org/g/3817181/3b0370c5a1/
echo ============================================================
echo.
set "url="
set /p "url=  URL（直接回车取消）："
if "%url%"=="" goto :menu
set "glimit="
set /p "glimit=  最多下几张图（直接回车 = 120）："
if "%glimit%"=="" set "glimit=120"
echo.
"%PY%" "%~dp0EH_scraper_v2.py" "%url%" --limit %glimit%
echo.
pause
goto :menu


:check
cls
"%PY%" "%~dp0check.py"
echo.
pause
goto :menu


:opendir
start "" "%~dp0"
goto :menu


:opendoc
if not exist "%~dp0README.md" (
    echo.
    echo 没找到 README.md。
    echo.
    pause
    goto :menu
)
start "" "%~dp0README.md"
goto :menu


:shell
cls
echo ============================================================
echo   命令行模式 —— python 已经在 PATH 里，直接敲 python 即可
echo ------------------------------------------------------------
echo   先试这条看全部参数：
echo     python EH_scraper_v2.py --help
echo.
echo   退出命令行模式：输入 exit 回车
echo ============================================================
echo.
cmd /k
goto :menu


:no_manifest
echo.
echo 还没有名单文件 eh_manifest.json。
echo 请先回到菜单用 [1] 标签搜索 生成一份，再来挑着下。
echo.
pause
goto :menu


:nodelib
echo.
echo 缺少依赖库 requests / lxml。装一下（把这行复制到命令行跑）：
echo.
echo     "%PY%" -m pip install requests lxml
echo.
pause
exit /b 1


:nopython
echo.
echo 没有找到本项目使用的 Python 环境：
echo     %PY%
echo.
echo 如果 conda 环境搬过位置，用记事本改本文件顶部的 PY39 那一行。
echo.
pause
exit /b 1
