# План исправления country crosswalk и классификации World Bank groups

Дата фиксации плана: 29 сентября 2026 года.

## 1. Цели и границы

План разделён на два независимых трека. **Трек A** восстанавливает надёжность страновых crosswalk-полей `geonames_id`, `ioc_code`, `fifa_code` и `fips_code`: происхождение каждого значения, полноту по корректному знаменателю, безопасное повторное обновление и защиту от коллизий. **Трек B** исправляет семантически неверную классификацию 25 статистических групп World Bank как межправительственных организаций.

Оба трека восстанавливают уже заявленное поведение, поэтому отдельный OpenSpec proposal для основного исправления не нужен. Текущий `countries-profile` уже требует backfill и field-level provenance для crosswalk, а текущая inclusion policy уже определяет статистические наборы как `reference_enumeration`. Новый proposal потребуется только в будущем, если появится новое экспортируемое поле, например `genc_code`, или будет расширен enum `scope_category`.

В план **не входят** добавление социально-экономических полей, изменение первичных кодов стран, переименование intblock id, пересмотр составов World Bank групп и расширение enum `scope_category`.

## 2. Исходное состояние и подтверждённые дефекты

| Область | Текущее состояние | Целевое состояние |
|---|---:|---:|
| `geonames_id` | 118/256; 116/194 суверенных ISO-государств | 194/194 на первом этапе; затем все применимые ISO-записи |
| `ioc_code` | 118/256 | 100% явно eligible NOC-сущностей, остальные объяснены |
| `fifa_code` | 117/256 | 100% явно eligible FIFA associations, остальные объяснены |
| `fips_code` | 118/256 | существующие значения документированы; completeness gate не вводится |
| Crosswalk provenance | 0 из 471 заполненных назначений имеют field-level provenance | 471/471 плюс provenance для новых значений |
| World Bank groups | 25/25 имеют `scope_category: igo` | 25/25 имеют `reference_enumeration` |
| Защита от регрессии wbgroup | `wbgroup` включён в `ORG_DIRS` генератора | path/blocktype invariant и тест |
| Quality analyzer | не проверяет семантику `scope_category` | использует общее правило с валидатором |

Критический порядок работ для crosswalk: **сначала provenance и проверки, потом расширение покрытия**. Иначе новый backfill увеличит уже существующий разрыв между данными и спецификацией.

## 3. Общие проектные решения

### 3.1. Источник и eligibility — разные понятия

Отсутствие значения не всегда является дефектом. GeoNames привязан к географическим сущностям и должен покрывать почти все текущие ISO-коды. IOC и FIFA присваивают коды не странам вообще, а NOC и футбольным ассоциациям; поэтому общий знаменатель 256 или даже 249 некорректен. FIPS 10-4 отозван и не должен использоваться как современный completeness target.

Для каждого crosswalk-поля нужен собственный набор eligible-кодов и явные исключения. Рекомендуемый файл — `data/schemas/country_crosswalk_exclusions.yaml` со структурой `field → country code → reason, source, reviewed_at`. Допустимые причины следует ограничить каталогом, например `not_a_member`, `split_associations`, `no_authoritative_mapping`, `historical_only`, `non_country_entity`.

### 3.2. Источники данных

1. **GeoNames:** официальный `countryInfo.txt` из GeoNames dump. Файл обновляется ежедневно, содержит ISO-коды и GeoNames id, распространяется под CC BY 4.0. В provenance указывать GeoNames, URL файла и дату извлечения.
2. **IOC:** официальный список NOC и кодов Olympics/IOC. Датированный список Paris 2024 пригоден как проверяемый snapshot, но eligibility следует сверять с актуальным каталогом NOC, а не с общим ISO-списком.
3. **FIFA:** официальный каталог 211 Member Associations. Нельзя выводить FIFA code автоматически из `iso3code`; различия вроде `ALG`, `SUI`, `NED`, `ENG`/`SCO`/`WAL` являются частью контракта.
4. **FIPS:** использовать только как legacy crosswalk. NIST официально отозвал FIPS 10-4 2 сентября 2008 года и указывает GENC как замену. Существующие значения можно подтвердить через GeoNames `countryInfo.txt`, но не устанавливать для поля обязательную полноту.

Для воспроизводимости добавить `data/schemas/country_crosswalk_sources.yaml`: URL, название источника, дата snapshot, лицензия и SHA-256 локального входного файла. Сырые скачанные файлы не обязаны попадать в Git; в репозитории остаются curated seed, metadata и provenance.

