# e-hentai-paw

e-hentai 画廊下载器 —— 支持**标签搜索**、**先看名单再挑着下**，提供**命令行（CLI）**和**图形界面（GUI）**两种入口。

---

## 它解决什么问题

**第一诉求：按标签或画廊 URL 批量下载画廊做收藏。**
e-hentai 上一个标签可能搜出几万个画廊；本工具把整批画廊（或单画廊的多张图）按序号拉下来、落到本地文件夹，是最常见的用途。

**第二诉求：先看名单再挑着下。**
一次全下既没必要也容易撞风控，所以这里的流程是**两步**：

1. 先搜，**只看名单**（`--dry-run`），一个字节都不下
2. 从名单里**挑序号**下（`--pick 2-4,7`）

一句话：**你 dry-run 看到的编号，就是 `--pick` 要写的编号。**

---

## 环境要求

| 项 | 说明 |
|---|---|
| Python | **3.9 或更新版本**（3.9 / 3.10 / 3.11 / 3.12 都测过）。版本管理推荐 [Miniconda](https://docs.conda.io/en/latest/miniconda.html) / [pyenv](https://github.com/pyenv/pyenv)，直接装官方安装包也行 |
| 操作系统 | **Windows 10 / 11**（本仓库的 `.bat` 启动器只在 Windows 下有意义）；其他系统理论上可跑（不依赖任何 Windows-only 代码），但未测 |
| 网络 | **必须能访问本地代理**（脚本会自动探本地 Clash 端口 7897 / 7890 / 7891），下文有专节 |

最省事的起步：

```bash
# 装 Miniconda（如已装跳过）
# 然后建一个 Python 3.9 环境
conda create -n eh-paw python=3.9 -y
conda activate eh-paw
python -m pip install requests lxml
```

---

## 🌐 代理端口自定义

> 这一节是**给改了 Clash 端口的用户**的，**90% 的情况你不用看**。

本工具默认连 `http://127.0.0.1:7897`（脚本会自动探本地 Clash 端口 7897 / 7890 / 7891）。
如果你改了 Clash 的端口（或用 SS / V2RayN / NekoBox / 其他本地代理），改下面这个值：

**方法 1：环境变量（推荐，全局生效）**

```bat
:: Windows cmd（永久，重开 cmd 生效）
setx HTTP_PROXY "http://127.0.0.1:你的端口"
setx HTTPS_PROXY "http://127.0.0.1:你的端口"
```

**方法 2：命令行参数（单次生效）**

```bash
python EH_scraper_v2.py --proxy http://127.0.0.1:你的端口
```

**方法 3：不走代理（如果你直连就通）**

```bash
python EH_scraper_v2.py --proxy off
```

## 🆘 启动失败 / 没装好 Python？

如果你**双击 `启动.bat` / `启动GUI.bat` 看到一堆中文报错**，最常见的就是 Python 环境没配好。两步走。

### Step 1：看报错最关键的一行

| 报错样例 | 含义 | 修法 |
|---|---|---|
| `'python' 不是内部或外部命令` | 系统找不到 `python.exe` | 走 §Step 2，配 `PYTHON_EXE` |
| `ModuleNotFoundError: No module named 'requests'` | Python 找到了，但依赖没装 | `pip install requests lxml` |
| `ModuleNotFoundError: No module named 'lxml'` | lxml 没装 | `pip install lxml` |
| `DLL load failed while importing _tkinter` | conda 环境缺 tkinter | `conda install -n 你的环境 tk` |
| 命令行窗口一闪就没了 | self-check 失败后静默退出 | 在 cmd 里手动敲 `启动.bat`，错误会留在窗口里（pause） |

### 如果是 `No module named ...`：依赖没装

完整报错一般长这样，**只看最后一行**就够：

```text
Traceback (most recent call last):
  File "D:\你的路径\e-hentai-paw\EH_scraper_v2.py", line 52, in <module>
    from lxml import etree
ModuleNotFoundError: No module named 'lxml'
```

本工具只需要两个库，一条命令装齐：

```bat
python -m pip install requests lxml
```

| 容易踩的坑 | 现象 | 怎么办 |
|---|---|---|
| 用 `pip install` 而不是 `python -m pip install` | 装完再跑，还是同一个 `No module named` | 电脑上有多个 Python 时，`pip` 可能装到别的上面。**一律用 `python -m pip`** |
| 装到了另一个 Python 上 | `python -c "import sys; print(sys.executable)"` 打印的路径，跟报错里 `File "...\EH_scraper_v2.py"` 不是同一个环境 | 用那个环境自己的解释器执行 `-m pip install` |
| 下载卡住、最后报 `ReadTimeoutError` | pip 一直转圈然后超时 | 换国内镜像：`python -m pip install requests lxml -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| `ImportError: DLL load failed while importing etree` | Python 找到了，但 lxml 的二进制跟它的版本/位数不匹配 | `python -m pip install --force-reinstall lxml`；还不行就 `conda install -n 你的环境 lxml` |
| `'pip' 不是内部或外部命令` | cmd 里根本找不到 pip | 用 `python -m pip`，绕开 PATH |

**装完验证**（打印 `ok` 才算装对）：

```bat
python -c "import requests, lxml; print('ok')"
```

> 💡 **GUI 窗口能正常打开，但一点「▶ 开始」日志框里就冒出 traceback** —— 这就是缺依赖的典型样子
> （GUI 启动时只需要 `tkinter`，真正干活的是它拉起来的子进程）。按上面把两个库装上即可。
>
> 💡 **菜单式 `e-hentai启动.bat` 走的是命令行**，所以缺依赖会在 cmd 窗口里直接打 traceback，
> 不会一闪而过（脚本带 `pause`）。

### Step 2：让脚本知道你的 Python 在哪

如果你**已经有了**一个 Python / conda 环境（环境名不叫 py39 也行，`myenv` / `ai` / `work` 任意都行），
**不需要改名**——把它的 `python.exe` 完整路径告诉脚本就行。

**永久**（推荐，写到注册表，全局生效）—— 打开任意 cmd，复制粘贴下面这一行（把路径换成你自己的）：

```bat
:: 1. 先找你的 python.exe 在哪
where python
:: 输出类似: C:\Users\你的用户名\miniconda3\envs\myenv\python.exe

:: 2. 把上面那行复制，改造成下面这条，粘到 cmd 里执行
setx PYTHON_EXE "C:\Users\你的用户名\miniconda3\envs\myenv\python.exe"
```

`setx` 写注册表，**执行后必须重新打开一个 cmd 才生效**。然后再双击 `启动.bat` 即可。

**临时**（仅当前 cmd）：

```bat
set PYTHON_EXE=C:\Users\你的用户名\miniconda3\envs\myenv\python.exe
启动.bat
```

### 实在找不到 Python 在哪？

打开任意 cmd，敲：

```bat
where python
```

输出的**第一行**就是 `python.exe` 的完整路径。把它配到 `PYTHON_EXE` 即可。
如果 `where python` 一行都没输出，说明你**根本没装 Python**——装一个就行：
- 官方：https://www.python.org/downloads/（**勾** "Add Python to PATH"）
- 或 Miniconda：https://docs.conda.io/en/latest/miniconda.html

---

## 运行依赖

| 项 | 说明 |
|---|---|
| 第三方库 | `requests`、`lxml` |
| 代理 | **必须走代理**。e-hentai 境内直连不通，脚本默认会自动探本地 Clash 端口（7897 / 7890 / 7891） |

装依赖：

```
python -m pip install requests lxml
```

---

## 三种用法

### A. 双击 `e-hentai启动.bat`（菜单式，不用背参数）

双击后会开一个命令行窗口，菜单就在里面：

```
    [1]  标签搜索 。。。 先看名单，不下载（dry-run）
    [2]  挑着下 。。。。。。 从名单里按序号下（2-4,7）
    [3]  单画廊下载 。。。。 粘一个画廊 URL

    [4]  网络预检 。。。。 Clash / 节点是否就绪
    [5]  打开下载文件夹
    [6]  打开说明文档 。。。 README.md
    [7]  命令行模式 。。。。 python 已就绪

    [0]  退出
```

**这是菜单式 CLI 入口**，双击一定会开命令窗口 —— 那就是本体，别关。（想要图形界面见下方 C 项）

也支持带参数直达，方便做桌面快捷方式：

```
e-hentai启动.bat check    只跑网络预检
e-hentai启动.bat search   直接进标签搜索
e-hentai启动.bat shell    直接进命令行模式
```

### B. 命令行

```bash
# ① 单画廊下载（粘 URL）
python EH_scraper_v2.py "https://e-hentai.org/g/3817181/3b0370c5a1/"

# ② 标签搜索 + 只看名单（不下载）
python EH_scraper_v2.py --tags "language:chinese$ female:feline" --limit 30 --dry-run

# ③ 搜完直接挑着下
python EH_scraper_v2.py --tags "language:chinese$" --limit 30 --pick 2-4,7

# ④ 精确复现：先从名单挑，再下（不受搜索结果变动影响）
python EH_scraper_v2.py --from-manifest eh_manifest.json --pick 2-4,7

# 只想确认代理通不通
python check.py
```

### C. 双击 `启动GUI.bat`（图形界面，不用背参数）

双击直接弹图形窗口（命令行窗口会闪一下，正常）。窗口里选模式（标签搜索 / 单画廊 / 从名单挑），
填参数点「▶ 开始」，运行日志实时刷在下方。

> 依赖同 A/B（Python 3.9+ 与 `requests`、`lxml`）；窗口本身只用到 Python 自带的 tkinter。
> 双击后若没出现窗口，**在 cmd 里手动敲 `启动GUI.bat`** —— 错误会留在窗口里（pause）。

---

## 参数表

| 参数 | 说明 |
|---|---|
| `url` | 画廊 URL，与 `--tags` 二选一 |
| `-t, --tags` | 标签搜索语句（见下） |
| `--limit` | 搜索模式：取前 N 个**画廊**（默认 30，`inf` = 全部，硬上限 1000）<br>单画廊模式：下前 N 张**图**（默认 120） |
| `--pick` | 按名单序号挑着下：`2-4,7` / `3-` / `-3` / `all` |
| `--pages` | 搜索模式专用：每个画廊最多下 N 张图（默认全部） |
| `--dry-run` | 只拉名单不下载，名单写进 `--manifest` 指的文件 |
| `--manifest` | 名单文件名（默认 `eh_manifest.json`） |
| `--from-manifest` | 从这个名单文件读结果，**跳过搜索请求** |
| `-o, --output` | 保存目录 |
| `-w, --workers` | 并发线程数（默认 4，上限 16） |
| `-d, --delay` | 每次请求前的随机延迟上限秒（默认 1.0，风控紧，别调太小） |
| `--cooldown` | 吃到 429/503 时全体线程一起安静的秒数（默认 20） |
| `--force` | 重下已存在的图（默认存在就跳过） |
| `--proxy` | 留空 = 自动探本地 Clash 端口；`off` = 直连；或写 `http://127.0.0.1:7897` |
| `--no-preflight` | 跳过发包前的代理预检 |

### 标签语法

| 写法 | 含义 |
|---|---|
| `language:chinese$` | 精确匹配（`$` = 完全匹配这个标签，不是包含） |
| `female:feline` | 普通标签 |
| `-male:feline` | **排除**这个标签 |
| `~feline` | 模糊匹配 |

多个标签用空格分隔，整串用引号包住。

### `--pick` 序号写法

用**英文逗号**分隔多段，每段可以是一个数或一个范围：

| 写法 | 含义 |
|---|---|
| `2-4,7` | 第 2、3、4、7 个 |
| `3-` | 从第 3 个到最后一个 |
| `-3` | 从第 1 个到第 3 个 |
| `all` | 全部 |

---

## 目录结构

```
e-hentai-paw/
├── EH_scraper_v2.py      主脚本（搜索 / 单画廊 双模式）
├── EH_gui.py             图形界面（tkinter 壳，套在主脚本外面）
├── common.py             共享库
├── check.py              网络预检，单独跑一次链路体检
├── e-hentai启动.bat      双击启动器（菜单式 CLI，GBK 编码）
├── 启动GUI.bat           图形界面启动器（探测 Python + 自检 + 起 GUI）
├── README.md
└── .gitignore
```

运行产物（不随仓库发布）：

- `eh_manifest.json` —— 名单文件，`--dry-run` 生成
- `eh_<标签>/` —— 下载的图

输出目录规则：

- 搜索模式 → `eh_<标签>/`（标签里的 `$ ~` 会被剔掉，空格变下划线）
- 每个画廊一个子目录：`<名单序号>_<画廊标题>/`
- 图名沿用名单里的**原始序号**，方便和 `--pick` 对应、也方便断点续传

---

## ⚠️ 免责声明

- 本工具**仅供个人欣赏、翻译与学习**使用。**禁止任何商业用途或非法盈利**，使用后果由使用者自负。
- e-hentai 是成人向站点，脚本默认就会下载成人内容，请自行判断是否适合使用。
- 请遵守站点自身的 API / 自动化使用条款，**控制请求频率**，避免给站点造成压力。
- 使用风险自负。作者不对下载到的内容、也不对账号安全承担任何责任。

---

## 🔗 相关项目

### 🐾 [felinepaw](https://github.com/SparkSlugcat/felinepaw) — 多站点图片爬虫框架

本项目的上游家族。同一套引擎设计，另有 e621 / FurAffinity / BBooru / WildDream / HypnoHub /
Rule34.us 等站点的下载脚本，以及统一的命令行入口与图形界面。

[![Stars](https://img.shields.io/github/stars/SparkSlugcat/felinepaw?style=for-the-badge&color=yellow)](https://github.com/SparkSlugcat/felinepaw/stargazers)

- **想要一个入口调所有站点**：用 felinepaw 的 `felinepaw_tool.py`，本仓库的行为与它保持一致

### 🖥 [e621-downloader](https://github.com/SparkSlugcat/e621-downloader) — e621 的图形界面版

e621 专用的 tkinter GUI，**免装 Python**，下载一个 exe 双击就能用；艺术家模式同样支持
「先扫描名单、再勾选下载」的挑着下工作流。

[![Latest release](https://img.shields.io/github/v/release/SparkSlugcat/e621-downloader?label=Download&style=for-the-badge&color=brightgreen)](https://github.com/SparkSlugcat/e621-downloader/releases/latest)
[![Stars](https://img.shields.io/github/stars/SparkSlugcat/e621-downloader?style=for-the-badge&color=yellow)](https://github.com/SparkSlugcat/e621-downloader/stargazers)

- **无需 Python** —— 从 Releases 下载 `E621Downloader.exe` 双击即用
- **标签 / 标签分页 / 艺术家** 等下载模式，中英双语界面，实时日志 + 停止按钮

> 💡 一句话：**只下 e-hentai** → 用本仓库；**只下 e621** → 看 [e621-downloader](https://github.com/SparkSlugcat/e621-downloader)；**要一个入口调所有站** → 看 [felinepaw](https://github.com/SparkSlugcat/felinepaw)。

---
---

# e-hentai-paw (English)

A downloader for e-hentai galleries, with **tag search** and a **browse-the-list-first-then-pick**
workflow. It offers both a **command-line interface (CLI)** and a **graphical interface (GUI)**.

> Part of the **[felinepaw](https://github.com/SparkSlugcat/felinepaw)** family — a multi-site image
> scraper framework covering e621 / e-hentai / FurAffinity / BBooru / WildDream / HypnoHub / Rule34.us.

## What it solves

A single tag search on e-hentai can return tens of thousands of galleries. Downloading all of them is
rarely useful and easy to get rate-limited for. So the workflow is **two steps**:

1. Search and **list only** (`--dry-run`) — not a single byte is downloaded
2. **Pick indices** from that list (`--pick 2-4,7`)

In one line: **the index shown in the dry-run output is the index you pass to `--pick`.**

## Requirements

| Item | Notes |
|---|---|
| Python | 3.9+ |
| Third-party | `requests`, `lxml` |
| Network | **A proxy is required.** e-hentai is not directly reachable from mainland China; the script probes the local Clash ports (7897 / 7890 / 7891) by default |

```
python -m pip install requests lxml
```

## 🆘 `No module named ...` — install the dependencies

The full traceback usually looks like this; **only the last line matters**:

```text
Traceback (most recent call last):
  File "D:\path\to\e-hentai-paw\EH_scraper_v2.py", line 52, in <module>
    from lxml import etree
ModuleNotFoundError: No module named 'lxml'
```

This tool needs exactly two libraries:

```bat
python -m pip install requests lxml
```

| Pitfall | Symptom | Fix |
|---|---|---|
| Running `pip install` instead of `python -m pip install` | The same `No module named` after "installing" | With several Pythons installed, bare `pip` may install into a different one. **Always use `python -m pip`** |
| Installed into the wrong interpreter | `python -c "import sys; print(sys.executable)"` prints a path outside the environment shown in the traceback | Run `-m pip install` with that environment's own interpreter |
| Downloads hang, then `ReadTimeoutError` | pip spins forever and times out | Use a mirror: `python -m pip install requests lxml -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| `ImportError: DLL load failed while importing etree` | lxml's binary doesn't match your Python version / architecture | `python -m pip install --force-reinstall lxml`, or `conda install -n YOUR_ENV lxml` |
| `'pip' is not recognized` | pip isn't on PATH | Use `python -m pip` |

Verify (it has to print `ok`):

```bat
python -c "import requests, lxml; print('ok')"
```

> 💡 **The GUI opens fine, but a traceback shows up in the log the moment you hit "Start"** — that's the
> classic missing-dependency symptom (the GUI itself only needs `tkinter`; the real download runs in the
> child process it spawns).
>
> 💡 The menu-driven `e-hentai启动.bat` runs in a real console, so missing deps print the traceback right
> there instead of vanishing (the script has `pause` on failure).

## Three ways to run

### A. Double-click `e-hentai启动.bat` (menu-driven, no flags to memorize)

A console window opens with the menu inside:

```
    [1]  Tag search ........ list only, no download (dry-run)
    [2]  Pick & download ... download by index from the list (2-4,7)
    [3]  Single gallery .... paste a gallery URL

    [4]  Network check ..... is Clash / the node ready?
    [5]  Open download folder
    [6]  Open documentation  README.md
    [7]  Command-line mode .. Python is already set up

    [0]  Exit
```

**This is the menu-driven CLI entry**, so double-clicking always opens a console window — that window
*is* the program, don't close it. (For a GUI, see item C below.)

Arguments are also accepted for direct entry, handy for desktop shortcuts:

```
e-hentai启动.bat check    network pre-check only
e-hentai启动.bat search   go straight to tag search
e-hentai启动.bat shell    go straight to command-line mode
```

### B. Command line

```bash
# (1) Single gallery (paste a URL)
python EH_scraper_v2.py "https://e-hentai.org/g/3817181/3b0370c5a1/"

# (2) Tag search, listing only (no download)
python EH_scraper_v2.py --tags "language:chinese$ female:feline" --limit 30 --dry-run

# (3) Search and download selected entries right away
python EH_scraper_v2.py --tags "language:chinese$" --limit 30 --pick 2-4,7

# (4) Reproduce exactly: pick from a saved list, no search request
python EH_scraper_v2.py --from-manifest eh_manifest.json --pick 2-4,7

# Just check whether the proxy works
python check.py
```

### C. Double-click `启动GUI.bat` (graphical interface, no flags to memorize)

Double-clicking opens a graphical window (a console window flashes briefly — that's normal). Pick a mode (tag search /
single gallery / from manifest), fill in the fields and click "▶ 开始"; the run log streams in below.

> Same requirements as A/B (Python 3.9+ with `requests` and `lxml`); the window itself only needs
> tkinter, which ships with Python. If no window appears, double-click `启动GUI.bat` instead — it
> prints the error to a console window first.

## Options

| Option | Description |
|---|---|
| `url` | Gallery URL; mutually exclusive with `--tags` |
| `-t, --tags` | Tag search expression (see below) |
| `--limit` | Search mode: take the first N **galleries** (default 30, `inf` = all, hard cap 1000)<br>Single-gallery mode: download the first N **images** (default 120) |
| `--pick` | Pick by list index: `2-4,7` / `3-` / `-3` / `all` |
| `--pages` | Search mode only: at most N images per gallery (default all) |
| `--dry-run` | Fetch the list only; write it to the file given by `--manifest` |
| `--manifest` | Manifest filename (default `eh_manifest.json`) |
| `--from-manifest` | Read results from this manifest file, **skipping the search request** |
| `-o, --output` | Output directory |
| `-w, --workers` | Concurrent threads (default 4, max 16) |
| `-d, --delay` | Max random delay before each request, in seconds (default 1.0 — rate limits are tight, don't go lower) |
| `--cooldown` | Seconds all threads stay quiet after a 429/503 (default 20) |
| `--force` | Re-download images that already exist (default: skip) |
| `--proxy` | Empty = auto-probe local Clash port; `off` = direct; or `http://127.0.0.1:7897` |
| `--no-preflight` | Skip the proxy pre-check before requests |

### Tag syntax

| Form | Meaning |
|---|---|
| `language:chinese$` | Exact match (`$` = match the tag exactly, not as a substring) |
| `female:feline` | Plain tag |
| `-male:feline` | **Exclude** this tag |
| `~feline` | Fuzzy match |

Separate multiple tags with spaces and quote the whole string.

### `--pick` index forms

Separate segments with **English commas**; each segment is a number or a range:

| Form | Meaning |
|---|---|
| `2-4,7` | The 2nd, 3rd, 4th and 7th entries |
| `3-` | From the 3rd entry to the last |
| `-3` | From the 1st entry to the 3rd |
| `all` | Everything |

## Layout

```
e-hentai-paw/
├── EH_scraper_v2.py      main script (search / single-gallery, dual mode)
├── EH_gui.py             graphical interface (tkinter shell over the main script)
├── common.py             shared library
├── check.py              network pre-check; run once to test the whole chain
├── e-hentai启动.bat      double-click launcher (menu-driven CLI, GBK encoded)
├── 启动GUI.bat           GUI launcher (probes Python + self-check + launches the GUI)
├── README.md
└── .gitignore
```

Runtime artifacts (not shipped with the repository):

- `eh_manifest.json` — the list file, produced by `--dry-run`
- `eh_<tags>/` — the downloaded images

Output directory rules:

- Search mode → `eh_<tags>/` (the `$ ~` symbols are stripped, spaces become underscores)
- One subdirectory per gallery: `<list index>_<gallery title>/`
- Image names keep their **original list index**, which lines up with `--pick` and with resume

## ⚠️ Disclaimers

- This tool is intended **only for personal appreciation, translation and learning**.
  **Commercial use or illegal profit-making is strictly prohibited.** You bear all responsibility.
- e-hentai is an adult-oriented site, and the script downloads adult content by default — use your own judgment.
- Please comply with the site's own API / automation guidelines and **keep request rates low** so you
  don't put pressure on the site.
- Use at your own risk. The author is not liable for downloaded content or account safety.

## 🔗 Related

### 🐾 [felinepaw](https://github.com/SparkSlugcat/felinepaw) — a multi-site image scraper framework

The upstream family this project belongs to. Built on the same engine design, it also ships downloaders
for e621 / FurAffinity / BBooru / WildDream / HypnoHub / Rule34.us, plus a unified CLI entry point and a GUI.

[![Stars](https://img.shields.io/github/stars/SparkSlugcat/felinepaw?style=for-the-badge&color=yellow)](https://github.com/SparkSlugcat/felinepaw/stargazers)

- **Want one entry point for every site**: use felinepaw's `felinepaw_tool.py`; this repository behaves identically

### 🖥 [e621-downloader](https://github.com/SparkSlugcat/e621-downloader) — the GUI edition for e621

A tkinter GUI dedicated to e621, **no Python required** — download one exe and double-click it.
Artist mode supports the same scan-the-list-then-tick workflow.

[![Latest release](https://img.shields.io/github/v/release/SparkSlugcat/e621-downloader?label=Download&style=for-the-badge&color=brightgreen)](https://github.com/SparkSlugcat/e621-downloader/releases/latest)
[![Stars](https://img.shields.io/github/stars/SparkSlugcat/e621-downloader?style=for-the-badge&color=yellow)](https://github.com/SparkSlugcat/e621-downloader/stargazers)

- **No Python required** — grab `E621Downloader.exe` from Releases and double-click it
- **Tag / Tag-page / Artist** download modes, bilingual (中文 / English) UI, live log + Stop button

> 💡 In one line: **only e-hentai** → use this repository; **only e621** → see [e621-downloader](https://github.com/SparkSlugcat/e621-downloader); **one entry point for every site** → see [felinepaw](https://github.com/SparkSlugcat/felinepaw).
