# 内容维护、质量检查与审查规范

## 新文章接入

1. 确认授权、原始来源、标题与发布日期。
2. 分配不复用的 `content_id`。
3. 选择栏目；无法确定时先放入 `appendix`，在 PR 说明原因。
4. 把正文放入 `docs/zh/<section>/`，资源放入 `docs/assets/`。
5. 在 `project/content-map.csv` 增加一行，并更新栏目索引和 `mkdocs.yml` 导航。
6. 运行完整质量检查并在 PR 报告内容数、页面数变化。

## 图片与附件

- 保留原始文件，不重新压缩、不覆盖，不移除 EXIF，除非版权或隐私审查明确要求。
- 文件名在发布后视为稳定路径；替换资源应使用新文件名。
- 图片使用相对路径和有意义的替代文本；历史原文中缺失的替代文本可另开无事实改写的可访问性 PR。
- 不把构建输出 `site/`、缓存或远端抓取的临时文件提交到仓库。

## 内部链接

- 链接必须指向仓库内真实文件；目录移动后同时修复所有入站与出站引用。
- 文章内部使用相对路径，README 从仓库根目录使用 `docs/...`。
- 链接到另一语言时必须明确 locale。
- 锚点检查受 Markdown 渲染器影响；修改标题时应视为潜在 URL 破坏并单独审查。

## 本地构建与质量检查

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python scripts/validate_content.py
.venv/Scripts/python -m mkdocs build --strict
.venv/Scripts/python scripts/validate_content.py --site site
git diff --check
```

非 Windows 环境把 `.venv/Scripts/python` 换成 `.venv/bin/python`。检查器验证映射数量、文件存在性、唯一 ID、导航覆盖、内部链接、图片、翻译 counterpart、重复路由及构建后的 HTML 页面数。

## PR 审查

内容 PR 必须说明：

- 内容来源与授权；
- 是否修改正文，以及逐项理由；
- 新增或改变的 `content_id`、路径和 locale；
- 事实、日期、姓名或译名中仍有疑问的部分；
- 执行过的命令和结果；
- 内容与页面计数变化。

审查时优先检查史实完整性、来源、作者表达和链接，再检查分类与样式。发现疑似事实冲突时，在 PR 或独立审查文档记录证据，不在结构重构中直接改写。

目录迁移、正文勘误、翻译和视觉样式原则上拆成不同提交，便于上游作者逐项判断和回退。
