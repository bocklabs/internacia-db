## REMOVED Requirements

### Requirement: Kosovo user-assigned status
**Reason**: Kosovo moved from `KV` to `XK` (the code used by the EU, the World Bank and most data providers); `KV` no longer remains in the dataset.
**Migration**: Look up retired codes in `countries_aliases.json` (`KV` → `XK`, `KSV` → `XKX`).

## ADDED Requirements

### Requirement: Kosovo code XK

Record `XK` SHALL have `entity_type: disputed_territory`, `code_status: user_assigned`, and `recognition_status` indicating disputed or partially recognized status. The retired alpha-2 code `KV` and alpha-3 code `KSV` SHALL appear in `countries_aliases.json` mapping to `XK` and `XKX` respectively.

#### Scenario: XK is the primary Kosovo code

- **WHEN** a consumer loads `data/countries/XK.yaml` or queries countries by `code = 'XK'`
- **THEN** the Kosovo record is returned with complete profile fields

#### Scenario: Legacy KV resolves via alias

- **WHEN** a consumer looks up country code `KV` in `countries_aliases.json`
- **THEN** the alias resolves to `XK`
