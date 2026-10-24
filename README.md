# e-hentai-paw

![e-hentai-paw — e-hentai gallery downloader](assets/social-preview.png)

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
| 网络 | **视所在网络而定**：境外通常直连即通，中国大陆需要代理。任何 **HTTP** 代理都行，下文有专节 |

最省事的起步：

```bash
# 装 Miniconda（如已装跳过）
# 然后建一个 Python 3.9 环境
conda create -n eh-paw python=3.9 -y
conda activate eh-paw
python -m pip install requests lxml
```

---

## 🌐 代理

**先问一句：你到底需不需要代理？**

| 你的网络 | 怎么办 |
|---|---|
| 境外 | 基本**直连就通**。`--proxy` 留空即可，想明确点就加 `--proxy off` |
| 中国大陆 | e-hentai 直连不通，**需要代理**。任何 **HTTP** 代理都行 |

> **`--proxy` 留空时怎么决定？分两级。**
> ① 先依次试本机常见混合端口 `7897` / `7890` / `7891` —— 只要有一个在监听就直接用它
> （这是 Clash / Clash Verge / mihomo 的出厂端口，所以软件开着就什么都不用填）；
> ② 三个都没开，再读 `HTTP_PROXY` / `HTTPS_PROXY` 和 Windows 系统代理设置；仍然没有就直连。
>
> 这么做是有原因的：e-hentai 境内直连必然失败，与其拿一个"能连上但出不了网"的系统代理
> 白跑一次，不如先把最常见的几个端口试一遍。

**用的不是 Clash 也完全可以。** 只要能提供一个 **HTTP 端口**就行：Clash / mihomo、
v2rayN、NekoBox、Surge、Proxifier、公司网关都一样。到那个软件的设置里找到端口填进来：

```bat
:: 方法 1：环境变量（永久，重开 cmd 生效）
setx HTTP_PROXY "http://127.0.0.1:你的端口"
setx HTTPS_PROXY "http://127.0.0.1:你的端口"
```

```bash
# 方法 2：命令行参数（单次生效）
python EH_scraper_v2.py --proxy http://127.0.0.1:你的端口

# 方法 3：完全不用代理（境外网络）
python EH_scraper_v2.py --proxy off
```

> ⚠️ **默认不支持 SOCKS。** 填 `socks5://` 会报 `Missing dependencies for SOCKS support`
> —— `requests` 认 SOCKS 需要额外的包。两个解法：
> **① 用客户端的「HTTP / 混合端口」（推荐）**；② `pip install "requests[socks]"`，
> 装完同一个 `socks5://` 地址就能用。

## 🆘 出问题了？

