# 🆘 排错手册 / Troubleshooting

> **文档范围** —— 本文件收录**装不上、跑不起来、跑到一半报错**的全部排查流程：启动失败、依赖缺失、
> `PYTHON_EXE` 配置、代理报错、里站进不去、限速，以及怎么报一个有用的 bug。
> README 只保留一张速查表，细节都在这里。
>
> **Scope** —— everything that can go wrong **before or during a run**: the launcher refusing to start,
> missing modules, `PYTHON_EXE`, proxy errors, the private site, rate limits, and how to file a bug.
> The README keeps a cheat sheet; every detail lives here.

> **工具声明** —— 本文件的实测数据、复现过程与排版由 AI 编程助手 **WorkBuddy** 协助完成，
> 所有结论均在作者本机复现并人工复核。如有疑义，请以源码与文中的步骤为准。
>
> **Tooling disclosure** —— the measurements, reproductions and formatting here were produced with the
> assistance of the AI coding assistant **WorkBuddy**; every finding was reproduced on the author's
> machine and reviewed manually. Trust the source code and the steps below over this document.

**索引 / Index**

| § | 主题 |
|---|---|
| 1 | 双击没反应 / 窗口一闪就没 |
| 2 | `No module named ...` —— 依赖没装 |
| 3 | 用 `PYTHON_EXE` 指定解释器 |
| 4 | 实在找不到 Python 在哪 |
| 5 | 代理与网络报错 |
| 6 | 里站（ExHentai）进不去 |
| 7 | 报 bug 要带什么 |

---

## 1 双击没反应 / 窗口一闪就没

如果你**双击 `启动.bat` / `启动GUI.bat` 之后看到一堆报错**，最常见的就是 Python 环境没配好。
**先看报错的最后一行** —— 那一行的信息量比上面几十行都大。

| 报错样例 | 含义 | 修法 |
|---|---|---|
| `'python' 不是内部或外部命令` | 系统找不到 `python.exe` | 走 §3，配 `PYTHON_EXE` |
| `ModuleNotFoundError: No module named 'requests'` | Python 找到了，但依赖没装 | 走 §2 |
| `ModuleNotFoundError: No module named 'lxml'` | lxml 没装 | 走 §2 |
| `DLL load failed while importing _tkinter` | conda 环境缺 tkinter | `conda install -n 你的环境 tk` |
| `pythonw.exe not found` | 同「找不到 python」 | 同第一条 |
| 命令行窗口一闪就没了 | 启动器自检失败后静默退出 | 在**已经打开的 cmd** 里手动敲 `启动.bat`，错误会被 `pause` 留住 |
| 窗口开了一下又自己关掉 | 同上（静默路径） | 同上 |

> 💡 `启动GUI.bat` 只自检 `import EH_gui` 这一句。它失败时窗口来不及显示就关了，
> **所以先在 cmd 里敲一次**，错误才会留在屏幕上。

---

## 2 `No module named ...` —— 依赖没装

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
| 装到了另一个 Python 上 | `python -c "import sys; print(sys.executable)"` 打印的路径跟报错里 `File "...\EH_scraper_v2.py"` 不是同一个环境 | 用那个环境自己的解释器执行 `-m pip install` |
| 下载卡住、最后报 `ReadTimeoutError` | pip 一直转圈然后超时 | 换国内镜像：`python -m pip install requests lxml -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| `ImportError: DLL load failed while importing etree` | lxml 的二进制跟 Python 版本/位数不匹配 | `python -m pip install --force-reinstall lxml`；还不行就 `conda install -n 你的环境 lxml` |
| `'pip' 不是内部或外部命令` | cmd 里根本找不到 pip | 用 `python -m pip`，绕开 PATH |

**装完验证**（打印 `ok` 才算装对）：

```bat
python -c "import requests, lxml; print('ok')"
```

> 💡 **GUI 窗口能正常打开，但一点「开始」日志框里就冒出 traceback** —— 这就是缺依赖的典型样子
> （GUI 启动时只需要 `tkinter`，真正干活的是它拉起来的子进程）。
>
> 💡 菜单式的 `e-hentai启动.bat` 跑在真控制台里，缺依赖时 traceback 会直接停在屏幕上，不用找日志。

---

## 3 用 `PYTHON_EXE` 指定解释器

如果你**已经有了**一个 Python / conda 环境（环境名不叫 `py39` 也行，`myenv` / `ai` / `work` 任意都行），
**不需要改名** —— 把它的 `python.exe` 完整路径告诉启动器就行。

**永久**（推荐，写到注册表，全局生效）—— 打开任意 cmd，复制粘贴下面这一行（把路径换成你自己的）：

```bat
:: 1. 先找你的 python.exe 在哪
where python
:: 输出类似: C:\Users\你的用户名\miniconda3\envs\myenv\python.exe

