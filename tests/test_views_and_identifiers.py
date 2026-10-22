"""Canonical views and reference tables inside DuckDB; identifier stability."""
import duckdb
import pytest

from internacia_builder.contract import build_contract
from internacia_builder.paths import datasets_dir, project_root
from internacia_builder.validate.identifiers import (
    check_identifier_stability,
    ids_at_ref,
    previous_release_ref,
)

DUCKDB_TYPES = {"VARCHAR": "string", "BOOLEAN": "boolean", "BIGINT": "int64", "INTEGER": "int32", "DOUBLE": "float64"}


@pytest.fixture(scope="module")
def con():
    with duckdb.connect(str(datasets_dir() / "internacia.duckdb"), read_only=True) as connection:
        yield connection


def test_every_contract_relation_is_in_duckdb_with_its_kind(con):
    kinds = dict(con.execute("SELECT table_name, table_type FROM information_schema.tables").fetchall())
    for table in build_contract("3.0.0")["tables"]:
        assert table["in_duckdb"]
        assert kinds[table["name"]] == ("VIEW" if table["kind"] == "view" else "BASE TABLE")


def test_view_columns_match_the_contract(con):
    for table in build_contract("3.0.0")["tables"]:
        if table["kind"] != "view":
            continue
        described = con.execute(f"DESCRIBE {table['name']}").fetchall()
        assert [(row[0], DUCKDB_TYPES[row[1]]) for row in described] == [
            (c["name"], c["type"]) for c in table["columns"]
        ]


def test_current_memberships_excludes_former_and_ended(con):
    current = {r[0] for r in con.execute("SELECT intblock_id FROM current_memberships WHERE country_code = 'US'").fetchall()}
    former = {
        r[0]
        for r in con.execute(
            "SELECT intblock_id FROM memberships WHERE country_code = 'US' AND status = 'former_member'"
        ).fetchall()
    }
    assert "NATO" in current
    assert former and not (current & former)
    historical = con.execute(
        "SELECT count(*) FROM current_memberships m JOIN intblocks i ON i.id = m.intblock_id "
        "WHERE i.status = 'historical' OR i.dissolved IS NOT NULL OR m.\"left\" IS NOT NULL"
    ).fetchone()[0]
    assert historical == 0


def test_country_views_are_null_safe(con):
    null_currency = con.execute("SELECT code FROM countries WHERE currencies IS NULL LIMIT 1").fetchone()
    assert null_currency is not None
    assert con.execute("SELECT count(*) FROM country_currencies WHERE country_code = ?", null_currency).fetchone()[0] == 0
    assert con.execute("SELECT currency_code FROM country_currencies WHERE country_code = 'CH'").fetchall() == [("CHF",)]
    assert con.execute("SELECT count(*) FROM country_timezones WHERE country_code = 'US'").fetchone()[0] > 1


def test_alias_tables_are_queryable(con):
    assert con.execute("SELECT target FROM intblocks_aliases WHERE alias = 'USAN'").fetchone() == ("UNASUR",)
    assert con.execute("SELECT count(*) FROM attribute_intblock_migrations").fetchone()[0] > 0


def test_identifier_stability_requires_alias():
    errors = check_identifier_stability("intblock", {"A", "B", "C"}, {"A"}, {"B"}, "v1.0.0", "aliases.yaml")
    assert len(errors) == 1
    assert "'C' existed in v1.0.0" in errors[0]


def test_previous_release_ids_come_from_git():
    ref = previous_release_ref(project_root())
    if ref is None:
        pytest.skip("no release tag reachable (shallow clone)")
    ids = ids_at_ref(project_root(), ref, "data/intblocks")
    assert ids and "NATO" in ids
