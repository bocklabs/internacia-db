# Change: Deprecate hand-written LLM tool schema files

## Why
`data/schemas/country_lookup.openai.json` and `intblock_lookup.openai.json` are maintained by
hand and drift from the data (their `scope_category` enum is hard-coded). The internacia SDK, the
single query layer (decision D2), now generates tool schemas from its own signatures and the
connected database (`internacia.tools`, SDK 0.4), and can execute the calls.

## What Changes
- Documentation points to `internacia.tools` for tool definitions.
- The two JSON files stay unchanged for one more MINOR release after the SDK release that ships
  `internacia.tools`, then they are removed.

## Impact
- Affected specs: contributor-docs
- Affected docs: `docs/ai-consumers.md`, `llms.txt`, `llms-full.txt`
