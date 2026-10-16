# Анализ пробелов Internacia DB на 29 сентября 2026 года

Репозиторий находится в хорошем техническом состоянии: исходные и экспортированные наборы согласованы, все **319 тестов** проходят, валидатор стран сообщает **0 ошибок и 0 предупреждений**, а валидатор intblocks — **0 ошибок и 114 предупреждений**. В текущем срезе находятся 256 страновых записей, 1272 intblocks, 78 blocktypes и 58 767 рёбер членства.

При этом «валидно» не означает «полно и семантически однозначно». У стран почти нет структурных дефектов, но заметно недозаполнены внешние идентификаторы и стабильные атрибуты. У intblocks основные проблемы находятся в трёх местах: классификация `scope_category`, отсутствие дат проверки состава и неполный охват крупных официальных каталогов договоров.

## Реестр стран: новых стран добавлять не нужно

Состав стран уже соответствует принятой политике: 249 текущих ISO 3166-1 записей и семь явно маркированных нестандартных или исторических кодов. Валидатор подтверждает целостность идентификаторов, границ, географических координат, статусов сущностей и provenance. Поэтому задача здесь — не расширять список, а повысить полезность существующих записей для join и entity resolution.

Пустые значения `gini` у 86 из 256 записей не следует считать обычным дефектом. Это ожидаемая разреженность источника, особенно для территорий, микрогосударств и спорных сущностей. Аналогично, отсутствие часовых поясов и столиц у отдельных необитаемых территорий уже корректно обрабатывается правилами исключений.

Наиболее существенные пробелы странового реестра следующие.

1. **Внешние crosswalk-идентификаторы заполнены лишь частично.** `geonames_id` отсутствует у 138 из 256 записей, включая 78 из 194 официальных суверенных государств. `ioc_code` и `fifa_code` имеют почти такое же покрытие, потому что текущий seed-файл содержит только 118 строк. Это снижает ценность набора как центра связывания сущностей, хотя поля уже заявлены как поставленная возможность в `docs/strategy-and-user-needs.md`.

2. **Стабильные страновые атрибуты после миграции из intblocks остаются сильно разреженными.** Не заполнены `writing_systems` у 198 записей, `dvd_region` у 131, `broadcast_systems` у 97, `legal_systems` у 153 и `rail_gauges` у 222. Текущие warn-пороги сознательно допускают эти уровни, поэтому CI не показывает проблему. Для потребителя наличие столбца может создавать ложное ожидание пригодного покрытия.

3. **Несогласована документация по Gini.** В `docs/enrichment.md` заявлен `max_null_rate: 0.33`, тогда как фактический `data/schemas/countries_completeness.yaml` задаёт `0.40`. Фактическая доля пропусков — 33,6%. Документация сейчас описывает порог, который данные уже превышают, но валидатор использует другой порог.

4. **Четыре специальных записи имеют старые годы населения.** Это `AN` — 2009, `XN` — 2012, `XA` — 2016 и `XS` — 2022. Для исторической `XN` это может быть корректно, но для спорных действующих сущностей стоит либо обновить значение, либо явно пояснить ограничение источника. Ещё 34 записи имеют значение населения без года, что разрешено схемой, но снижает сопоставимость.

5. **OpenSpec содержит устаревшую норму о Kosovo.** Текущие данные и публичная документация используют `XK`, но `openspec/specs/countries-entity-model/spec.md` всё ещё требует `KV`. Это не дефект набора данных, однако текущая спецификация противоречит реализованному контракту.

Практическое улучшение — добавить отдельные completeness-правила для crosswalk-полей с корректным знаменателем. Для GeoNames знаменателем могут быть все текущие ISO-сущности, а для IOC и FIFA — только сущности, которым код действительно может быть назначен. Сначала стоит довести GeoNames для 194 суверенных государств до 100%, затем расширить покрытие территорий. Для разреженных стабильных атрибутов лучше публиковать явную метрику покрытия по `entity_type`, а не только высокий общий warn-порог.

## Intblocks: главный долг — семантика, а не синтаксис

Формальная целостность intblocks хорошая. Нет дубликатов `id`, неразрешённых ссылок, ошибок схемы, конфликтов дат, проблем с provenance или рассинхронизации экспортов. Только восемь записей не имеют `includes`, и они проходят проверку как намеренно неприменимые к государственному членству.

