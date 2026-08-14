# KON-MATRIX — Уровень L3 (Целевой)

**Согласно оценочной матрице KON-MATRIX v2.0**

L3 — это ориентир для команд, стремящихся к максимальной подтверждаемой надёжности и готовности к самому строгому аудиту (SOC 2, ISO 27001, независимый pen-test).

---

## Что даёт L3

| Кон | L3 даёт бизнесу |
|-----|-----------------|
| **Целостность** | Доказуемая цепочка поставки: от исходного кода до продакшена без подмены артефактов |
| **Чистота** | Независимо подтверждённая безопасность: SBOM, pen-test, аудит supply chain |
| **Развитие** | Обновления без простоя: canary, blue-green, MTTR < 5 мин |
| **Прозрачность** | Полный аудит-след: WORM-логи, экспорт данных по запросу, real-time дашборды |

---

## Требования для внедрения

### Инструменты (Фаза 1 — готово)

| Инструмент | Назначение |
|------------|------------|
| [tools/scanner-l3.py](../../tools/scanner-l3.py) | Автоматическая проверка всех 4 Конов L3 |
| [tools/generate-sbom.py](../../tools/generate-sbom.py) | Генерация CycloneDX SBOM из pyproject.toml |

### Инструменты (Фаза 2 — в разработке)

| Инструмент | Назначение |
|------------|------------|
| `tools/verify-slsa.py` | Верификация SLSA-аттестатов |
| `tools/worm-logger.py` | Неизменяемое WORM-хранилище audit log |
| `docs/l3/reproducible-builds.md` | Гайд по воспроизводимым сборкам |
| `docs/l3/zero-downtime-deployment.md` | Гайд по zero-downtime deployment |

### Инструменты (Фаза 3 — планируется)

| Инструмент | Назначение |
|------------|------------|
| `tools/export-api.py` | REST API экспорта артефактов |
| `docs/l3/SOC2-preparation.md` | Маппинг L3 → SOC 2 CC-критерии |
| `docs/l3/ISO27001-preparation.md` | Маппинг L3 → ISO 27001 контроли |
| `docs/l3/independent-audit.md` | Подготовка к независимому аудиту |

---

## Пошаговый гайд: переход с L2 на L3

### Шаг 1 — Убедитесь, что L2 пройден

```bash
python tools/scanner-l2.py
```

L2 должен быть зелёным: подписанные коммиты, Dependabot, ADR, метрики.

### Шаг 2 — Сгенерируйте SBOM (PUR-L3)

```bash
python tools/generate-sbom.py
python tools/scanner-l3.py   # PUR-L3 → PASS
```

### Шаг 3 — Настройте SLSA (INT-L3, Фаза 2)

1. Добавьте workflow `.github/workflows/slsa-verification.yml`
2. Генерируйте provenance attestation при каждом релизе
3. Задокументируйте reproducible builds в `docs/l3/reproducible-builds.md`

### Шаг 4 — Zero-downtime (EVO-L3, Фаза 2)

1. Опишите стратегию blue-green / canary в `docs/l3/zero-downtime-deployment.md`
2. Добавьте health checks и rollback runbook
3. Настройте метрики MTTR

### Шаг 5 — WORM + Export API (TRA-L3, Фазы 2–3)

1. Внедрите `tools/worm-logger.py` для audit log
2. Подключите CI workflow `audit-log.yml`
3. Разверните `tools/export-api.py` с endpoints `/passport`, `/metrics`, `/audit-log`, `/sbom`

### Шаг 6 — Финальная верификация

```bash
python tools/scanner-l3.py
# Цель: 4/4 PASS
```

Обновите [L3-PASSPORT.md](../passport/L3-PASSPORT.md) и передайте аудиторам.

---

## ROI от внедрения L3

| Выгода | Описание |
|--------|----------|
| **Снижение рисков supply chain** | SLSA + SBOM позволяют быстро реагировать на CVE (Log4Shell-style) |
| **Готовность к аудиту** | SOC 2 / ISO 27001 — артефакты L3 покрывают 60–80% типовых запросов аудиторов |
| **Zero-downtime** | Canary + rollback снижают потери от неудачных деплоев |
| **Доверие клиентов** | KON-MATRIX Passport L3 — публичное доказательство зрелости |
| **Соответствие регуляторам** | WORM-логи и export API закрывают требования GDPR «право на переносимость» |

---

## Быстрые команды

```bash
# Проверка L3
python tools/scanner-l3.py

# Генерация SBOM
python tools/generate-sbom.py --output sbom/sbom.cyclonedx.json

# Просмотр Passport
cat docs/passport/L3-PASSPORT.md
```

---

## Связанные документы

- [L3 — Целевой уровень (критерии)](../levels/L3-ideal.md)
- [Matrix Core — полная таблица 12 ячеек](../matrix-core.md)
- [L3 Passport (шаблон)](../passport/L3-PASSPORT.md)
- [L2 Passport](../passport/L2-PASSPORT.md)

---

> L3 — не обязательный минимум, а стратегическая цель. Начните с Фазы 1 (SBOM + scanner), двигайтесь итеративно.
