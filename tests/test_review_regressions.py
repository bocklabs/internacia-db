"""Consumer regressions for reviewed data corrections and shared scope rules."""
import json
import re

import duckdb
import pytest

from internacia_builder.paths import datasets_dir, project_root
from internacia_builder.validate.intblock_rules import check_intblock_scope_category, check_scope_coverage
from internacia_builder.validate.intblocks import validate_scope_category


def test_scope_warning_is_shared_and_missing_count_is_ratcheted():
    record = {"id": "ORG", "status": "formal"}
    issue = check_intblock_scope_category(record)[0]
    assert validate_scope_category([("org.yaml", record)]) == [f"org.yaml: {issue['suggested_action']}"]
    assert check_scope_coverage([record], {"scope_category": {"max_missing_formal": 0}})
    assert not check_scope_coverage([record], {"scope_category": {"max_missing_formal": 1}})
    assert check_scope_coverage([record], {"scope_category": {"max_missing_formal": 2, "pending_taxonomy": {"MSF": "NGO", "CANTO": "NGO"}}})


def test_corrected_roster_and_merged_entities():
    with duckdb.connect(str(datasets_dir() / "internacia.duckdb"), read_only=True) as con:
        assert con.execute("SELECT count(*) FROM memberships WHERE intblock_id='ECOWAS' AND status IN ('member','founding_member')").fetchone()[0] == 12
        assert con.execute("SELECT country_code FROM memberships WHERE intblock_id='ECOWAS' AND status='former_member' AND \"left\"='2025-01-29' ORDER BY 1").fetchall() == [("BF",), ("ML",), ("NE",)]
        for qid in ("Q5153892", "Q2863003", "Q4230"):
            assert con.execute("SELECT count(*) FROM intblocks WHERE wikidata_id=?", [qid]).fetchone()[0] == 1
        assert con.execute("SELECT partof FROM intblocks WHERE id='COL'").fetchone()[0] == ["COMMONWEALTH"]
    aliases = {r["alias"]: r["target"] for r in json.loads((datasets_dir() / "intblocks_aliases.json").read_text())}
    assert {k: aliases[k] for k in ("COMMLEARN", "ABCZNZ", "USAN")} == {"COMMLEARN": "COL", "ABCZNZ": "ABCANZ", "USAN": "UNASUR"}


@pytest.mark.parametrize(("status", "full_member"), [
    ("member", True), ("founding_member", True), ("former_member", False),
    ("partner", False), ("observer", False), ("funder", False), ("participant", False),
])
def test_documented_full_membership_predicate(status, full_member):
    docs = (project_root() / "docs/ai-consumers.md").read_text().split("### Current full membership", 1)[1]
    sql = re.search(r"```sql\n(.*?)```", docs, re.S)[1]
    with duckdb.connect() as con:
        con.execute("CREATE TABLE memberships (intblock_id VARCHAR, country_code VARCHAR, status VARCHAR)")
        con.execute("INSERT INTO memberships VALUES ('ORG', 'US', ?)", [status])
        assert bool(con.execute(sql).fetchall()) is full_member
