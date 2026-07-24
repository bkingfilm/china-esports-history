# 参与贡献

感谢你帮助保存和整理中国电竞史料。

## 你可以参与

- **补充史料或纠错**：使用“补充史料 / 纠错”Issue 模板，尽量注明时间、地点、人物和一手来源。
- **请求或参与翻译**：使用英文翻译请求模板。翻译前请阅读 [多语言与翻译工作流](project/localization.md)。
- **维护目录与站点**：阅读 [信息架构](project/information-architecture.md)、[内容映射](project/content-map.csv) 和 [维护规范](project/maintenance.md)。

不要在没有来源和作者确认的情况下直接重写历史叙述。事实争议应先记录证据并讨论。

## 提交前

安装 `requirements.txt` 后执行：

```bash
python scripts/validate_content.py
python -m mkdocs build --strict
python scripts/validate_content.py --site site
git diff --check
```

PR 请清楚说明是否改动正文、如何验证，以及内容页和构建页数量是否变化。
