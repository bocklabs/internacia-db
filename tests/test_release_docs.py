"""Release and SDK-status docs must match the build and the current DuckDB."""

import re

import duckdb
import pytest

from internacia_builder.paths import datasets_dir, project_root

DOCS = project_root() / "docs"
DUCKDB_PATH = datasets_dir() / "internacia.duckdb"


def _section(text: str, heading: str) -> str:
    start = text.index(f"## {heading}\n")
    end = text.find("\n## ", start + 1)
    return text[start : end if end != -1 else None]


def _slug(heading: str) -> str:
    return re.sub(r"\s", "-", re.sub(r"[^\w\- ]", "", heading.strip().lower()))


def test_documented_release_assets_match_build():
    section = _section((DOCS / "release-distribution.md").read_text(encoding="utf-8"), "Release assets")
    rows = [line for line in section.splitlines() if line.startswith("| ") and "`" in line]
    documented = {name for row in rows for name in re.findall(r"`([^`]+)`", row)}
    assert "migration.vX.Y.Z.json" in documented
    built = {
        path.name
        for path in datasets_dir().iterdir()
        if path.is_file() and not re.fullmatch(r"migration\.v.+\.json", path.name)
    }
    assert documented - {"migration.vX.Y.Z.json"} == built


def test_llm_scenario_anchors_resolve():
    text = (DOCS / "llm-scenarios.md").read_text(encoding="utf-8")
    anchors = {_slug(h) for h in re.findall(r"^#+ (.+)$", text, re.MULTILINE)}
    links = set(re.findall(r"\]\(#([^)]+)\)", text))
    assert links and links <= anchors, links - anchors


def _scenario_sql(text: str, heading_prefix: str) -> list[str]:
    heading = next(h for h in re.findall(r"^## (.+)$", text, re.MULTILINE) if h.startswith(heading_prefix))
    sql = re.findall(r"```sql\n(.*?)```", _section(text, heading), re.DOTALL)
    return [s.replace("'data/datasets/", f"'{datasets_dir().as_posix()}/") for s in sql]


@pytest.mark.skipif(not DUCKDB_PATH.is_file(), reason="internacia.duckdb not built")
def test_llm_scenario_sql_runs():
    text = (DOCS / "llm-scenarios.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```sql\n(.*?)```", text, re.DOTALL)
    assert len(blocks) >= 30
    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    try:
        for sql in blocks:
            sql = sql.replace("'data/datasets/", f"'{datasets_dir().as_posix()}/")
            if re.search(r"^\s*(SELECT|WITH)\b", sql, re.MULTILINE | re.IGNORECASE):
                con.execute(sql).fetchall()
        assert con.execute(_scenario_sql(text, "1.")[0]).fetchone()[0] == "US"
        assert con.execute(_scenario_sql(text, "2.")[0]).fetchone()[0] == "US"
        fuzzy = _scenario_sql(text, "6.")[0]
        assert con.execute(fuzzy).fetchone()[1] == "EU"
        assert con.execute(fuzzy.replace("欧盟", "Untied States")).fetchone()[1] == "US"
        assert con.execute(_scenario_sql(text, "7.")[0]).fetchall() == [("EU", "European Union")]
        assert len(con.execute(_scenario_sql(text, "8.")[0]).fetchall()) == 20
        current = {row[0] for row in con.execute(_scenario_sql(text, "4.")[0].replace("LIMIT 20", "")).fetchall()}
        assert "NATO" in current and "NAFTA" not in current
        assert con.execute(_scenario_sql(text, "28.")[0]).fetchone()[0] == "UNASUR"
    finally:
        con.close()
