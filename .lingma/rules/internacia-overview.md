<!-- Generated from templates/agent-shims/.lingma/rules/internacia-overview.md by scripts/generate_agent_shims.py; edit the template and rerun. -->
# Internacia 全局规则

本仓库是 **国家与国际组织参考数据集**（YAML 源 + DuckDB/Parquet 导出）。

## 必须遵守

- **禁止** 给 countries 添加 HDI、GDP、政体等社会经济字段。
- intblock 成员关联用 `includes[].id`（国家 alpha-2），不用 `includes[].name`。
- `borders` 为 alpha-3；关联时用 `iso3code`。
- 不要手改 `data/datasets/`（由 `python scripts/builder.py build` 生成）。

查询请使用 `data/datasets/internacia.duckdb` 或 Parquet 导出，不要解析源 YAML。导出文件不提交到仓库：先运行一次 `python scripts/builder.py build`（或从最新 GitHub Release 下载）。

## 详细指南

请阅读 [AGENTS.zh.md](../../AGENTS.zh.md) 与 [docs/agents/zh/query.md](../../docs/agents/zh/query.md)。

## 校验命令

```bash
python scripts/validate_countries.py --json
python scripts/validate_intblocks.py --json
pytest tests/
```
