#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i18n.py — 中英双语词库 + 语言偏好持久化
=========================================

用法：
    import i18n
    i18n.t("key")               # 当前语言的字符串
    i18n.t("key", n=3)          # 支持 {n} 占位符（str.format 语法）
    i18n.set_lang("en")         # 切语言并记住（写 ~/.paw/ehentai.lang）

默认语言从哪来（优先级从高到低）：
    1. 环境变量 PAW_LANG —— GUI 起子进程时塞进去的，保证界面和日志同一个语言
    2. ~/.paw/ehentai.lang —— 用户上次在 GUI 里选的语言
    3. "zh"

词条按用途分段（界面 / 抓取器 / 公共库），新增文案时加在自己那段里。
"""

import os
from pathlib import Path

#: 决定偏好文件路径：~/.paw/<APP_ID>.lang
APP_ID = "ehentai"
#: GUI 传给子进程的语言通道（环境变量）
LANG_ENV = "PAW_LANG"

LANGS = ("zh", "en")
LANG_NAMES = ("中文", "English")


# ============================================================
# 中文词条
# ============================================================

ZH = {
    # ---------- 界面（EH_gui.py） ----------
    "gui_title": "e-hentai-paw 下载器",
    "gui_lang_label": "语言:",
    "gui_params": " 任务参数 ",
    "gui_mode_label": "模式:",
    "gui_mode_tags": "标签搜索",
    "gui_mode_gallery": "单画廊(URL)",
    "gui_mode_manifest": "从名单挑",
    "gui_tags_label": "标签(--tags):",
    "gui_url_label": "画廊URL:",
    "gui_manifest_in_label": "名单文件(--from-manifest):",
    "gui_browse": "浏览...",
    "gui_output_label": "输出目录(--output):",
    "gui_limit_label": "数量(--limit):",
    "gui_pick_label": "挑序号(--pick):",
    "gui_pages_label": "每画廊限张(--pages):",
    "gui_manifest_out_label": "保存名单(--manifest):",
    "gui_workers_label": "线程:",
    "gui_delay_label": "延迟:",
    "gui_cooldown_label": "冷却:",
    "gui_proxy_label": "代理(--proxy):",
    "gui_site_label": "站点:",
    "gui_cookie_file_label": "Cookie文件(--cookie-file):",
    "gui_dry_run": "只列名单(--dry-run)",
    "gui_force": "重新下载(--force)",
    "gui_no_preflight": "跳过预检(--no-preflight)",
    "gui_hint": "提示：代理/输出目录/数量等留空 = 用脚本默认；标签语法如 "
                "language:chinese$ / female:cat / -male:cat（空格分隔多个）；"
                "--limit 搜索模式作用于画廊、单画廊模式作用于图片；"
                "「挑序号」「每画廊限张」「只列名单」主要用于搜索流程；"
                "里站要先把 cookie 存进 .ehcookie（每行一条 k=v）再把站点选成 exhentai，"
                "Cookie文件留空即自动读它",
    "gui_start": "▶ 开始",
    "gui_stop": "■ 停止",
    "gui_status_idle": "空闲",
    "gui_status_running": "运行中...",
    "gui_status_stopping": "正在停止...",
    "gui_status_done": "完成（退出码 {code}）",
    "gui_log_frame": " 运行日志 ",
    "gui_lang_switched": "语言已切换为 {lang}",
    "gui_dlg_output_dir": "选择输出目录",
    "gui_dlg_manifest_file": "选择名单文件",
    "gui_dlg_cookie_file": "选择 cookie 文件",
    "gui_filetype_cookie": "Cookie 文件 (*.txt;*.ehcookie)",
    "gui_filetype_all": "所有文件",
    "gui_err_need_tags": "标签搜索模式需要填写标签(--tags)",
    "gui_err_need_url": "单画廊模式需要填写画廊 URL",
    "gui_err_need_manifest": "从名单模式需要选择名单文件(--from-manifest)",
    "gui_msg_running_title": "提示",
    "gui_msg_running": "任务正在运行中",
    "gui_err_title": "错误",
    "gui_err_args_title": "参数错误",
    "gui_err_scraper_missing": "找不到 {name}，请确认它在同一目录。",
    "gui_proc_exit": "[进程结束，退出码 {code}]",
    "gui_stop_requested": "已请求停止",
    "gui_selftest_search": "搜索模式:",
    "gui_selftest_gallery": "单画廊模式:",
    "gui_selftest_site": "里站模式:",
    "gui_selftest_public": "表站模式(不应带 --site):",
    "gui_selftest_manifest": "从名单模式:",
    "gui_selftest_assert_tags": "标签搜索漏填标签却没有报错",
    "gui_selftest_ok": "OK：窗口构建 + 命令拼装全部通过。",

    # ---------- 抓取器（EH_scraper_v2.py） ----------
    "eh_err_parse_url": "无法从 URL 解析 gid/token: {url}",
    "eh_proxy_auto": "自动选中本地代理 {url}（--proxy 可覆盖）",
    "eh_search_page": "  搜索第 {page} 页: 解析 {got} 条（新增 {fresh}，累计 {total}{cap}）",
    "eh_gallery_links_page": "  画廊第 {page} 页: {n} 个链接（累计 {total}）",
    "eh_gallery_links_enough": "  已够 {n} 张，停止翻页",
    "eh_manifest_write_failed": "名单写入失败：{err}",
    "eh_manifest_not_found": "找不到名单文件：{path}",
    "eh_manifest_unreadable": "名单文件读不了（{kind}）：{err}",
    "eh_results_title": "\n===== 搜索结果{summary} =====",
    "eh_results_summary": "（共 {total} 个{note}）",
    "eh_col_pages": "页数",
    "eh_col_category": "分类",
    "eh_col_title": "标题",
    "eh_results_footer": "  （共 {n} 个。用 --pick 2-4,7 挑着下，编号就是上面的 #）",
    "eh_image_list_title": "\n===== 图片名单（共 {n} 张）=====",
    "eh_desc": "e-hentai 画廊下载器 v3（单画廊 / 标签搜索 / dry-run / 挑着下）",
    "eh_epilog_examples": "示例:",
    "eh_epilog_note": "--limit / --pick 作用于「当次名单」:\n"
                      "  搜索模式 = 搜出来的画廊;  单画廊模式 = 画廊里的图片\n",
    "eh_help_url": "画廊 URL，例如 https://e-hentai.org/g/3817181/3b0370c5a1/",
    "eh_help_tags": "标签搜索（与 URL 二选一）。语法: language:chinese$ / female:cat / "
                    "-male:cat / ~cat，空格分隔多个",
    "eh_help_output": "保存目录。留空 = 读项目根 .pawout（无则当前目录）; "
                      "搜索模式作为根目录，单画廊作为该画廊目录",
    "eh_help_limit": "搜索模式: 取前 N 个画廊（默认 {n}，inf=全部）; "
                     "单画廊模式: 下前 N 张图（默认 120）",
    "eh_help_pick": "按名单序号挑着下，如 2-4,7 / 3- / all（编号 = dry-run 看到的 #）",
    "eh_help_pages": "搜索模式专用: 每个画廊最多下 N 张图（默认 inf=全部）",
    "eh_help_dry_run": "只拉名单不下载（同时把名单写进 --manifest 指的文件）",
    "eh_help_manifest": "--dry-run 保存名单的文件名（默认 eh_manifest.json）",
    "eh_help_from_manifest": "从这个名单文件读结果，跳过搜索请求（配合 --pick 精确复现）",
    "eh_help_workers": "并发线程数（默认4）",
    "eh_help_delay": "每次请求前的随机延迟上限秒（默认1.0）。e-hentai 风控较紧，别调太小",
    "eh_help_cooldown": "吃到 429/503 时全体线程一起安静的秒数，默认 20",
    "eh_help_force": "重新下载已存在的图（默认：存在就跳过）",
    "eh_help_proxy": "代理: 留空=自动检测, off=直连, 或 http://127.0.0.1:7897",
    "eh_help_no_preflight": "跳过发包前的代理预检",
    "eh_err_fetch_gallery_indent": "  获取画廊页面失败：{err}",
    "eh_err_fetch_gallery": "获取画廊页面失败: {err}",
    "eh_err_no_links_indent": "  未找到任何图片链接（画廊可能已被删除或需要登录）。",
    "eh_err_no_links": "未找到任何图片链接（画廊可能已被删除或需要登录）。",
    "eh_pages_limited": "  --pages {pages}：本画廊只取下前 {n} 张",
    "eh_output_dir_indent": "  输出目录: {path}",
    "eh_output_dir": "输出目录: {path}",
    "eh_err_pages_invalid": "--pages 需要是正整数或 inf。",
    "eh_skip_exists": "  [{idx}] 已存在，跳过",
    "eh_err_no_img_src": "详情页未找到图片 src",
    "eh_err_empty_file": "下载文件为空",
    "eh_done_progress": "  #{idx} 完成 -> {name}（进度 {done}/{total}）",
    "eh_job_failed": "  [{idx}] 失败: {err}",
    "eh_need_url_or_tags": "请给出画廊 URL 或 --tags 标签（二选一）。",
    "eh_example_url": '  例：python EH_scraper_v2.py "https://e-hentai.org/g/xxx/yyy/"',
    "eh_example_tags": '  例：python EH_scraper_v2.py --tags "language:chinese$" '
                       "--limit 30 --dry-run",
    "eh_example_manifest": "  例：python EH_scraper_v2.py --from-manifest "
                           "eh_manifest.json --pick 2-4,7",
    "eh_proxy_enabled": "已启用代理: {proxy}",
    "eh_proxy_direct": "未使用代理（直连）—— e-hentai 境内通常直连不通，不通就加 "
                       "--proxy http://127.0.0.1:7897",
    "eh_manifest_no_images": "名单里没有图片。",
    "eh_manifest_read_images": "从名单读回 {n} 张图：{title}",
    "eh_pick_images": "--pick 挑出 {n} 张（文件名用原始序号）",
    "eh_download_done": "\n===== 下载完成 =====",
    "eh_summary_counts": "成功: {ok} | 跳过: {skip} | 失败: {fail}",
    "eh_saved_to": "文件保存至: {path}",
    "eh_manifest_read_galleries": "从名单读回 {n} 个画廊（原搜索: {query}）",
    "eh_query_unrecorded": "(未记录)",
    "eh_manifest_no_galleries": "名单里没有画廊。",
    "eh_limit_capped": "--limit 太大，搜到 {n} 个就够了（硬上限 {cap}）。",
    "eh_search_start": "\n搜索: {query}",
    "eh_search_target": "目标: 收前 {n} 个画廊",
    "eh_search_failed": "搜索请求失败：{err}",
    "eh_search_empty": "没搜到任何画廊。检查一下标签写法（如 language:chinese$）。",
    "eh_manifest_saved": "\n名单已保存: {path}",
    "eh_manifest_next_hint": "下次可用: python {prog} --from-manifest {manifest} --pick 2-4,7",
    "eh_pick_galleries": "\n--pick 挑出 {n} 个画廊: {idx}",
    "eh_output_root": "\n输出根目录: {path}",
    "eh_all_done": "\n===== 全部完成 =====",
    "eh_galleries_selected": "画廊: 选中 {n} 个",
    "eh_images_summary": "图片: 成功 {ok} | 跳过 {skip} | 失败 {fail}",
    "eh_saved_root": "保存至: {path}",
    "eh_gallery_meta": "画廊标题: {title} | 文件数: {count} | 分类: {category}",
    "eh_gallery_tags": "标签: {tags}",
    "eh_gallery_meta_missing": "gdata API 未返回信息，回退用 URL 命名目录。",
    "eh_fetching_links": "正在翻页抓取图片详情页链接...",
    "eh_pick_images_in_limit": "--pick 挑出 {n} 张（在名单前 {limit} 张里挑；"
                               "文件名用原始序号 {idx}）",
    "eh_download_plan": "共 {n} 张图片（下载上限 {limit}），{workers} 线程，"
                        "随机延迟 0~{delay}s",
    "eh_gallery_summary": "画廊: {title} (gid={gid})",

    # ---------- 里站 / cookie（ExHentai） ----------
    "eh_help_site": "目标站点: e-hentai=表站(默认,游客可看) | exhentai=里站(必须有 cookie)。"
                    "给单画廊 URL 时留空会自动按 URL 域名判断",
    "eh_help_cookie": "直接给 cookie 串，如 \"ipb_member_id=...; ipb_pass_hash=...; igneous=...\"",
    "eh_help_cookie_file": "从文件读 cookie（浏览器插件导出的 cookies.txt 或每行一条 k=v）。"
                           "留空 = 环境变量 EH_COOKIE > 当前目录/.ehcookie > 脚本目录/.ehcookie",
    "eh_site_selected": "目标站点: {site}",
    "eh_site_from_url": "URL 指向 {site}，已自动切到这个站",
    "eh_cookie_loaded": "已载入 {n} 条 cookie（来源: {source}）",
    "eh_cookie_none": "未提供 cookie（游客身份，只能看到表站公开内容）",
    "eh_cookie_file_bad": "cookie 文件读不出来: {path}",
    "eh_cookie_empty": "cookie 解析出来是空的，检查一下格式：要 `名字=值`，用 `;` 或换行分隔",
    "eh_cookie_igneous": "  igneous = {value}（里站通行证）",
    "eh_ex_need_cookie": "里站必须带 cookie 才能进 —— 现在一条都没有，先去拿。",
    "eh_ex_hint": "怎么拿：浏览器登录表站 → 打开 exhentai.org（能进说明账号有权限）→ F12 → "
                  "Application → Cookies → 把 ipb_member_id / ipb_pass_hash / igneous 三条"
                  "存进项目根的 .ehcookie（每行一条 k=v），再用 --site exhentai",
    "eh_ex_no_rights": "进不去里站：igneous = {value}，说明账号还没有里站权限"
                       "（或 igneous 已过期）。合法的是一串 17 位字符。",
    "eh_ex_blocked": "进不去里站：igneous = {value}… 看起来是合法值，但首页仍然是空白 —— "
                     "大概率是出口 IP 被拦（共享节点常见），或者 cookie 少了 ipb_member_id / ipb_pass_hash。",
    "eh_ex_probe_failed": "里站探测请求失败（网络/代理层面）: {err}",
    "eh_ex_blank_hint": "  说明：这个「空白页」是 HTTP 200 的，不是报错 —— 里站就是用空白页拒绝访问的。",
    "eh_blank_page_warn": "  拿到的是空白页（HTTP 200）—— cookie 可能在运行中失效了，"
                          "重新登录表站换一份 igneous 再跑。",
    "eh_blank_page_warn_public": "  拿到的是空页面（HTTP 200）—— 表站不需要 cookie，"
                                 "这更像是代理节点抽风，换个节点重试。",

    # ---------- 公共库（common.py） ----------
    # ⚠️ 这一段必须与 felinepaw/i18n.py 的同名段保持一致：两边的 common.py 是逐字节拷贝。
    "common_limit_invalid": "--limit 需要是正整数或 inf。",
    "common_pick_empty": "--pick 是空的。写成 2-4,7 这样的序号（或 all）。",
    "common_pick_none_left": "--pick 挑完之后一个都不剩。",
    "common_help_delay": "每次请求前的基准延时秒数，默认 0（不限速）。被站点限流时试试 --delay 1.0",
    "common_help_jitter": "在基准延时上叠加的随机抖动秒数，默认 0。配合 --delay 用（如 --delay 1 --jitter 1.5）让节奏不像机器",
    "common_help_cooldown": "吃到 429/503 时让所有线程一起安静多少秒，默认 20",
    "common_help_no_preflight": "跳过发包前的代理预检（默认会先花约 1 秒确认链路，失败时能立刻说清是 Clash 没开还是节点问题）",
    "common_pick_dash": "--pick 里的 '-' 两边至少要有一个数字：{part!r}",
    "common_pick_reversed": "--pick 的区间写反了（{start} > {end}）：{part!r}",
    "common_pick_bad": "--pick 看不懂这一段：{part!r}（支持 2-4,7 / 3- / -3 / all）",
    "common_pick_oob_n": "--pick 里有超出范围的序号已忽略：{n} 个（{first}~{last} 等，当前名单只有 {total} 个）",
    "common_pick_oob_list": "--pick 里有超出范围的序号已忽略：{ids}（当前名单只有 {total} 个）",
}


# ============================================================
# 英文词条（key 必须与 ZH 一一对应）
# ============================================================

EN = {
    # ---------- 界面 ----------
    "gui_title": "e-hentai-paw Downloader",
    "gui_lang_label": "Language:",
    "gui_params": " Task Parameters ",
    "gui_mode_label": "Mode:",
    "gui_mode_tags": "Tag Search",
    "gui_mode_gallery": "Single Gallery (URL)",
    "gui_mode_manifest": "Pick from Manifest",
    "gui_tags_label": "Tags (--tags):",
    "gui_url_label": "Gallery URL:",
    "gui_manifest_in_label": "Manifest (--from-manifest):",
    "gui_browse": "Browse...",
    "gui_output_label": "Output dir (--output):",
    "gui_limit_label": "Limit (--limit):",
    "gui_pick_label": "Pick (--pick):",
    "gui_pages_label": "Pages per gallery (--pages):",
    "gui_manifest_out_label": "Save manifest (--manifest):",
    "gui_workers_label": "Workers:",
    "gui_delay_label": "Delay:",
    "gui_cooldown_label": "Cooldown:",
    "gui_proxy_label": "Proxy (--proxy):",
    "gui_site_label": "Site:",
    "gui_cookie_file_label": "Cookie file (--cookie-file):",
    "gui_dry_run": "List only (--dry-run)",
    "gui_force": "Re-download (--force)",
    "gui_no_preflight": "Skip preflight (--no-preflight)",
    "gui_hint": "Hint: leave proxy / output dir / limit blank to use the script defaults; "
                "tag syntax such as language:chinese$ / female:cat / -male:cat "
                "(space-separated); --limit applies to galleries in search mode and to "
                "images in single-gallery mode; Pick, Pages per gallery and List only "
                "are mainly for the search flow; for the private site, save cookies to "
                ".ehcookie (one k=v per line) and set Site to exhentai - leaving the "
                "cookie file blank reads it automatically",
    "gui_start": "▶ Start",
    "gui_stop": "■ Stop",
    "gui_status_idle": "Idle",
    "gui_status_running": "Running...",
    "gui_status_stopping": "Stopping...",
    "gui_status_done": "Finished (exit code {code})",
    "gui_log_frame": " Log ",
    "gui_lang_switched": "Language switched to {lang}",
    "gui_dlg_output_dir": "Select output directory",
    "gui_dlg_manifest_file": "Select manifest file",
    "gui_dlg_cookie_file": "Select cookie file",
    "gui_filetype_cookie": "Cookie files (*.txt;*.ehcookie)",
    "gui_filetype_all": "All files",
    "gui_err_need_tags": "Tag search mode requires tags (--tags)",
    "gui_err_need_url": "Single gallery mode requires a gallery URL",
    "gui_err_need_manifest": "Manifest mode requires a manifest file (--from-manifest)",
    "gui_msg_running_title": "Notice",
    "gui_msg_running": "A task is already running",
    "gui_err_title": "Error",
    "gui_err_args_title": "Invalid arguments",
    "gui_err_scraper_missing": "Cannot find {name}; make sure it is in the same folder.",
    "gui_proc_exit": "[Process exited, exit code {code}]",
    "gui_stop_requested": "Stop requested",
    "gui_selftest_search": "Search mode:",
    "gui_selftest_gallery": "Single gallery mode:",
    "gui_selftest_site": "Private site mode:",
    "gui_selftest_public": "Public site mode (no --site expected):",
    "gui_selftest_manifest": "Manifest mode:",
    "gui_selftest_assert_tags": "tag search did not raise when tags were empty",
    "gui_selftest_ok": "OK: window build + argument assembly all passed.",

    # ---------- 抓取器 ----------
    "eh_err_parse_url": "Cannot parse gid/token from URL: {url}",
    "eh_proxy_auto": "Auto-selected local proxy {url} (override with --proxy)",
    "eh_search_page": "  Search page {page}: parsed {got} (new {fresh}, total {total}{cap})",
    "eh_gallery_links_page": "  Gallery page {page}: {n} links (total {total})",
    "eh_gallery_links_enough": "  Reached {n} images, stop paging",
    "eh_manifest_write_failed": "Failed to write manifest: {err}",
    "eh_manifest_not_found": "Manifest file not found: {path}",
    "eh_manifest_unreadable": "Cannot read manifest ({kind}): {err}",
    "eh_results_title": "\n===== Search results{summary} =====",
    "eh_results_summary": " ({total} total{note})",
    "eh_col_pages": "Pages",
    "eh_col_category": "Category",
    "eh_col_title": "Title",
    "eh_results_footer": "  ({n} total. Use --pick 2-4,7 to pick some; "
                         "the number is the # above)",
    "eh_image_list_title": "\n===== Image list ({n} images) =====",
    "eh_desc": "e-hentai gallery downloader v3 (single gallery / tag search / dry-run / pick)",
    "eh_epilog_examples": "Examples:",
    "eh_epilog_note": "--limit / --pick apply to the current list:\n"
                      "  search mode = galleries found;  single gallery mode = images "
                      "in the gallery\n",
    "eh_help_url": "Gallery URL, e.g. https://e-hentai.org/g/3817181/3b0370c5a1/",
    "eh_help_tags": "Tag search (either this or URL). Syntax: language:chinese$ / "
                    "female:cat / -male:cat / ~cat, space-separated",
    "eh_help_output": "Save directory. Blank = read .pawout in the project root "
                      "(else current dir); in search mode it is the root, in single "
                      "gallery mode it is that gallery's folder",
    "eh_help_limit": "Search mode: take the first N galleries (default {n}, inf=all); "
                     "single gallery mode: download the first N images (default 120)",
    "eh_help_pick": "Pick by list index, e.g. 2-4,7 / 3- / all "
                    "(index = the # shown by dry-run)",
    "eh_help_pages": "Search mode only: at most N images per gallery (default inf=all)",
    "eh_help_dry_run": "Only fetch the list, do not download (also writes the list to "
                       "the file given by --manifest)",
    "eh_help_manifest": "File name used by --dry-run to save the list "
                        "(default eh_manifest.json)",
    "eh_help_from_manifest": "Read the result from this manifest, skipping the search "
                             "request (use with --pick for exact reproduction)",
    "eh_help_workers": "Number of concurrent threads (default 4)",
    "eh_help_delay": "Max random delay in seconds before each request (default 1.0). "
                     "e-hentai rate-limits aggressively, do not set it too low",
    "eh_help_cooldown": "Seconds all threads stay quiet after a 429/503, default 20",
    "eh_help_force": "Re-download images that already exist (default: skip if present)",
    "eh_help_proxy": "Proxy: blank=auto detect, off=direct, or http://127.0.0.1:7897",
    "eh_help_no_preflight": "Skip the proxy preflight check before sending requests",
    "eh_err_fetch_gallery_indent": "  Failed to fetch gallery page: {err}",
    "eh_err_fetch_gallery": "Failed to fetch gallery page: {err}",
    "eh_err_no_links_indent": "  No image links found (the gallery may be deleted or "
                              "require login).",
    "eh_err_no_links": "No image links found (the gallery may be deleted or "
                       "require login).",
    "eh_pages_limited": "  --pages {pages}: only the first {n} images of this gallery",
    "eh_output_dir_indent": "  Output dir: {path}",
    "eh_output_dir": "Output dir: {path}",
    "eh_err_pages_invalid": "--pages must be a positive integer or inf.",
    "eh_skip_exists": "  [{idx}] already exists, skipped",
    "eh_err_no_img_src": "No image src found on the detail page",
    "eh_err_empty_file": "Downloaded file is empty",
    "eh_done_progress": "  #{idx} done -> {name} (progress {done}/{total})",
    "eh_job_failed": "  [{idx}] failed: {err}",
    "eh_need_url_or_tags": "Please give a gallery URL or --tags (one of the two).",
    "eh_example_url": '  e.g.: python EH_scraper_v2.py "https://e-hentai.org/g/xxx/yyy/"',
    "eh_example_tags": '  e.g.: python EH_scraper_v2.py --tags "language:chinese$" '
                       "--limit 30 --dry-run",
    "eh_example_manifest": "  e.g.: python EH_scraper_v2.py --from-manifest "
                           "eh_manifest.json --pick 2-4,7",
    "eh_proxy_enabled": "Proxy enabled: {proxy}",
    "eh_proxy_direct": "No proxy (direct connection) - e-hentai usually cannot be "
                       "reached directly from within China; if it fails, add "
                       "--proxy http://127.0.0.1:7897",
    "eh_manifest_no_images": "No images in the manifest.",
    "eh_manifest_read_images": "Read {n} images from manifest: {title}",
    "eh_pick_images": "--pick selected {n} images (original index used as filename)",
    "eh_download_done": "\n===== Download complete =====",
    "eh_summary_counts": "OK: {ok} | skipped: {skip} | failed: {fail}",
    "eh_saved_to": "Files saved to: {path}",
    "eh_manifest_read_galleries": "Read {n} galleries from manifest "
                                  "(original search: {query})",
    "eh_query_unrecorded": "(not recorded)",
    "eh_manifest_no_galleries": "No galleries in the manifest.",
    "eh_limit_capped": "--limit too large, {n} is enough (hard cap {cap}).",
    "eh_search_start": "\nSearch: {query}",
    "eh_search_target": "Target: collect the first {n} galleries",
    "eh_search_failed": "Search request failed: {err}",
    "eh_search_empty": "No galleries found. Check the tag syntax "
                       "(e.g. language:chinese$).",
    "eh_manifest_saved": "\nManifest saved: {path}",
    "eh_manifest_next_hint": "Next time: python {prog} --from-manifest {manifest} "
                             "--pick 2-4,7",
    "eh_pick_galleries": "\n--pick selected {n} galleries: {idx}",
    "eh_output_root": "\nOutput root: {path}",
    "eh_all_done": "\n===== All done =====",
    "eh_galleries_selected": "Galleries: {n} selected",
    "eh_images_summary": "Images: OK {ok} | skipped {skip} | failed {fail}",
    "eh_saved_root": "Saved to: {path}",
    "eh_gallery_meta": "Gallery title: {title} | files: {count} | category: {category}",
    "eh_gallery_tags": "Tags: {tags}",
    "eh_gallery_meta_missing": "gdata API returned nothing; falling back to naming "
                               "the folder from the URL.",
    "eh_fetching_links": "Paging through the gallery to collect image detail links...",
    "eh_pick_images_in_limit": "--pick selected {n} images (out of the first {limit}; "
                               "original index {idx} used as filename)",
    "eh_download_plan": "{n} images in total (download limit {limit}), {workers} "
                        "threads, random delay 0~{delay}s",
    "eh_gallery_summary": "Gallery: {title} (gid={gid})",

    # ---------- ExHentai / cookies ----------
    "eh_help_site": "Target site: e-hentai=public site (default, works as guest) | "
                    "exhentai=private site (cookie required). With a gallery URL, blank means "
                    "the site is inferred from the URL host",
    "eh_help_cookie": "Raw cookie string, e.g. \"ipb_member_id=...; ipb_pass_hash=...; igneous=...\"",
    "eh_help_cookie_file": "Read cookies from a file (browser-exported cookies.txt or one k=v per line). "
                           "Blank = env EH_COOKIE > ./.ehcookie > <script dir>/.ehcookie",
    "eh_site_selected": "Target site: {site}",
    "eh_site_from_url": "URL points at {site}; switched to it automatically",
    "eh_cookie_loaded": "Loaded {n} cookie entries (source: {source})",
    "eh_cookie_none": "No cookies supplied (guest mode: public-site content only)",
    "eh_cookie_file_bad": "Cannot read cookie file: {path}",
    "eh_cookie_empty": "Parsed no cookies. Expected `name=value` pairs separated by ';' or newlines",
    "eh_cookie_igneous": "  igneous = {value} (private-site pass)",
    "eh_ex_need_cookie": "The private site requires cookies - none supplied. Get one first.",
    "eh_ex_hint": "How: log in on the public site -> open exhentai.org (if it loads, the account has "
                  "access) -> F12 -> Application -> Cookies -> save ipb_member_id / ipb_pass_hash / "
                  "igneous into .ehcookie (one k=v per line), then run with --site exhentai",
    "eh_ex_no_rights": "Cannot enter the private site: igneous = {value}, so the account has no "
                       "private-site access (or the value expired). A valid one is 17 characters long.",
    "eh_ex_blocked": "Cannot enter the private site: igneous = {value}... looks valid, but the front "
                     "page is still blank - most likely the exit IP is blocked (common with shared "
                     "nodes), or ipb_member_id / ipb_pass_hash are missing.",
    "eh_ex_probe_failed": "Private-site probe failed (network/proxy level): {err}",
    "eh_ex_blank_hint": "  Note: this blank page is HTTP 200, not an error - the private site denies "
                        "access by returning a blank page.",
    "eh_blank_page_warn": "  Got a blank page (HTTP 200) - cookies probably expired mid-run. "
                          "Log in again, refresh igneous, and rerun.",
    "eh_blank_page_warn_public": "  Got an empty page (HTTP 200) - the public site needs no "
                                 "cookies, so this is more likely a flaky proxy node. Retry.",

    # ---------- 公共库 ----------
    # ⚠️ 这一段必须与 felinepaw/i18n.py 的同名段保持一致：两边的 common.py 是逐字节拷贝。
    "common_limit_invalid": "--limit must be a positive integer or inf.",
    "common_pick_empty": "--pick is empty. Use an index expression such as 2-4,7 (or all).",
    "common_pick_none_left": "--pick left nothing to download.",
    "common_help_delay": "Base delay in seconds before each request, default 0 (no throttling). Try --delay 1.0 if the site rate-limits you",
    "common_help_jitter": "Random jitter in seconds added to the base delay, default 0. Use it with --delay (e.g. --delay 1 --jitter 1.5) so the pace does not look robotic",
    "common_help_cooldown": "Seconds all threads stay quiet after a 429/503, default 20",
    "common_help_no_preflight": "Skip the proxy preflight before sending requests (by default about 1 second is spent confirming the link, so failures say clearly whether Clash is not running or the node is bad)",
    "common_pick_dash": "In --pick, '-' needs at least one number on either side: {part!r}",
    "common_pick_reversed": "--pick range is reversed ({start} > {end}): {part!r}",
    "common_pick_bad": "Cannot parse this part of --pick: {part!r} (supported: 2-4,7 / 3- / -3 / all)",
    "common_pick_oob_n": "Ignored {n} out-of-range index(es) in --pick ({first}~{last} etc.; the list has only {total})",
    "common_pick_oob_list": "Ignored out-of-range index(es) in --pick: {ids} (the list has only {total})",
}


# ============================================================
# 语言偏好（跨进程、跨会话）
# ============================================================

def pref_path() -> Path:
    return Path.home() / ".paw" / ("%s.lang" % APP_ID)


def read_pref() -> str:
    """读上次选的语言；没有或不认识就返回空串。"""
    try:
        s = pref_path().read_text(encoding="utf-8").strip().lower()
    except OSError:
        return ""
    return s if s in LANGS else ""


def save_pref(lang: str) -> None:
    """记住选择。写不进去就算了 —— 只读目录（exe 装进 Program Files）不值得报错。"""
    try:
        p = pref_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(lang, encoding="utf-8")
    except OSError:
        pass


def _initial() -> str:
    env = os.environ.get(LANG_ENV, "").strip().lower()
    if env in LANGS:
        return env
    return read_pref() or "zh"


_CURRENT = _initial()


def set_lang(lang: str, persist: bool = True) -> None:
    """切当前语言。

    persist=True（默认）= 同时写偏好文件。GUI 里点下拉框就走这条；
    子进程从不调它（靠 PAW_LANG 环境变量），所以日志不会被"顺手改掉"偏好。
    """
    global _CURRENT
    _CURRENT = lang if lang in LANGS else "zh"
    if persist:
        save_pref(_CURRENT)


def get_lang() -> str:
    return _CURRENT


def t(key: str, **kw) -> str:
    """取当前语言的文案；缺 key 时退化到中文，再退化到 key 本身（便于发现漏翻）。"""
    table = EN if _CURRENT == "en" else ZH
    s = table.get(key)
    if s is None:
        s = ZH.get(key, key)
    if kw:
        try:
            return s.format(**kw)
        except (KeyError, IndexError, ValueError):
            return s
    return s