### 3.3. Обновления не должны молча перезаписывать значения

`seed_country_crosswalks.py` должен работать в режимах `--check`, `--dry-run` и `--apply`. По умолчанию скрипт не меняет YAML. Если значение источника отличается от заполненного значения, это **conflict**, а не автоматическая замена. Перезапись разрешается только отдельным флагом и должна обновлять provenance.

Вывод скрипта должен содержать числа `added`, `unchanged`, `conflicts`, `not_applicable`, `unresolved`, а опциональный JSON-отчёт — список кодов в каждой категории. Повторный запуск на уже обновлённом дереве обязан давать нулевой diff.

## 4. Трек A — исправление страновых crosswalk

### A1. Зафиксировать контракт и исключения

**Изменяемые файлы:**

- `data/schemas/country_crosswalk_seed.csv`;
- новый `data/schemas/country_crosswalk_sources.yaml`;
- новый `data/schemas/country_crosswalk_exclusions.yaml`;
- `docs/ai-consumers.md` и `docs/data-dictionary.md`.

**Задачи:**

1. Зафиксировать, что `geonames_id`, `ioc_code`, `fifa_code`, `fips_code` являются внешними идентификаторами и уникальны в пределах назначенных значений.
2. Описать знаменатель каждого поля: GeoNames — официальные ISO-сущности; IOC/FIFA — только подтверждённые NOC/MA; FIPS — без completeness target.
3. Запретить объяснение пропуска свободным текстом вне каталога причин.
4. Обозначить `fips_code` как withdrawn/legacy в документации, сохранив поле для обратной совместимости.
5. Не добавлять `genc_code` в рамках этого исправления; это отдельное будущее изменение схемы.

**Критерий приёмки:** для каждого null в eligible-наборе есть либо задача backfill, либо запись исключения; неeligible-записи не ухудшают метрику покрытия.

### A2. Рефакторинг seed-скрипта до изменения данных

**Изменяемые файлы:**

- `scripts/seed_country_crosswalks.py`;
- новые тесты, предпочтительно `tests/test_seed_country_crosswalks.py`;
- при необходимости helper в `internacia_builder/validate/country_rules.py`.

**Задачи:**

1. Убрать встроенный `DEFAULT_SEED` как второй источник истины. Скрипт должен завершаться ошибкой, если curated seed отсутствует или невалиден.
2. Добавить разбор CLI: `--check`, `--dry-run`, `--apply`, `--field`, `--report-json`.
3. Валидировать уникальность `code` и всех непустых внешних идентификаторов.
4. Проверять формат: GeoNames — положительное целое как строка; IOC/FIFA — три заглавные ASCII-буквы; FIPS — две заглавные ASCII-буквы.
5. Добавлять или обновлять отдельную provenance-запись для каждого заполненного поля: `field`, `source`, `url`, `retrieved_at`.
6. Не дублировать provenance при повторном запуске. При том же значении обновление даты возможно только явным режимом refresh.
7. Сохранять хирургическое редактирование YAML и стабильный порядок полей; fallback с полным `yaml.dump` убрать или покрыть snapshot-тестом, чтобы он не создавал массовый форматный diff.
8. При конфликте существующего и нового значения завершать `--check` ненулевым кодом и печатать обе версии.

**Обязательные тесты:**

- новое значение и provenance вставляются вместе;
- заполненное значение без provenance получает provenance;
- совпадающее значение идемпотентно;
- конфликт не перезаписывается;
- повторный запуск не меняет файл;
- неизвестный country code в seed является ошибкой;
- дубли GeoNames/IOC/FIFA/FIPS являются ошибкой;
- значение с неверным форматом отвергается.

### A3. Закрыть уже существующий provenance-долг

Сейчас 118 стран имеют хотя бы один crosswalk, но ни одна из 471 заполненных связей не имеет требуемого field-level provenance. Это нужно исправить отдельным коммитом до добавления новых значений, чтобы review отделял метаданные от расширения покрытия.

**Задачи:**