Однако потребитель, который фильтрует `scope_category`, может получить неверный результат. Поле уже позиционируется как главный способ отделять IGO, договоры, форумы и референсные группы, поэтому семантическая точность здесь важнее заполненности низкоприоритетных описательных полей.

### Неполная и ошибочная классификация `scope_category`

Всего `scope_category` отсутствует у **192 из 1272** записей, или 15,1%. Из них 114 имеют `status: formal`; именно эти записи образуют все 114 предупреждений валидатора. Пропуски сконцентрированы в `gaspipeline` (25), `acronym` (21), `cultural` (21), `food` (18), `economic` (15), `pta` (14), `project` (13), `customs` (11) и `fund` (10).

Заполненные значения также содержат системную ошибку: **все 25 World Bank grouping records имеют `scope_category: igo`**. В их числе `WLD`, `HIC`, `LIC`, `LMC`, `UMC`, `EAS`, `SAS`, `LAC` и другие статистические группы. По собственной политике проекта это `reference_enumeration`, а не межправительственные организации. Следовательно, стандартный запрос `WHERE scope_category = 'igo'` возвращает ложноположительные результаты.

Есть и более глубокая проблема модели. Все 16 спортивных записей классифицированы как `igo`, как и FIFA, IOC, IATA, ICRC, IUCN, WADA, BIMCO, HUGO и Global Maritime Forum. Эти сущности имеют разную правовую природу: международные ассоциации, федерации, гибридные союзы, гуманитарные организации и многосторонние инициативы. Четырёх текущих значений поля недостаточно, если такие записи должны оставаться в реестре.

Рекомендуется сделать два изменения. Сначала без изменения схемы исправить 25 World Bank групп на `reference_enumeration` и классифицировать 114 формальных пропусков. Затем через OpenSpec разделить **назначение записи как join target** и **правовую природу сущности**. Минимальный вариант — добавить `international_association` и `program_or_network`; более чистый вариант — сохранить `scope_category` для формы набора, а отдельным полем хранить `entity_nature`.

### Свежесть состава не контролируется для четверти реестра

`last_verified` отсутствует у **309 записей**, или 24,3%. Среди них есть UN, WHO, WIPO, IMF, FAO, UNESCO, UNICEF, IMO, ICAO, ITU, INTERPOL, крупные спортивные федерации и многочисленные UN agencies. Для заполненных дат просрочки нет: все они относятся к 2026 году.

Проблема скрыта конфигурацией. Для `last_verified` установлен `max_null_rate: 1.0`, поэтому отсутствие даты никогда не создаёт completeness-warning. Проверка 12-месячного SLA работает только для уже заполненных значений. Следует установить начальный warn-порог около фактической базы — 0,25 — и затем снижать его по волнам до 0,10 и 0,05. Первой волной должны стать формальные записи с большим составом и часто меняющиеся форумы.

### Wikidata gate допускает временные заглушки без срока жизни

`wikidata_id` отсутствует у **170 записей**, или 13,4%, и каждый такой пропуск формально покрыт исключением. Но 118 исключений имеют причину вида `pending enrichment backfill`, а 109 происходят из общего `deep-review audit`. Это не доказательство отсутствия сущности в Wikidata, а незавершённая задача, превращённая в постоянное исключение.

Кроме того, в `wikidata_exclusions.yaml` остались два id уже удалённых attribute-intblocks: `LSBIJURIDICAL` и `SUSPCOU`. Они были перенесены в vocab/migration-артефакты и больше не существуют в intblocks.

Рекомендуется типизировать причины исключения: `no_item_verified`, `maps_to_parent`, `ambiguous`, `pending_backfill`. Только первые три должны удовлетворять постоянному gate. Для `pending_backfill` нужен срок, например 90 дней, после которого CI снова предупреждает. Отдельная проверка должна запрещать исключения для отсутствующих в реестре id.

### Отчёт качества расходится с валидатором

