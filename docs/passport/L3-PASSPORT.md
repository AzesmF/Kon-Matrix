# KON-MATRIX PASSPORT — Уровень L3

**Проект:** Kon-Matrix  
**Уровень верификации:** L3 (Целевой)  
**Дата выдачи:** 14.08.2026  
**Верифицировал:** Павел (AzemF)  

**Статусы:**
- L1: [L1-PASSPORT.md](./L1-PASSPORT.md) ✅
- L2: [L2-PASSPORT.md](./L2-PASSPORT.md) ✅
- L3: 🔄 Фаза 1 и 2 завершены. Фаза 3 (API, Pen-test, Diffoscope) в планировании.

---

## Артефакты L3

### 1. Целостность (INT-L3) — Сквозная верификация сборок

| Требование | Артефакт | Статус |
|------------|----------|--------|
| Reproducible builds | [docs/l3/reproducible-builds.md](../l3/reproducible-builds.md) | ✅ Фаза 2 |
| SLSA Level 1–2 | [.github/workflows/slsa-verification.yml](../../.github/workflows/slsa-verification.yml) | ✅ Фаза 2 |
| SLSA-аттестат | [.slsa/provenance.json](../../.slsa/provenance.json) | ✅ Фаза 2 |
| Верификация SLSA | [tools/verify-slsa.py](../../tools/verify-slsa.py) | ✅ Фаза 2 |
| Diffoscope | Отчёт сравнения бинарников | ⏳ Фаза 3 |
| Подписанные релизы | Git tag + GitHub Release | ✅ (Начато в L2) |

**Инструмент проверки:** `python3 tools/scanner-l3.py` → INT-L3

---

### 2. Чистота (PUR-L3) — Независимый аудит безопасности

| Требование | Артефакт | Статус |
|------------|----------|--------|
| SBOM (CycloneDX) | [sbom/sbom.cyclonedx.json](../../sbom/sbom.cyclonedx.json) | ✅ Фаза 1 |
| Генератор SBOM | [tools/generate-sbom.py](../../tools/generate-sbom.py) | ✅ Фаза 1 |
| CI генерации SBOM | [.github/workflows/sbom-generation.yml](../../.github/workflows/sbom-generation.yml) | ✅ Фаза 2 |
| OWASP ZAP pen-test | Отчёт `security/zap-report.json` | ⏳ Фаза 3 |
| Внешний аудит | [docs/l3/independent-audit.md](../l3/independent-audit.md) | ⏳ Фаза 3 |

**Инструмент проверки:** `python3 tools/scanner-l3.py` → PUR-L3

---

### 3. Развитие (EVO-L3) — Бесшовная эволюция

| Требование | Артефакт | Статус |
|------------|----------|--------|
| Zero-downtime deployment | [docs/l3/zero-downtime-deployment.md](../l3/zero-downtime-deployment.md) | ✅ Фаза 2 |
| Blue-green / Canary | Стратегия в документации | ✅ Фаза 2 |
| Rollback процедуры | Runbook в docs/l3/ | ✅ Фаза 2 |
| MTTR < 5 мин | [tools/metrics-l2.py](../../tools/metrics-l2.py) → L3 метрики | ⏳ Фаза 3 |
| Health checks | Конфигурация deployment | ✅ Фаза 2 |

**Инструмент проверки:** `python3 tools/scanner-l3.py` → EVO-L3

---

### 4. Прозрачность (TRA-L3) — Полный аудит-лог и экспорт

| Требование | Артефакт | Статус |
|------------|----------|--------|
| WORM-хранилище логов | [tools/worm-logger.py](../../tools/worm-logger.py) | ✅ Фаза 2 |
| Audit log CI | [.github/workflows/audit-log.yml](../../.github/workflows/audit-log.yml) | ✅ Фаза 2 |
| API экспорта | [tools/export-api.py](../../tools/export-api.py) | ⏳ Фаза 3 |
| Endpoints | `/passport`, `/metrics`, `/audit-log`, `/sbom` | ⏳ Фаза 3 |
| External monitoring | Интеграция с дашбордами | ⏳ Фаза 3 |

**Инструмент проверки:** `python3 tools/scanner-l2.py` / `worm-logger.py verify` → TRA-L3

---

## Чек-лист для аудиторов

- [x] **INT-L3:** Предоставлен SLSA Provenance attestation (Level ≥ 1)
- [x] **PUR-L3:** Предоставлен актуальный SBOM в формате CycloneDX
- [x] **EVO-L3:** Описана стратегия zero-downtime (blue-green / canary / rollback)
- [x] **TRA-L3:** Продемонстрирована неизменяемость audit log (WORM hash chain)
- [ ] **PUR-L3:** Отчёт pen-test или внешнего аудита без критических замечаний (Фаза 3)
- [ ] **TRA-L3:** Экспорт данных через API (Фаза 3)

---

## Доказательства соответствия

```bash
# Проверка WORM-лога
python3 tools/worm-logger.py verify

# Верификация SLSA
python3 tools/verify-slsa.py

# Ожидаемый результат (после завершения всех фаз):
# INT-L3  ✅  PASS
# PUR-L3  ✅  PASS
# EVO-L3  ✅  PASS
# TRA-L3  ✅  PASS
# Итог: PASS — все 4 критерия L3 выполнены (4/4)
```

---

## Ссылки

- **Репозиторий:** https://github.com/AzesmF/Kon-Matrix
- **L1 Passport:** [L1-PASSPORT.md](./L1-PASSPORT.md)
- **L2 Passport:** [L2-PASSPORT.md](./L2-PASSPORT.md)
- **L3 Overview:** [docs/l3/README.md](../l3/README.md)
- **Matrix Core:** [docs/matrix-core.md](../matrix-core.md)

---

*Этот Passport актуализирован 14.08.2026. Фазы 1 и 2 реализованы. Фаза 3 находится в стадии проектирования.*