1. Для 118 существующих `geonames_id` и `fips_code` добавить provenance на GeoNames `countryInfo.txt`; для IOC и FIFA использовать соответствующие официальные источники.
2. Если исходное значение невозможно подтвердить официальным источником, не придумывать provenance: поместить запись в conflict report и исправить либо удалить значение после ручной проверки.
3. Добавить правило `check_crosswalk_provenance(record)` в `country_rules.py`: каждое непустое crosswalk-поле должно иметь хотя бы одну provenance-запись с тем же `field`, непустыми `source`, `url`, `retrieved_at`.
4. Подключить правило и к `validate_countries`, и к `analyze-quality`.
5. На миграционном PR правило можно выпустить как warning; в том же PR после backfill ожидается ноль предупреждений, после чего режим фиксируется как error.

**Критерий приёмки:** 471 из 471 существующих назначений подтверждены provenance; нет orphan provenance, указывающего на пустое поле.

### A4. GeoNames backfill — сначала 194 суверенных государства

Это наиболее однозначная и полезная часть исправления. Маппинг строится по ISO alpha-2 из официального `countryInfo.txt`; имена не используются как ключ.

**Задачи:**

1. Скачать snapshot `countryInfo.txt`, записать дату, URL, лицензию и SHA-256.
2. Сопоставить строки с `data/countries/*.yaml` строго по `code`.
3. Сформировать diff для 78 отсутствующих `geonames_id` среди 194 суверенных государств.
4. Проверить, что каждый id уникален и существует в snapshot.
5. Применить backfill и field-level provenance.
6. Добавить отдельный coverage-check: `sovereign_state + official_iso3166_1` должен иметь `geonames_id` без исключений.

**Критерий приёмки:** `194/194` суверенных ISO-государств имеют валидный и уникальный `geonames_id`; validator, quality analyzer и idempotence-test проходят.

### A5. GeoNames для территорий и специальных сущностей

После суверенных государств расширить покрытие на остальные 55 текущих ISO-сущностей. Этот этап отделён, потому что GeoNames и ISO могут по-разному моделировать территории, особые административные районы и спорные сущности.

**Задачи:**

1. Сформировать список всех `official_iso3166_1` без GeoNames после A4.
2. Автоматически принять только прямые alpha-2 совпадения.
3. Для каждого отсутствующего или неоднозначного соответствия сделать ручную запись в exclusions с официальной ссылкой и датой проверки.
4. Для `user_assigned`, `obsolete` и supranational записей не требовать GeoNames id, но разрешить подтверждённые значения, например для Kosovo.

**Критерий приёмки:** все 249 официальных ISO-записей либо имеют GeoNames id, либо покрыты узким документированным исключением; общий null-rate больше не используется вместо eligibility-aware метрики.

### A6. IOC и FIFA как отдельные source-specific backfill

IOC и FIFA нельзя смешивать с GeoNames в одном автоматическом предположении. Они требуют собственных eligible-наборов и ручной обработки исключений.

**Задачи IOC:**

1. Собрать актуальный официальный NOC roster и codes snapshot.
2. Сопоставлять сначала по подтверждённому названию/странице NOC, затем фиксировать country code вручную в curated seed.
3. Учесть территории и особые коды: `HKG`, `TPE`, `KOS`, `PUR`, `BER`, `CAY`, `IVB`, `ISV` и аналогичные.
4. Не трактовать отсутствие NOC как дефект ISO-записи.

**Задачи FIFA:**

1. Взять официальный roster 211 Member Associations.
2. Не выводить код из ISO3. Все коды должны быть получены из официального FIFA snapshot или подтверждённой страницы ассоциации.
3. Для `GB` зафиксировать отсутствие единого FIFA code причиной `split_associations`, поскольку FIFA использует отдельные associations England, Scotland, Wales и Northern Ireland.
4. Территории с собственной ассоциацией связывать с существующей country record, если она есть; FIFA-сущности без country record не создавать автоматически.

**Критерий приёмки:** 100% eligible NOC и FIFA associations, которые имеют соответствующую запись в `countries`, получили код или документированное исключение; коды уникальны и имеют provenance.

### A7. FIPS: стабилизация legacy-поля

1. Добавить в документацию предупреждение об отзыве FIPS 10-4 и ссылку на NIST.
2. Существующие значения подтвердить источником и provenance.
3. Дополнительный backfill разрешён только из зафиксированного legacy snapshot; не смешивать FIPS с GENC.
4. Не добавлять error/warn completeness gate для `fips_code`.
5. Рассмотрение `genc_code` вынести в отдельный OpenSpec proposal с оценкой потребительского спроса.

## 5. Трек B — переклассификация World Bank groups

