# Internacia 全局规则

本仓库是 **国家与国际组织参考数据集**（YAML 源 + DuckDB/Parquet 导出）。

## 必须遵守

{{ guardrails_zh }}

{{ data_access_zh }}

## 详细指南

请阅读 [AGENTS.zh.md](../../AGENTS.zh.md) 与 [docs/agents/zh/query.md](../../docs/agents/zh/query.md)。

## 校验命令

```bash
python scripts/validate_countries.py --json
python scripts/validate_intblocks.py --json
pytest tests/
```