:: 2. 把上面那行复制，改造成下面这条，粘到 cmd 里执行
setx PYTHON_EXE "C:\Users\你的用户名\miniconda3\envs\myenv\python.exe"
```

`setx` 写注册表，**执行后必须重新打开一个 cmd 才生效**。然后再双击 `启动.bat` / `启动GUI.bat` 即可。

**临时**（仅当前 cmd）：

```bat
set PYTHON_EXE=C:\Users\你的用户名\miniconda3\envs\myenv\python.exe
启动.bat
```

---

## 4 实在找不到 Python 在哪

打开任意 cmd，敲：

```bat
where python
```

输出的**第一行**就是 `python.exe` 的完整路径。把它配到 `PYTHON_EXE` 即可。

如果 `where python` 一行都没输出，说明你**根本没装 Python** —— 装一个就行：

- 官方：<https://www.python.org/downloads/>（**勾** "Add Python to PATH"）
- 或 Miniconda：<https://docs.conda.io/en/latest/miniconda.html>

---

## 5 代理与网络报错

e-hentai 在国内**不挂代理连不上**。脚本默认会探测本地 Clash 的三个端口：7897 / 7890 / 7891。

| 报错 | 含义 | 怎么办 |
|---|---|---|
| `proxy_down` | 预检发现那个端口没在监听 | 确认 Clash 开着，或显式给 `--proxy http://127.0.0.1:端口` |
| `bad_proxy_url` | 代理串不是合法 URL | 要带协议头：`http://127.0.0.1:7897` |
| 每个请求都 `ProxyError` | 端口能连但代理没在转发 | 换节点；或加 `--no-preflight` 看原始报错 |
| 全部超时、没有报错 | 一般是节点死了 | 在 Clash 里换节点再试 |
| 表站正常、里站空白 | 见 §6 | 见 §6 |

跑之前在 cmd 里单测一次链路最省事：

```bash
python check.py
```

> 💡 `--no-preflight` 只跳过预检那一次探测，不会改变实际请求怎么走。

---

## 6 里站（ExHentai）进不去

里站和表站是**同一套数据库**，只差一个域名，多一道门：服务器只看 cookie 里的 `igneous`。

| 现象 | 原因 | 怎么办 |
|---|---|---|
| **空白页 + HTTP 200**（不是 403） | cookie 没权限或已过期 | 重新登录表站取一份 cookie；**不要拿状态码判断成功** |
| 程序说「没权限 / 空白页」 | 工具开跑前会探一次首页，提前把原因说清 | 按提示补 cookie，而不是重试 |
| 换了账号还是空白 | `.ehcookie` 里是旧值 | 三件套 `ipb_member_id` / `ipb_pass_hash` / `igneous` 要一起换 |
| 用了 `--cookie` 但没生效 | 优先级记错了 | 顺序是 `--cookie` > `--cookie-file` > 环境变量 `EH_COOKIE` > 项目根的 `.ehcookie` |

`igneous` 有效期约一个月，过期后重新登录表站再取一份。

> ⚠️ `.ehcookie` 是账号凭证，**等同于密码**，已 gitignore —— 不要提交，也不要去外发。
> 本工具会把 cookie 同时挂到 `.exhentai.org` 和 `.e-hentai.org` 两个域上，因为里站和表站会互相跳。

---

## 7 报 bug 要带什么

带上这五项，通常一轮就能定位：

1. **完整命令行**（含所有参数），或者「双击了哪个 bat」
2. **输出最后 10 行**（不要只截第一屏）
3. `python -c "import sys; print(sys.executable)"` 的结果
4. 用的是**表站还是里站**，以及换成 `--proxy off` 有没有变化
5. 你期望什么、实际发生了什么

提 issue：<https://github.com/SparkSlugcat/e-hentai-paw/issues>

---
---

# Troubleshooting (English)

Everything that can go wrong **before or during a run** — the launcher refusing to start, missing
modules, `PYTHON_EXE`, proxy errors, the private site, rate limits — is on this page. The README keeps
a cheat sheet; details live here.

## 1 Nothing happens on double-click

If you double-clicked `启动.bat` / `启动GUI.bat` and got a wall of text, the usual cause is a
misconfigured Python. **Read the last line of the traceback first.**