### B1. Исправить 25 исходных YAML

Во всех файлах `data/intblocks/wbgroup/*.yaml` изменить только:

```yaml
scope_category: igo
```

на:

```yaml
scope_category: reference_enumeration
```

Затронутые id: `EAS`, `ECA`, `ECS`, `EMU`, `EUU`, `HIC`, `HPC`, `LAC`, `LCN`, `LDC`, `LIC`, `LMC`, `LMY`, `MEA`, `MIC`, `MNA`, `NAC`, `NOC`, `OEC`, `OED`, `SAS`, `SSA`, `SSF`, `UMC`, `WLD`.

Не менять `id`, `blocktype`, `status`, `includes`, `name`, provenance и даты. `EUU` и `OED` остаются именно World Bank classification sets, а не дубликатами канонических `EU` и `OECD`.

**Критерий приёмки:** запрос к исходным YAML и DuckDB возвращает 25 `wbgroup` и ноль `scope_category = 'igo'` среди них.

### B2. Устранить первопричину в label-скрипте

**Файл:** `scripts/label_scope_category.py`.

1. Удалить `wbgroup` из `ORG_DIRS`.
2. Добавить `wbgroup` в reference-набор либо реализовать более явное правило: если directory или `blocktype` равен `wbgroup`, вернуть `reference_enumeration` до организационных эвристик.
3. Сделать blocktype-based правило приоритетнее имени директории, чтобы перемещение файла не меняло семантику.
4. Добавить unit-тесты для `wbgroup`, обычной IGO и treaty body.
5. Запустить скрипт после ручной правки и подтвердить нулевой diff.

### B3. Добавить общий семантический invariant

Сейчас `validate_scope_category` находится только в `internacia_builder/validate/intblocks.py`, тогда как `intblock_rules.py` заявлен как общий слой между validator и quality analyzer. Правило нужно перенести в общий слой.

Рекомендуемый контракт:

```python
check_intblock_scope_category(record, rel_path) -> list[issue]
```

Он должен проверять:

1. значение входит в допустимый enum;
2. formal record без категории получает существующее предупреждение;
3. запись с `wbgroup` в `blocktype` обязана иметь `reference_enumeration`;
4. `reference_enumeration` не превращается автоматически в IGO только из-за `status: formal`.

Семантическое нарушение `wbgroup → igo` после исправления данных следует считать **error**, а отсутствие категории у других formal records пока остаётся warning. Один checker должен вызываться из `validate_intblocks.py` и из per-record цикла `scripts/builder.py analyze-quality`.

**Обязательные тесты:**

- wbgroup + `igo` возвращает `SCOPE_CATEGORY_SEMANTIC_MISMATCH`;
- wbgroup + `reference_enumeration` проходит;
- unknown enum по-прежнему обнаруживается;
- formal record без категории по-прежнему предупреждает;
- quality analyzer видит тот же semantic mismatch, что и validator.

### B4. Уточнить документацию и имя blocktype

В `docs/ai-consumers.md` и `docs/intblock-inclusion-policy.md` добавить прямое правило: World Bank region/income/lending aggregates — `reference_enumeration`; организации World Bank Group, например `WB` и `IBRD`, — `igo`.

Отдельно рекомендуется изменить display name blocktype `wbgroup` с **World Bank Group** на **World Bank classification group** во всех переводах. ID `wbgroup` остаётся неизменным, поэтому это не ломает join. Если изменение переводов сочтут избыточным для исправляющего PR, вынести его в следующий documentation-only PR.

### B5. Пересобрать артефакты и описать изменение поведения

После исправления YAML пересобрать Parquet, DuckDB, manifests и quality reports штатным builder. Схема не меняется, поэтому `schema_hash` должен остаться прежним; изменятся data/content hashes.

В CHANGELOG отметить ожидаемое изменение: запрос

```sql
SELECT * FROM intblocks WHERE scope_category = 'igo';
```

станет короче на 25 статистических наборов, а `reference_enumeration` вырастет на 25. Это исправление точности, а не удаление данных. Таблица `memberships` и составы групп не должны измениться.

## 6. Рекомендуемое разбиение на PR

