# e-hentai-paw

e-hentai 画廊下载器 —— **纯命令行**（CLI），支持**标签搜索**、**先看名单再挑着下**。

拆自 [felinepaw](../felinepaw) 家族的 `sites/e-hentai/`，独立成一个自包含的目录。
`common.py` 是那份公共库的**拷贝**（不是 import），所以两边改动要手动同步。

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
| Python | 3.9+（本机固定用 `%USERPROFILE%\miniconda3\envs\py39`） |
| 第三方库 | `requests`、`lxml` |
| 网络 | **必须走代理**。e-hentai 境内直连不通，脚本默认会自动探本地 Clash 端口（7897 / 7890 / 7891） |

装依赖：

```
%USERPROFILE%\miniconda3\envs\py39\python.exe -m pip install requests lxml
```

---

## 两种用法

### A. 双击 `启动.bat`（菜单式，不用背参数）

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
启动.bat check    只跑网络预检
启动.bat search   直接进标签搜索
启动.bat shell    直接进命令行模式
```

### B. 命令行

```bash
# ① 单画廊下载（粘 URL）
python EH_scraper_v2.py "https://e-hentai.org/g/3817181/3b0370c5a1/"

# ② 标签搜索 + 只看名单（不下载）
python EH_scraper_v2.py --tags "language:chinese$ female:anal" --limit 30 --dry-run

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
| `female:anal` | 普通标签 |
| `-male:anal` | **排除**这个标签 |
| `~anal` | 模糊匹配 |

多个标签用空格分隔，整串用引号包住。

---

## 目录结构

```
e-hentai-paw/
├── EH_scraper_v2.py     主脚本（搜索 / 单画廊 双模式）
├── common.py            共享库（从 felinepaw 拷贝，改动要同步）
├── check.py             网络预检，单独跑一次链路体检
├── 启动.bat             双击启动器（菜单式，GBK 编码）
├── README.md            本文件
├── PROJECT_STATUS.md    项目规格与交接文档（含 tkinter 学习计划）
├── .gitignore
├── eh_manifest.json     运行产物：名单（dry-run 生成）
└── eh_<标签>/           运行产物：下载的图
```

输出目录规则：

- 搜索模式 → `eh_<标签>/`（标签里的 `$ ~` 会被剔掉，空格变下划线）
- 每个画廊一个子目录：`<名单序号>_<画廊标题>/`
- 图名 = **名单里的原始序号**（不是重新编号）。这条很重要：否则 `--pick 2-4`
  和 `--pick 5-6` 会写出同名文件，被断点续传当成"已下载"跳过，**静默漏图**。

---

## 已知问题与设计决定

### 搜索结果翻页是**游标式**，不是 `page=N`

e-hentai 的搜索结果页用 `&next=<gid>` 翻页（gid = 本页最后一个画廊的 id）。

实测 `page=0` / `page=1` / `page=2` / `page=50` 返回的是**完全相同**的一批数据 ——
**静默重复，不报错**。所以如果哪天翻页看起来"卡在第一页"，先怀疑这里。

本脚本已用游标实现，从页面底部的 `<a id="unext">` 或 `var nexturl=` 取下一个游标。

### `--pages` 会提前停止翻页

画廊详情页每页 20 个链接。要下的张数够了就不再翻页 —— 一个 207 页的画廊
下了前 3 张就停，从 11 个请求降到 1 个。

### 代理为什么"不问系统、直接探本地端口"

`--proxy` 留空时，脚本**不读系统代理设置**，而是直接探 7897 / 7890 / 7891。
原因：本机的**环境变量**里可能存着另一个代理端口（能连上、但出不了网），
系统级 auto 检测会优先拿到它，于是只能在真实请求时才失败 —— 等于白跑一次。

显式写 `--proxy off` / `--proxy auto` / `--proxy <URL>` 时一律尊重你的输入。

---

## 与 felinepaw 的关系

| | |
|---|---|
| 源头 | `../felinepaw/sites/e-hentai/EH_scraper_v2.py` |
| 本目录 | 同一套代码的发布副本（独立目录，可整体拷走） |
| 同步 | 改任意一边后，把 `EH_scraper_v2.py` 和 `common.py` 拷到另一边 |
| 家族入口 | felinepaw 的 `felinepaw_tool.py ehentai ...` 也能调（走源头那份） |

**没有图形界面。** 想给它加一层 tkinter 窗口，看 `PROJECT_STATUS.md` 的学习计划。
