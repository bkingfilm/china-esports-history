"""给 RSS 提供文章的原始首发日期。

全书 67 篇正文都是 2013 至 2018 年陆续首发在知乎专栏的旧文，
2026-07-25 才一次性导入本仓库。mkdocs-rss-plugin 默认取 git 提交时间，
结果 feed 里 20 条的时间戳全是导入那一秒，订阅端会看到一堆同时刻的条目。

正文第一行本来就写着出处，形如：

    > 首发于知乎专栏（2013-11-12）原文链接：https://zhuanlan.zhihu.com/p/19611097

这里把那个日期抽出来塞进 page.meta，由 mkdocs.yml 的 date_from_meta 读走。
用 hook 而不是给 67 个文件加 front matter，是为了不改正文一个字节。

事件用 on_page_markdown，早于插件读 meta 的 on_page_content。
"""

import logging
import re

LOG = logging.getLogger("mkdocs.plugins.rss_date")

# 全角括号，日期形如 2013-11-12。出处站点不限死，只认「首发于」和括号里的日期。
FIRST_PUBLISHED = re.compile(r"首发于[^（\n]*（(\d{4}-\d{2}-\d{2})）")

AUTHOR = "BBKinG"

# 摘要要跳过的行：标题、出处引用、图片、视频说明、分隔线、HTML 标签
_SKIP_LINE = re.compile(
    r"^\s*(#|>|!\[|\[\s*!\[|<|-{3,}|\*{3,}|视频[/／]|图[/／])"
)

_hits = 0
_misses = []


def _first_paragraph(markdown: str, limit: int = 160) -> str:
    """取正文第一段真正的内容，供 RSS 摘要用。

    正文开头依次是 h1 标题、「首发于知乎专栏」出处引用、有时还有配图和
    「视频/CCTV5」这类说明行。插件默认从头截 240 字，截出来的全是这些，
    订阅端看到的每条摘要长得一模一样，所以这里自己挑第一段正文。
    """
    for line in markdown.splitlines():
        text = line.strip().strip("　")  # 正文段落以全角空格缩进
        if not text or _SKIP_LINE.match(line.strip()):
            continue
        # markdown 行内标记与链接去掉，摘要是纯文本。
        # 裸 URL 也要删：正文里夹着独立成行的知乎视频地址，删完这行就空了，
        # 会被下面的长度关挡掉，不会当成摘要。
        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"[*_`\[\]]", "", text).strip()
        if len(text) < 20:  # 太短的多半是小标题或图注，跳过
            continue
        return text[:limit] + ("…" if len(text) > limit else "")
    return ""


def on_page_markdown(markdown, page, config, files, **kwargs):
    """把首发日期、作者、摘要写进 page.meta，供 mkdocs-rss-plugin 读取。"""
    global _hits

    src = page.file.src_uri
    # 只管简体正文，跟 mkdocs.yml 里 rss 插件的 match_path 保持一致
    if not src.startswith("zh/") or src.endswith("index.md"):
        return markdown

    match = FIRST_PUBLISHED.search(markdown)
    if match:
        page.meta["date_created"] = match.group(1)
        _hits += 1
    else:
        # 没有首发行的篇目让插件回退到 git 时间，不阻断构建
        _misses.append(src)

    page.meta.setdefault("author", AUTHOR)

    if "description" not in page.meta:
        abstract = _first_paragraph(markdown)
        if abstract:
            page.meta["description"] = abstract

    return markdown


def on_post_build(config, **kwargs):
    LOG.info("RSS 首发日期注入：命中 %d 篇", _hits)
    if _misses:
        LOG.info(
            "无首发行、回退 git 时间的 %d 篇：%s",
            len(_misses),
            "、".join(_misses),
        )