这一节故意留短。完整的排查手册在 **[`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)** ——
启动失败、依赖缺失、`PYTHON_EXE` 配置、代理报错、里站空白页、限速，以及怎么报一个有用的 bug。

| 现象 | 去哪查 |
|---|---|
| `'python' 不是内部或外部命令`、`pythonw.exe not found` | TROUBLESHOOTING §3 —— 配 `PYTHON_EXE` |
| `ModuleNotFoundError: No module named ...` | TROUBLESHOOTING §2 —— `python -m pip install requests lxml` |
| `DLL load failed while importing _tkinter` | TROUBLESHOOTING §1 —— `conda install -n 你的环境 tk` |
| 窗口一闪就没了 | TROUBLESHOOTING §1 —— 先在 cmd 里敲 `启动.bat` |
| 里站空白页 / HTTP 200 | TROUBLESHOOTING §6 —— cookie 权限与过期 |
| `ProxyError` / 全部超时 | TROUBLESHOOTING §5 —— 代理与网络 |

## 运行依赖

| 项 | 说明 |
|---|---|
| 第三方库 | `requests`、`lxml` |
| 代理 | 留空 = 先试本机 `7897` / `7890` / `7891`，再跟随系统代理；境外可填 `off` 直连。任何 **HTTP** 代理都行 |

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

    [4]  网络预检 。。。。 代理 / 节点是否就绪
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
python EH_scraper_v2.py "https://e-hentai.org/g/123456/abcdef1234/"

# ② 标签搜索 + 只看名单（不下载）
python EH_scraper_v2.py --tags "language:chinese$ female:cat" --limit 30 --dry-run

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

## 📦 打包成 exe（可选）

不想碰命令行、也不想装 Python 的话，可以自己打一个单文件 exe：

```bat
:: 方式一：本机常用 —— 钉死 py39、复用现成的 PyInstaller，最快、不用联网
双击  打包-本机.bat

:: 方式二：换台机器打 / 给别人打 —— 自动扫环境，缺 PyInstaller 就装到 _pyi_env
双击  build_exe.bat
```

产物都是 **`dist\EHPaw.exe`**（约 20 MB，单文件，目标机器不需要装 Python）。

**打完必须自己验三条** —— 打包退出码 0 不代表能用：

```bat
dist\EHPaw.exe --selftest              :: 应打出 frozen=True 和 "OK：窗口构建 + 命令拼装全部通过"
dist\EHPaw.exe --run-scraper --help    :: 应打出 usage，而不是弹出窗口
双击 dist\EHPaw.exe                     :: 界面能开，能跑一次 dry-run
```

第二条专门验「自己起自己」。打包后 exe 里**没有** `python.exe`，也没有磁盘上的
`EH_scraper_v2.py`；GUI 起子进程时改走 `EHPaw.exe --run-scraper <参数>`，标志没接上
就会无限套娃地开窗口。

**打包不会带出你的本机路径。** 两个 bat 都先在**中性目录**里构建：

先说实测结论：PyInstaller 6.22 打包时会把模块的源码路径**剥成裸文件名**（`EH_gui.py`），
所以现在静态 `strings` 是搜不出源码目录的。中性目录这一步属于**兜底** —— 换 PyInstaller
版本、或者以后 `datas` 里从项目目录取文件，构建路径就可能真的被带进产物。脚本的做法是：
只把「要打包的 5 个 `.py` + `assets/icon.ico`」
复制到 `<项目所在盘>:\_pawbuild\e-hentai-paw`（既没有用户名、也没有中文目录名），
在那儿 build，再把 exe 拷回来、删掉临时目录。项目所在的盘写不了时退到 `%PUBLIC%\_pawbuild`。

> ⚠️ **不要整个目录 copy**。`.pawout`、`.ehcookie`、`eh_manifest.json`、
> `PROJECT_STATUS.md`（里面有本机绝对路径）都不该靠近构建目录 —— 清单就是上面那 6 个文件。

打完会自动跑一次 `check_privacy.py`，判据分两档：

| 命中类型 | 例子 | 判定 |
|---|---|---|
| **路径形态** | `\你的名字\`、`Users\你的名字`、整个项目目录 | 判**失败**，退出码 1 |
| 裸用户名 | `你的名字` | 只**告警**：三个字母在 36 MB 压缩数据里几乎必然出现几次，是噪声 |

单独跑也行：`python check_privacy.py dist\EHPaw.exe`（可选再给用户名和项目目录）。

**下载目录落在哪**：exe 旁边有 `.pawout`（一行路径）就用它，没有就落到 **exe 旁边的
`downloads\`**。所以「日常版 / 发布版」不需要打两个 exe —— 同一个 exe，旁边放不放
`.pawout` 就是两种身份。

> ⚠️ `.pawout` 是本机私有文件（已在 `.gitignore`），别连 exe 一起发出去。
>
> ⚠️ conda 把 `tcl86t.dll` / `tk86t.dll` 放在 `<env>\Library\bin`，**不在** `<env>\DLLs`。
> 两个 bat 都已经把它加进 `PATH`；如果你是手敲 `python -m PyInstaller`，这一步得自己做。
> 漏了的话 PyInstaller 只在日志里丢一行 `WARNING: could not resolve 'tcl86t.dll'`，
> 产物却是**双击完全没反应**（`DLL load failed while importing _tkinter`）。

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
| `--proxy` | 留空 = 先试 `7897` / `7890` / `7891`，再跟随系统代理；`off` = 直连；或写 `http://127.0.0.1:端口` |
| `--no-preflight` | 跳过发包前的代理预检 |
| `--site` | `e-hentai`（表站，默认）或 `exhentai`（里站，必须带 cookie）。给 URL 时留空会按域名自动判断 |
| `--cookie` | 直接给 cookie 串：`"ipb_member_id=…; ipb_pass_hash=…; igneous=…"` |
| `--cookie-file` | 从文件读 cookie（`.ehcookie` / 浏览器插件导出的 `cookies.txt`）。留空 = 环境变量 `EH_COOKIE` → `.ehcookie` |

### 里站（ExHentai）

里站和表站是**同一套数据库**，gid / token / 图片全部通用，只差一个域名。区别是里站多一道门：
访问时服务器只看 cookie 里的 `igneous`，合法才放行。

```bash
# 1. 把三条 cookie 存进项目根的 .ehcookie（模板见 .ehcookie.example）
cp .ehcookie.example .ehcookie      # 然后填 ipb_member_id / ipb_pass_hash / igneous

# 2. 用里站跑
python EH_scraper_v2.py --site exhentai --tags "language:chinese$" --limit 30 --dry-run

# 3. 或者直接粘里站 URL —— 站点会按域名自动切
python EH_scraper_v2.py "https://exhentai.org/g/1234567/abcdef1234/"
```

⚠️ **两个必须知道的坑**：

- 没权限时里站返回的是**空白页 + HTTP 200**，不是 403。本工具会先探一次首页把原因说清，
  不要拿状态码判断成功。
- cookie 会过期（`igneous` 有效期约一个月），过期后重新登录表站再取一份。

`.ehcookie` 是账号凭证，等同于密码，**已 gitignore，不要提交也不要去外发**。

### 标签语法

| 写法 | 含义 |
|---|---|
| `language:chinese$` | 精确匹配（`$` = 完全匹配这个标签，不是包含） |
| `female:cat` | 普通标签 |
| `-male:cat` | **排除**这个标签 |
| `~cat` | 模糊匹配 |

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
├── check_privacy.py      打包/发布前隐私自检：扫产物里有没有本机路径（两个 bat 会自动调）
├── e-hentai启动.bat      双击启动器（菜单式 CLI，GBK 编码）
├── 启动GUI.bat           图形界面启动器（探测 Python + 自检 + 起 GUI）
├── README.md
├── TROUBLESHOOTING.md    排错手册（启动、依赖、代理、里站、限速）
├── assets/               图标与封面图
├── .ehcookie.example     里站 cookie 模板（复制成 .ehcookie 再填）
└── .gitignore
```

运行产物（不随仓库发布）：

- `eh_manifest.json` —— 名单文件，`--dry-run` 生成
- `eh_<标签>/` —— 下载的图
- `.ehcookie` —— 本机凭证，**已 gitignore**，别提交

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
| Network | **Depends on where you are.** Directly reachable from most of the world; mainland China needs a proxy. Any **HTTP** proxy works — see "Proxy" below |

```
python -m pip install requests lxml
```

## 🌐 Proxy

**First question: do you need one at all?**

| Your network | What to do |
|---|---|
| Outside mainland China | Nothing — e-hentai is directly reachable. Leave `--proxy` empty, or pass `--proxy off` to be explicit |
| Mainland China | A proxy is required. **Any HTTP proxy works** |

> **What does an empty `--proxy` do? Two stages.**
> ① It probes the usual local mixed ports `7897` / `7890` / `7891` in order and uses the
> first one that is listening — those are the factory defaults for Clash / Clash Verge /
> mihomo, so with one of those running you don't need to pass anything;
> ② if none answers, it falls back to `HTTP_PROXY` / `HTTPS_PROXY` and the Windows system
> proxy, and finally to a direct connection.
>
> The reason is practical: a direct connection to e-hentai from mainland China always fails,
> and a system proxy that connects but can't route would waste an entire run.

**Using a client that isn't Clash?** That's fine — anything that exposes an **HTTP** port
works: Clash / mihomo, v2rayN, NekoBox, Surge, Proxifier, a corporate gateway. Find that
port in the client and pass it:

```bat
:: Option 1: environment variables (persistent, takes effect after reopening cmd)
setx HTTP_PROXY "http://127.0.0.1:YOUR_PORT"
setx HTTPS_PROXY "http://127.0.0.1:YOUR_PORT"
```

```bash
# Option 2: command-line flag (one-off)
python EH_scraper_v2.py --proxy http://127.0.0.1:YOUR_PORT

# Option 3: no proxy at all (fine outside mainland China)
python EH_scraper_v2.py --proxy off
```

> ⚠️ **SOCKS is not supported by default.** `socks5://` fails with
> `Missing dependencies for SOCKS support` — `requests` needs an extra package for it.
> Either point at the client's **HTTP / mixed port** (recommended), or install
> `pip install "requests[socks]"` and the same `socks5://` address will work.

## 🆘 Something broke?

Kept short on purpose — the full guide is **[`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)**:
startup failures, missing modules, `PYTHON_EXE`, proxy errors, the blank private-site page,
rate limits, and how to file a bug.

| Symptom | Where to look |
|---|---|
| `'python' is not recognized`, `pythonw.exe not found` | TROUBLESHOOTING §3 — set `PYTHON_EXE` |
| `ModuleNotFoundError: No module named ...` | TROUBLESHOOTING §2 — `python -m pip install requests lxml` |
| `DLL load failed while importing _tkinter` | TROUBLESHOOTING §1 — `conda install -n YOUR_ENV tk` |
| Window flashes and disappears | TROUBLESHOOTING §1 — run `启动.bat` from a cmd window |
| Blank page on the private site | TROUBLESHOOTING §6 — cookie permission and expiry |
| `ProxyError` / everything times out | TROUBLESHOOTING §5 — proxy and network |

## Three ways to run

### A. Double-click `e-hentai启动.bat` (menu-driven, no flags to memorize)

A console window opens with the menu inside:

```
    [1]  Tag search ........ list only, no download (dry-run)
    [2]  Pick & download ... download by index from the list (2-4,7)
    [3]  Single gallery .... paste a gallery URL

    [4]  Network check ..... is the proxy / node ready?
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
python EH_scraper_v2.py "https://e-hentai.org/g/123456/abcdef1234/"

# (2) Tag search, listing only (no download)
python EH_scraper_v2.py --tags "language:chinese$ female:cat" --limit 30 --dry-run

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

## 📦 Building a standalone .exe (optional)

If you want a double-clickable binary that needs no Python at all, build one yourself:

```bat
:: Local, everyday use — pinned to py39, reuses an existing PyInstaller (fast, offline)
double-click  打包-本机.bat

:: Portable — probes for a working environment and installs PyInstaller into _pyi_env if missing
double-click  build_exe.bat
```

Both produce **`dist\EHPaw.exe`** (about 20 MB, single file, the target machine needs no Python).

**Verify three things afterwards** — exit code 0 does not mean the binary works:

```bat
dist\EHPaw.exe --selftest              :: should print frozen=True and the OK line
dist\EHPaw.exe --run-scraper --help    :: should print usage, NOT open a window
double-click dist\EHPaw.exe             :: window opens; run one dry-run
```

The second check covers "the exe launching itself". A frozen exe contains **no** `python.exe`
and no `EH_scraper_v2.py` on disk, so the GUI spawns `EHPaw.exe --run-scraper <args>` instead.
Miss that flag and every start spawns another GUI window.

**The build does not leak your local paths.** Both `.bat` files build inside a **neutral
directory**:

Measured first: PyInstaller 6.22 strips each module's source path down to the bare filename
(`EH_gui.py`), so a static `strings` pass will not reveal the build directory today. The neutral
directory is therefore **belt and braces** — a different PyInstaller release, or a future `datas`
entry read from the project folder, could put the path back in. The scripts copy only the 5 `.py`
files + `assets/icon.ico` into
`<drive>:\_pawbuild\e-hentai-paw` (no username, no non-ASCII directory names), build there,
copy the exe back, then delete the temp tree. If that drive is not writable it falls back to
`%PUBLIC%\_pawbuild`.

> ⚠️ **Never `xcopy` the whole folder.** `.pawout`, `.ehcookie`, `eh_manifest.json` and
> `PROJECT_STATUS.md` (which contains absolute paths) must stay out of the build directory —
> the six files above are the complete list.

After the build it runs `check_privacy.py` automatically, in two tiers:

| Match | Example | Verdict |
|---|---|---|
| **Path shape** | `\yourname\`, `Users\yourname`, the whole project directory | **fails**, exit code 1 |
| Bare username | `yourname` | **warning only** — a three-letter word shows up a few times in 36 MB of compressed data by pure chance |

Runnable on its own: `python check_privacy.py dist\EHPaw.exe` (optionally pass username and
project directory).

**Where downloads land**: a `.pawout` file (one line, a path) next to the exe wins; otherwise
files go to **`downloads\` next to the exe**. That is why there is no need to build two
binaries — the same exe is either your personal setup (`.pawout` present) or a clean release.

> ⚠️ `.pawout` is machine-private (it is in `.gitignore`) — never ship it alongside the exe.
>
> ⚠️ conda keeps `tcl86t.dll` / `tk86t.dll` in `<env>\Library\bin`, **not** in `<env>\DLLs`.
> Both `.bat` files add it to `PATH` for you. If you invoke `python -m PyInstaller` by hand,
> you must do it yourself: skipping this prints only a `WARNING: could not resolve 'tcl86t.dll'`
> line in the log, yet the resulting exe **does nothing on double-click**
> (`DLL load failed while importing _tkinter`).

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
| `--proxy` | Empty = try `7897` / `7890` / `7891` first, then the system proxy; `off` = direct; or `http://127.0.0.1:PORT` |
| `--no-preflight` | Skip the proxy pre-check before requests |
| `--site` | `e-hentai` (public, default) or `exhentai` (private, cookies required). With a URL, blank means the site is inferred from the host |
| `--cookie` | Raw cookie string: `"ipb_member_id=…; ipb_pass_hash=…; igneous=…"` |
| `--cookie-file` | Read cookies from a file (`.ehcookie`, or a browser-exported `cookies.txt`). Blank = env `EH_COOKIE` → `.ehcookie` |

### Private site (ExHentai)

The private site and the public site share **one database**: gids, tokens and images are identical,
only the domain differs. The private site adds a gate — it only looks at the `igneous` cookie and
lets you in when that value is valid.

```bash
# 1. Save the three cookies into .ehcookie in the project root (template: .ehcookie.example)
cp .ehcookie.example .ehcookie      # then fill in ipb_member_id / ipb_pass_hash / igneous

# 2. Run against the private site
python EH_scraper_v2.py --site exhentai --tags "language:chinese$" --limit 30 --dry-run

# 3. Or just paste a private-site URL - the site is inferred from the host
python EH_scraper_v2.py "https://exhentai.org/g/1234567/abcdef1234/"
```

⚠️ **Two things worth knowing**:

- Without access, the private site answers with a **blank page and HTTP 200** — not 403. This tool
  probes the front page once and tells you why; do not treat the status code as success.
- Cookies expire (`igneous` lasts about a month). Re-login on the public site to get a fresh one.

`.ehcookie` is an account credential — as sensitive as a password. It is **gitignored**;
never commit it or send it anywhere.

### Tag syntax

| Form | Meaning |
|---|---|
| `language:chinese$` | Exact match (`$` = match the tag exactly, not as a substring) |
| `female:cat` | Plain tag |
| `-male:cat` | **Exclude** this tag |
| `~cat` | Fuzzy match |

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
├── TROUBLESHOOTING.md    troubleshooting guide (startup, deps, proxy, private site, rate limits)
├── assets/               icon and README banner
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
