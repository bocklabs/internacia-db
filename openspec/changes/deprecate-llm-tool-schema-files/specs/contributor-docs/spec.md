## MODIFIED Requirements

### Requirement: LLM tool-call schema artifacts

Tool-call definitions for LLM agents SHALL come from the internacia SDK (`internacia.tools`), which generates them from the SDK's query methods and the connected database. `docs/ai-consumers.md` SHALL document this. The hand-written `data/schemas/country_lookup.openai.json` and `data/schemas/intblock_lookup.openai.json` are deprecated: they SHALL remain for one MINOR release after the SDK release that ships `internacia.tools` and SHALL then be removed.

#### Scenario: Agent loads country lookup schema

- **WHEN** an integrator follows `docs/ai-consumers.md` to get tool definitions
- **THEN** it is directed to `internacia.tools.openai_tools()`, which defines lookup by ISO code or name without nested struct definitions

#### Scenario: Deprecated files remain during the window

- **WHEN** an integrator still reads `data/schemas/country_lookup.openai.json` during the deprecation window
- **THEN** the file exists and the documentation marks it deprecated