| Error | Meaning | Fix |
|---|---|---|
| `'python' is not recognized` | `python.exe` not on PATH | §3 — set `PYTHON_EXE` |
| `ModuleNotFoundError: No module named 'requests'` | Python found, dependency missing | §2 |
| `ModuleNotFoundError: No module named 'lxml'` | lxml missing | §2 |
| `DLL load failed while importing _tkinter` | the conda env has no tkinter | `conda install -n YOUR_ENV tk` |
| `pythonw.exe not found` | same as "python not found" | §3 |
| The console window flashes and vanishes | the launcher's self-check failed and it exits silently | open a cmd window first and type `启动.bat` there — the error stays on screen |
| A window opens, then closes itself | same silent path | same fix |

> 💡 The GUI launcher only self-checks `import EH_gui`. When that fails there is no time to read
> anything, which is why running the `.bat` **from an already-open cmd** is the diagnostic step.

## 2 `No module named ...` — install the dependencies

Only the **last line** of the traceback matters:

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
> 💡 The menu-driven `e-hentai启动.bat` runs in a real console, so a missing dependency leaves the
> traceback right on screen — no need to hunt for a log.

## 3 Point the launcher at your Python (`PYTHON_EXE`)

If you already have a Python / conda env (any name works — `myenv` / `ai` / `work`), you don't need to
rename it. Just tell the launcher where its `python.exe` is.

**Permanent (registry, global)** — open any cmd and paste:

```bat
:: 1. Find your python.exe
where python
:: Output is like: C:\Users\YOUR_NAME\miniconda3\envs\myenv\python.exe

:: 2. Adapt that path and paste this
setx PYTHON_EXE "C:\Users\YOUR_NAME\miniconda3\envs\myenv\python.exe"
```

`setx` writes to the registry; **reopen any cmd for it to take effect**, then double-click the `.bat` again.

**Temporary (current cmd only)**:

```bat
set PYTHON_EXE=C:\Users\YOUR_NAME\miniconda3\envs\myenv\python.exe
启动.bat
```

## 4 Can't find Python at all

```bat
where python
```

The **first line** is the full path to `python.exe` — set it as `PYTHON_EXE`. If `where python` prints
nothing, you don't have Python installed:

- Official: <https://www.python.org/downloads/> (check **"Add Python to PATH"**)
- Or Miniconda: <https://docs.conda.io/en/latest/miniconda.html>

## 5 Proxy and network errors

e-hentai is not reachable from mainland China without a proxy. The script probes the usual local Clash
ports by default: 7897 / 7890 / 7891.

| Message | Meaning | Fix |
|---|---|---|
| `proxy_down` | the preflight probe found nothing listening on that port | make sure Clash is running, or pass `--proxy http://127.0.0.1:PORT` |
| `bad_proxy_url` | the proxy string isn't a valid URL | it needs the scheme: `http://127.0.0.1:7897` |
| `ProxyError` on every request | the port answers but nothing is forwarded | switch node, or add `--no-preflight` to see the raw error |
| Everything times out with no error | usually a dead node | switch nodes in Clash and retry |
| Public site fine, private site blank | see §6 | see §6 |

One-shot link check:

```bash
python check.py
```

> 💡 `--no-preflight` only skips that single probe; it does not change how requests are actually sent.

## 6 The private site (ExHentai) won't open

Same database as the public site, one extra gate: the server only looks at the `igneous` cookie.

| Symptom | Cause | Fix |
|---|---|---|
| **Blank page with HTTP 200** (not 403) | cookie lacks permission or has expired | log in to the public site and take a fresh cookie; **never judge success by the status code** |
| The tool reports "blank page / no permission" | it probes the front page before starting, on purpose | supply a fresh cookie instead of retrying |
| Still blank after switching accounts | `.ehcookie` holds stale values | replace all three: `ipb_member_id` / `ipb_pass_hash` / `igneous` |
| `--cookie` seems ignored | wrong priority in mind | order is `--cookie` > `--cookie-file` > env `EH_COOKIE` > `.ehcookie` in the project root |

`igneous` is valid for roughly a month; log in again when it expires.

> ⚠️ `.ehcookie` is an account credential — treat it as a password. It is gitignored: don't commit it,
> don't share it. The tool attaches the cookies to **both** `.exhentai.org` and `.e-hentai.org`, because
> the two sites redirect into each other.

## 7 Filing a bug report

Include these five items and it can usually be diagnosed in one round-trip:

1. **The full command line** (every flag), or which `.bat` you double-clicked
2. **The last 10 lines of output** — not a screenshot of the first screen
3. The output of `python -c "import sys; print(sys.executable)"`
4. Public or private site, and whether `--proxy off` changes anything
5. What you expected vs. what happened

Open an issue at <https://github.com/SparkSlugcat/e-hentai-paw/issues>.