Свежий запуск `scripts/builder.py analyze-quality` сообщает **0 проблем и 100% clean records**, хотя `validate_intblocks.py --json` одновременно возвращает 114 предупреждений о `scope_category`. Это нарушает требование parity в `openspec/specs/intblocks-data-quality/spec.md`, согласно которому правила валидатора должны попадать и в `dataquality/`.

Причина архитектурная: validator и quality analyzer всё ещё используют частично дублированные наборы правил. В активном OpenSpec `refactor-builder-into-package` соответствующая задача прямо оставлена deferred. Это следует исправить как баг: оба CLI должны вызывать один и тот же набор rule functions и различаться только форматом вывода и порогом завершения.

## Подтверждённые отсутствующие записи

Шесть официальных каталогов были сверены с текущими 1272 id, именами и алиасами. Уже документированные проходы UNTC, WTO RTA-IS, WTO PTA, UNCTAD IIA и `.int` повторно не обходились. Новая проверка охватила договоры ВОИС, конвенции HCCH, ключевые конвенции IMO, региональные рыболовные органы FAO, сеть FATF и программу Regional Seas UNEP.

Наиболее заметный пробел — не малоизвестные организации, а глобальные договоры с отдельными официальными реестрами сторон. ВОИС публикует самостоятельный каталог и построчные статусы участников для своих договоров [1]. IMO отдельно выделяет ключевые конвенции и публикует государственный status workbook [8]. HCCH ведёт собственные депозитарные таблицы для каждой конвенции [13].

### Первая волна: добавить в ближайший релиз

Эти записи имеют высокий охват, устойчивые официальные реестры и явно проходят действующую inclusion policy. Предложенные id следует считать рабочими; длинные id без официального акронима требуют отдельной проверки naming policy.

1. **`BERNECOPYRIGHTCONVENTION`** — Berne Convention for the Protection of Literary and Artistic Works, 182 стороны. Это не существующая природоохранная `BERNECONVENTION` [2].
2. **`PARISCONVENTION`** — Paris Convention for the Protection of Industrial Property, 181 сторона. Это не климатическая `PARISAGREEMENT` [3].
3. **`SOLAS`** — International Convention for the Safety of Life at Sea; ключевая конвенция IMO с отдельным глобальным составом [9].
4. **`STCW`** — Convention on Standards of Training, Certification and Watchkeeping for Seafarers; отдельный официальный реестр сторон [10].
5. **`COLREG`** — Convention on the International Regulations for Preventing Collisions at Sea [11].
6. **`PCT`** — Patent Cooperation Treaty, официальный акроним и самостоятельный реестр ВОИС [4].
7. **`MARPOL`** — Convention for the Prevention of Pollution from Ships. Перед добавлением нужно явно решить, как моделировать базовый инструмент и приложения [12].
8. **`APOSTILLE`** — HCCH 1961 Apostille Convention, 130 contracting parties [14].

Для договоров ВОИС нельзя механически копировать все строки реестра: будущие даты вступления в силу и институциональные участники должны быть отфильтрованы по состоянию на дату среза. Для IMO status workbook следует сохранить снимок с датой публикации в provenance. Для HCCH в `includes` должны попадать стороны, для которых EIF уже наступил.

### Вторая волна: высокий приоритет после первой

Эти договоры также хорошо подтверждены, но имеют меньший охват или более узкую прикладную область. Они подходят для второй серии data-only PR после того, как будет закреплён единый шаблон импорта официальных roster.

1. **`MADRIDPROTOCOL`**, **`WCT`** и **`WPPT`** — самостоятельные действующие договоры ВОИС; они не дублируют WIPO, Berne Convention или существующую `PHONOGRAMS` [5] [6] [7].
2. **`HAGUECHILDABDUCTION`**, **`HAGUEADOPTION`**, **`HAGUESERVICE`**, **`HAGUEEVIDENCE`** и **`HAGUECHILDPROTECTION`** — действующие конвенции HCCH с отдельными roster [15] [16] [17] [18].
3. **`FAL`** и **`LL`** — действующие IMO conventions, оставленные за пределами первой восьмёрки только из-за приоритета более универсальных морских инструментов [8].

### Тематический backlog: организации и региональные договоры

