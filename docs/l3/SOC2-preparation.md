# Подготовка к SOC 2 через KON-MATRIX L3

KON-MATRIX L3 покрывает значительную часть критериев SOC 2 Trust Services Criteria (TSC). Этот документ показывает маппинг.

## Маппинг KON-MATRIX на SOC 2 TSC

### CC6: Логический и физический доступ
- **KON-MATRIX INT-L2/L3:** Подписанные коммиты, Branch Protection, SLSA.
- **Доказательство:** `L3-PASSPORT.md` (секция Целостность).

### CC7: Системные операции
- **KON-MATRIX TRA-L3:** WORM-логи, мониторинг, DAST-сканирование (OWASP ZAP).
- **Доказательство:** `audit-logs/worm-chain.jsonl`, отчёты ZAP в GitHub Security.

### CC8: Управление изменениями
- **KON-MATRIX EVO-L2/L3:** ADR, SemVer, Zero-downtime deployment, Reproducible builds.
- **Доказательство:** `docs/adr/`, `CHANGELOG.md`, `docs/l3/zero-downtime-deployment.md`.

### CC9: Управление рисками
- **KON-MATRIX PUR-L2/L3:** Dependabot (CVE), SBOM, Pen-test.
- **Доказательство:** `sbom/sbom.cyclonedx.json`, Dependabot alerts.

## Как использовать KON-MATRIX для SOC 2 аудита

1. Пройдите KON-MATRIX L3 самоаудит (`python3 tools/scanner-l3.py`).
2. Сформируйте `audit-export/manifest.json` через `export-audit-bundle.py`.
3. Предоставьте аудитору CPA этот пакет как доказательство технической готовности.
4. Аудитор SOC 2 проверит организационные контроли (политики, обучение), которые KON-MATRIX не покрывает, но техническая часть будет закрыта.

## Ограничения

KON-MATRIX **не заменяет** аттестацию SOC 2. Он закрывает технические контроли, но не организационные (HR, физические офисы, юридические договоры).
