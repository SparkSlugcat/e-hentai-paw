# e-hentai-paw

e-hentai 画廊下载器 —— **纯命令行**（CLI），支持**标签搜索**、**先看名单再挑着下**。

> 本项目属于 [felinepaw](https://github.com/SparkSlugcat/felinepaw) 家族 —— 一个覆盖
> e621 / e-hentai / FurAffinity / BBooru / WildDream / HypnoHub / Rule34.us 的多站点图片爬虫框架。

---

## 它解决什么问题

e-hentai 上搜一个标签可能出来几万个画廊，一次全下既没必要也容易撞风控。
所以这里的流程是**两步**：

1. 先搜，**只看名单**（`--dry-run`），一个字节都不下
2. 从名单里**挑序号**下（`--pick 2-4,7`）

一句话：**你 dry-run 看到的编号，就是 `--pick` 要写的编号。**

---

## 依赖

| 项 | 说明 |
|---|---|
| Python | 3.9+ |
| 第三方库 | `requests`、`lxml` |
| 网络 | **必须走代理**。e-hentai 境内直连不通，脚本默认会自动探本地 Clash 端口（7897 / 7890 / 7891） |

装依赖：

```
python -m pip install requests lxml
```

---

## 两种用法

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

**这是个 CLI 工具，没有图形界面**，所以双击一定会开命令窗口 —— 那就是本体，别关。

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
├── common.py             共享库
├── check.py              网络预检，单独跑一次链路体检
├── e-hentai启动.bat      双击启动器（菜单式，GBK 编码）
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

- **只想要图形界面**：e621 用户请看 [e621-downloader](https://github.com/SparkSlugcat/e621-downloader)，免装 Python 的 exe，双击即用
- **想要一个入口调所有站点**：用 felinepaw 的 `felinepaw_tool.py`，本仓库的行为与它保持一致

> 💡 一句话：**只下 e-hentai** → 用本仓库；**同时要下别的站** → 看 [felinepaw](https://github.com/SparkSlugcat/felinepaw)。

---
---

# e-hentai-paw (English)

A **command-line** downloader for e-hentai galleries, with **tag search** and a
**browse-the-list-first-then-pick** workflow.

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

## Two ways to run

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

**This is a CLI tool with no GUI**, so double-clicking always opens a console window — that window
*is* the program, don't close it.

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
├── common.py             shared library
├── check.py              network pre-check; run once to test the whole chain
├── e-hentai启动.bat      double-click launcher (menu-driven, GBK encoded)
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

- **Just want a GUI**: e621 users should look at [e621-downloader](https://github.com/SparkSlugcat/e621-downloader) — a no-Python-required exe, double-click and go
- **Want one entry point for every site**: use felinepaw's `felinepaw_tool.py`; this repository behaves identically

> 💡 In one line: **only e-hentai** → use this repository; **other sites too** → see [felinepaw](https://github.com/SparkSlugcat/felinepaw).
