<!-- Generated from templates/agent-shims/.kimi/AGENTS.md by scripts/generate_agent_shims.py; edit the template and rerun. -->
# Kimi Code — Internacia 补充说明

完整中文指南：[AGENTS.zh.md](../AGENTS.zh.md)  
English: [AGENTS.md](../AGENTS.md)

## 长任务（K3）建议

1. 先读 [llms.zh.txt](../llms.zh.txt)（紧凑索引），再按需打开 `docs/agents/zh/query.md`。
2. 查询请使用 `data/datasets/internacia.duckdb` 或 Parquet 导出，不要解析源 YAML。导出文件不提交到仓库：先运行一次 `python scripts/builder.py build`（或从最新 GitHub Release 下载）。
3. **编辑** YAML 前读 [docs/agents/zh/contribute.md](../docs/agents/zh/contribute.md)，完成后运行：

```bash
python scripts/validate_countries.py --json
python scripts/validate_intblocks.py --json
```

## 硬性护栏

- **禁止** 给 countries 添加 HDI、GDP、政体等社会经济字段。
- intblock 成员关联用 `includes[].id`（国家 alpha-2），不用 `includes[].name`。
- `borders` 为 alpha-3；关联时用 `iso3code`。
- 不要手改 `data/datasets/`（由 `python scripts/builder.py build` 生成）。

## 中文查询示例

见 [docs/query-examples.zh.md](../docs/query-examples.zh.md)。
