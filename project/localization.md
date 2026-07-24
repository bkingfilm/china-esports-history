# 多语言架构与翻译工作流

## Locale 与对应关系

简体中文 `zh` 是权威原文和默认阅读语言，英文 `en` 是首个目标语言。每篇内容由 `content_id` 标识，不使用文件名匹配译文。对应关系与状态统一记录在 `project/content-map.csv`。

允许的翻译状态：

- `not_started`：未开始；
- `translating`：翻译中，不能加入正式导航；
- `review`：待语言和史实校对；
- `published`：已发布并通过构建检查。

## 缺失译文与 fallback

站点不自动显示机器翻译，也不把中文正文伪装成英文页。英文缺失时：

1. 英文导航不创建空白章节；
2. 英文首页说明当前覆盖范围并链接中文目录；
3. 读者可通过 translation request 提议下一篇；
4. 搜索仍能找到中文原文；
5. 不进行内容级自动跳转，以免用户误判当前语言。

## 页面 metadata

现有正文的权威 metadata 存在映射表中，以避免一次性给 67 篇原文加入大段 front matter。新增或翻译内容至少维护：

- `content_id`
- locale
- 页面标题
- 原始发布日期（可确认时）
- 内容时期
- 主题
- 涉及实体
- 翻译状态
- counterpart 路径

若未来在 Markdown 中加入 front matter，字段名必须与映射表一致，并通过脚本检查两者没有冲突。

## 语言导航与 SEO

- 根页面提供明确语言入口。
- Material 的 `extra.alternate` 生成语言选择入口和 `hreflang` alternate。
- `site_url` 让 MkDocs 为页面生成 canonical，并生成 sitemap。
- 全站 alternate 当前指向各语言首页；只有映射表中 `published` 的 counterpart 才能建立内容级互链。
- 新 locale 必须先有 locale 首页、导航文案、搜索语言配置和 fallback 说明，再加入语言切换器。

## 翻译流程

1. 在映射表把目标语言状态改为 `translating`，填写预定路径。
2. 从中文原文翻译，不从第三方转载或二手译文回译。
3. 保留来源、引文边界、作者语气、图片和注释；不把推测改成事实。
4. PR 中列出术语选择、无法确认的专名和可能需要作者判断之处。
5. 由至少一名中文史料校对者和一名目标语言校对者审查。
6. 状态改为 `review`，通过链接、映射和严格构建。
7. 审查通过后改为 `published`，加入目标语言导航并建立 counterpart 链接。

机器翻译只能作为未发布草稿，不能在没有人工审查时标记为 `published`。