| PR | Содержание | Размер | Зависимость |
|---|---|---:|---|
| **PR-B1** | 25 wbgroup YAML, исправление label script, общий invariant, тесты, rebuild | M | независим |
| **PR-A1** | источники/exclusions, безопасный CLI seed-скрипта, unit tests | M | независим |
| **PR-A2** | provenance для 471 существующих назначений, validator + analyzer rule | M | после A1 |
| **PR-A3** | GeoNames backfill 78 суверенных государств, coverage gate | M | после A2 |
| **PR-A4** | GeoNames для остальных ISO territories и exclusions | M | после A3 |
| **PR-A5** | IOC и FIFA eligible backfill, exceptions, docs | L | после A2; можно параллельно A3/A4 |
| **PR-A6** | FIPS legacy docs/provenance и решение по будущему GENC proposal | S | после A2 |

PR-B1 лучше слить первым: он небольшой, устраняет неверные результаты запросов и не зависит от внешних snapshot. Crosswalk-работу не следует объединять в один массовый PR: provenance, GeoNames и спортивные коды имеют разные источники и разные review-регрессии.

## 7. Проверки для каждого PR

Минимальный набор:

```bash
python scripts/validate_countries.py --json
python scripts/validate_intblocks.py --json
.venv/bin/pytest -q
.venv/bin/python scripts/check_generated_artifacts.py
.venv/bin/python scripts/builder.py analyze-quality --output .work/remediation-quality
```

Дополнительные проверки crosswalk:

```sql
-- Уникальность GeoNames id
SELECT geonames_id, COUNT(*)
FROM countries
WHERE geonames_id IS NOT NULL
GROUP BY geonames_id
HAVING COUNT(*) > 1;

-- Покрытие суверенных ISO-государств
SELECT COUNT(*) FILTER (WHERE geonames_id IS NULL) AS missing
FROM countries
WHERE code_status = 'official_iso3166_1'
  AND entity_type = 'sovereign_state';
```

Дополнительные проверки wbgroup:

```sql
SELECT id, scope_category
FROM intblocks
WHERE list_contains(blocktype, 'wbgroup')
  AND scope_category != 'reference_enumeration';

SELECT COUNT(*)
FROM intblocks
WHERE list_contains(blocktype, 'wbgroup');
```

Ожидаемые результаты: первый запрос возвращает 0 строк, второй — 25.

## 8. Rollback и риски

Оба трека не меняют схему, поэтому rollback — revert data/code commit и штатная пересборка артефактов. Миграционный JSON не требуется; `schema_hash` не должен меняться.

Основные риски crosswalk: ошибочное предположение, что IOC/FIFA равны ISO3; коллизии территорий; неподтверждённое происхождение текущих значений; массовое переформатирование YAML; недетерминированное обновление внешнего snapshot. Они закрываются раздельными eligibility-наборами, conflict-mode, field-level provenance, SHA-256 snapshot и idempotence tests.

Основной риск wbgroup — изменение результатов потребительского запроса по IGO. Это намеренное исправление. Его следует явно отметить в CHANGELOG и защитить тестом, а не сохранять неверную классификацию ради стабильности количества строк.

## 9. Definition of Done

Работа завершена, когда одновременно выполнены условия:

1. 25 World Bank classification groups имеют `reference_enumeration`; генератор и общий validator не позволяют вернуть `igo`.
2. Validator и quality analyzer одинаково обнаруживают semantic mismatch.
3. Каждое заполненное crosswalk-поле имеет field-level provenance.
4. Все 194 суверенных ISO-государства имеют уникальный `geonames_id`.
5. Остальные ISO-сущности, IOC NOC и FIFA associations оцениваются по отдельным eligible-наборам; пропуски объяснены машинно-читаемыми исключениями.
6. `fips_code` явно документирован как legacy и не используется как текущий completeness gate.
7. Seed-скрипт безопасен, детерминирован и идемпотентен.
8. Все validators, tests, documented queries и artifact-consistency проверки проходят.
9. `schema_hash` остаётся неизменным, data hashes пересобраны, изменение поведения записано в CHANGELOG.

## Официальные источники

- GeoNames export и лицензия: https://www.geonames.org/export/
- GeoNames dump format и CC BY 4.0: https://download.geonames.org/export/dump/readme.txt
- Официальный Olympics/IOC список NOC-кодов: https://www.olympics.com/en/news/paris-2024-olympics-full-list-ioc-national-olympic-committee-codes
- FIFA Member Associations: https://inside.fifa.com/associations
- NIST о выводе FIPS 10-4 и замене на GENC: https://www.nist.gov/document/replacement-standards-withdrawn-fips-geographic-codes
