# Retired intblock IDs without replacements

This document tracks removed intblock records that do **not** have an equivalent current intblock. Unlike a rename or merge, a retirement has no successor: the ID is recorded in `data/intblocks_aliases.yaml` with `reason: retired` and no `target`, so the generated `intblocks_aliases.{json,parquet}` carry a null `target`. Consumers that resolve stored IDs through the alias map should treat `retired` as "gone, do not remap" (for an HTTP layer, the equivalent of `410 Gone`). Update joins and caches to handle the absence of the retired ID after regenerating dataset exports.

The change below corrects an entity-type error rather than asserting that the named media service ceased operations. Historical YAML remains recoverable from Git, but the entity does not belong in a reference dataset of international organizations, treaties, and named country groups.

| Retired ID | Retired in | Reason | Downstream action |
|---|---|---|---|
| `TELESUR` | 3.1.0 (reviewed 2026-09-30) | La Nueva Televisión del Sur (T.V. SUR) C.A. is a Venezuelan commercial company, not an international organization with member states; the seven exported country links did not represent membership. | Remove `TELESUR` from intblock and membership queries, do not resolve it to a different organization, and model verifiable dated shareholder relationships in a separate corporate dataset if needed. |

```sql
SELECT d.*
FROM downstream AS d
LEFT JOIN read_parquet('data/datasets/intblocks_aliases.parquet') AS a
  ON d.intblock_id = a.alias AND a.reason = 'retired'
WHERE a.alias IS NULL;  -- drop rows keyed on retired ids
```

The legal-form basis is the [2014 Venezuelan court decision](https://caracas.tsj.gob.ve/DECISIONES/2014/JUNIO/2258-12-2564-14-164-14.HTML), the operator's [terms of use](https://www.telesurtv.net/terminos-de-uso/), and a [2020 court decision](https://historico.tsj.gob.ve/decisiones/scon/enero/309498-0003-29120-2020-20-0038.HTML) discussing its shareholder book without supplying a reliable current list. See the [scope-taxonomy OpenSpec design](../openspec/changes/complete-intblock-scope-taxonomy/design.md) and the changelog for migration context.
