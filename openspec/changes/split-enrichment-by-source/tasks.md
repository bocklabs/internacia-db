## 1. Per-source enrichment
- [x] 1.1 Source policy and thresholds (`data/schemas/enrichment_sources.yaml`)
- [x] 1.2 Split and review gate (`internacia_builder/enrichment_sources.py`, `scripts/enrichment_split.py`)
- [x] 1.3 `enrichment-check.yml`: one PR per source, auto-merge or `needs-review`
- [x] 1.4 Changed-record rule skips metadata-only intblock changes
- [ ] 1.5 Set `ENRICHMENT_REVIEWER`, "Allow auto-merge" and branch protection; watch the first run (maintainer)