Дополнительные каталоги показали, что общий охват зрелых региональных организаций уже неплох. Например, в официальном списке FATF отсутствуют только два из FATF + девяти FSRBs. В каталоге FAO уже покрыта значительная часть наиболее известных fisheries bodies. Это хороший признак: дальнейшее расширение следует вести маленькими тематическими волнами, а не массовым импортом.

Подтверждённый backlog выглядит так.

- **FATF Global Network:** `GABAC` и `MONEYVAL`. Для MONEYVAL нужно аккуратно моделировать Crown Dependencies и другие несуверенные юрисдикции [20] [21] [22].
- **FAO Regional Fishery Bodies:** `BOBPIGO`, `CACFISH`, `BCC`, `FCWC`, `SRFC`, `NACA` [19].
- **UNEP Regional Seas:** `CPPS`, `COBSEA`, `TEHRAN`, `LIMA`, `SPAW`; `NOWPAP` пока отложить из-за расхождения официальных страниц о составе [23] [24] [25] [26] [27] [28].

Перед авторингом каждой записи всё равно требуется повторная проверка `id`, алиасов, даты вступления в силу и состава. Каталог — источник кандидата, но не автоматический источник `includes`.

## Приоритетный план улучшений

Первый этап должен исправить то, что уже влияет на корректность запросов. Он не требует широкого изменения схемы и может быть разбит на небольшие проверяемые PR. Второй этап закрывает недостающие глобальные join targets. Только после этого стоит расширять модель типов сущностей.

### P0 — исправить потребительский контракт

1. Переклассифицировать 25 `wbgroup` из `igo` в `reference_enumeration` и добавить тест, запрещающий `scope_category: igo` для World Bank grouping records.
2. Заполнить `scope_category` для 114 формальных записей и затем изменить предупреждение на CI-gate после очистки backlog.
3. Добавить правило `scope_category` в quality analyzer и устранить расхождение «114 предупреждений против 0 проблем» через общий rule engine.
4. Исправить OpenSpec `KV` → `XK`, заменить `TBD` в Purpose действующих спецификаций и архивировать завершённые изменения. Сейчас `openspec list` показывает 27 неархивированных changes, большинство уже помечены complete.
5. Добавить первую волну из восьми глобальных договоров с официальными roster и записать новые каталоги в `docs/intblock-sources.md`.

### P1 — сделать свежесть и entity linking измеримыми

1. Ввести реальный warn-порог для отсутствующего `last_verified`, начать с 0,25 и уменьшать его после каждой волны обновления.
2. Перепроверить 118 временных Wikidata exclusions, удалить два orphan-id и добавить срок жизни для `pending_backfill`.
3. Завершить GeoNames crosswalk для 78 официальных суверенных государств; затем отдельно определить eligible-наборы для IOC и FIFA.
4. Добавить вторую волну договоров ВОИС, HCCH и IMO. Для каждой записи требовать минимум четыре provenance entries и отдельный источник roster.
5. Разрешить три явно отмеченных «pending maintainer merge» пары в allowlist: `UNASUR`/`USAN`, `COL`/`COMMLEARN`, `ABCANZ`/`ABCZNZ`.

### P2 — улучшить модель и долгосрочное покрытие

1. Подготовить OpenSpec для разделения join-категории и правовой природы сущности. Это устранит ложное обозначение спортивных федераций, частных ассоциаций и гибридных организаций как IGO.
2. Провести тематические catalogue walks FAO RFB, FATF FSRBs и UNEP Regional Seas, сохраняя границы поиска и дату в `docs/intblock-sources.md`.
3. Повысить покрытие `writing_systems`, `legal_systems`, `broadcast_systems` и `rail_gauges` сначала для 249 текущих ISO-кодов. Не добавлять новые социально-экономические поля.
4. Удалить неиспользуемый blocktype `unregionalgroup` либо документировать конкретный будущий набор записей, который его оправдывает.
5. Исправить документацию по Gini и добавить тест согласованности числовых порогов между `docs/enrichment.md` и completeness-конфигурацией.

## Проверка результата аудита

Локальная проверка выполнялась против текущего рабочего дерева. До начала анализа в нём уже были незакоммиченные изменения release workflow, manifest/meta-файлов, DuckDB, dataquality и документации; аудит их не изменял. Созданы только рабочие файлы под `.work/repo-gap-audit/` и этот отчёт.

Повторяемые команды:

```bash
python scripts/validate_countries.py --json
python scripts/validate_intblocks.py --json
.venv/bin/pytest -q
.venv/bin/python scripts/check_generated_artifacts.py
.venv/bin/python scripts/builder.py analyze-quality --output .work/repo-gap-audit/quality-fresh
```

Итог проверок: validators — без ошибок; tests — 319/319; artifact consistency — OK; intblocks validator — 114 предупреждений; fresh quality analyzer — 0 проблем. Последняя пара результатов и есть подтверждённый дефект parity, а не ошибка интерпретации старого отчёта.

## References

[1]: https://www.wipo.int/en/web/treaties "WIPO-Administered Treaties"
[2]: https://www.wipo.int/en/web/treaties/ip/berne "Berne Convention for the Protection of Literary and Artistic Works"
[3]: https://www.wipo.int/en/web/treaties/ip/paris "Paris Convention for the Protection of Industrial Property"
[4]: https://www.wipo.int/en/web/treaties/registration/pct "Patent Cooperation Treaty"
[5]: https://www.wipo.int/en/web/treaties/registration/madrid_protocol "Madrid Protocol"
[6]: https://www.wipo.int/en/web/treaties/ip/wct "WIPO Copyright Treaty"
[7]: https://www.wipo.int/en/web/treaties/ip/wppt "WIPO Performances and Phonograms Treaty"
[8]: https://www.imo.org/en/About/Conventions/Pages/ListOfConventions.aspx "IMO List of Conventions"
[9]: https://www.imo.org/en/about/conventions/pages/international-convention-for-the-safety-of-life-at-sea-(solas),-1974.aspx "International Convention for the Safety of Life at Sea"
[10]: https://www.imo.org/en/about/conventions/pages/international-convention-on-standards-of-training,-certification-and-watchkeeping-for-seafarers-(stcw).aspx "International Convention on Standards of Training, Certification and Watchkeeping for Seafarers"
[11]: https://www.imo.org/en/about/conventions/pages/colreg.aspx "Convention on the International Regulations for Preventing Collisions at Sea"
[12]: https://www.imo.org/en/about/conventions/pages/international-convention-for-the-prevention-of-pollution-from-ships-(marpol).aspx "International Convention for the Prevention of Pollution from Ships"
[13]: https://www.hcch.net/en/instruments/conventions "HCCH Conventions and Other Instruments"
[14]: https://www.hcch.net/en/instruments/conventions/status-table/?cid=41 "HCCH 1961 Apostille Convention Status Table"
[15]: https://www.hcch.net/en/instruments/conventions/status-table/?cid=24 "HCCH 1980 Child Abduction Convention Status Table"
[16]: https://www.hcch.net/en/instruments/conventions/status-table/?cid=69 "HCCH 1993 Adoption Convention Status Table"
[17]: https://www.hcch.net/en/instruments/conventions/status-table/?cid=17 "HCCH 1965 Service Convention Status Table"
[18]: https://www.hcch.net/en/instruments/conventions/status-table/?cid=82 "HCCH 1970 Evidence Convention Status Table"
[19]: https://www.fao.org/fishery/rfb/en "FAO Regional Fishery Bodies"
[20]: https://www.fatf-gafi.org/en/countries/global-network.html "FATF Global Network"
[21]: https://www.fatf-gafi.org/en/countries/global-network/gabac.html "FATF Profile of GABAC"
[22]: https://www.coe.int/en/web/moneyval/moneyval-brief/members "MONEYVAL Members and Territories"
[23]: https://www.unep.org/topics/ocean-seas-and-coasts/regional-seas-programme "UNEP Regional Seas Programme"
[24]: https://www.unep.org/permanent-commission-south-pacific-cpps "Permanent Commission for the South Pacific"
[25]: https://www.unep.org/cobsea/who-we-are "Coordinating Body on the Seas of East Asia"
[26]: https://www.unep.org/tehran-convention "Tehran Convention"
[27]: https://treaties.un.org/Pages/showDetails.aspx?objid=08000002800bca1b "Lima Convention Treaty Record"
[28]: https://www.unep.org/cep/what-we-do/specially-protected-areas-and-wildlife-spaw "SPAW Protocol"
