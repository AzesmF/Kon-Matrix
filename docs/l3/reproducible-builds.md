# Reproducible Builds — KON-MATRIX L3

**Кон:** INT-L3 (Целостность) — сквозная верификация сборок  
**Цель:** гарантировать, что артефакт в продакшене побитово совпадает с результатом воспроизводимой сборки из исходников.

---

## Принципы

1. **Детерминизм** — одинаковый вход (исходники + зависимости + окружение) → одинаковый выход (хэш артефакта).
2. **Изоляция** — сборка выполняется в контролируемом CI-окружении, а не на машине разработчика.
3. **Аттестация** — каждая сборка сопровождается SLSA Provenance attestation.
4. **Верификация** — хэш артефакта сравнивается с записью в SBOM и SLSA materials.

---

## Настройка изолированного окружения

### Python-проекты (Kon-Matrix)

```bash
# Фиксация версии Python
python3 --version   # >= 3.10

# Генерация SBOM (фиксирует состав компонентов)
python tools/generate-sbom.py

# Верификация контрольных сумм исходников
python tools/scanner-l1.py
```

### CI/CD (GitHub Actions)

Workflow `.github/workflows/slsa-verification.yml`:
- запускается при push тега `v*` и вручную (`workflow_dispatch`);
- генерирует SLSA Provenance attestation;
- сохраняет артефакт в `.slsa/provenance.json`;
- запускает `python tools/verify-slsa.py`.

---

## Фиксация зависимостей

| Механизм | Файл | Назначение |
|----------|------|------------|
| PEP 621 | `pyproject.toml` | Декларация прямых зависимостей |
| SBOM | `sbom/sbom.cyclonedx.json` | Машиночитаемый bill of materials |
| Lockfile | `requirements-lock.txt` _(опционально)_ | Pin транзитивных зависимостей |
| SHA256SUMS | `SHA256SUMS` | Контрольные суммы исходных файлов |

---

## Детерминированные сборки

### Шаги для воспроизводимой сборки

1. Checkout конкретного git commit (не floating branch).
2. Установить фиксированную версию Python (`actions/setup-python@v7` с `python-version: "3.11"`).
3. Установить зависимости из lockfile / SBOM.
4. Собрать артефакт с `SOURCE_DATE_EPOCH=0` (для детерминизма timestamps).
5. Вычислить SHA-256 артефакта.
6. Сгенерировать SLSA attestation с materials = git commit + SBOM hash.

### Пример (локально)

```bash
export SOURCE_DATE_EPOCH=0
git archive HEAD | sha256sum
python tools/generate-sbom.py
python tools/verify-slsa.py
```

---

## SLSA Level 1–2

| Level | Требование | Реализация в Kon-Matrix |
|-------|------------|-------------------------|
| **L1** | Provenance exists | `.slsa/provenance.json` + `verify-slsa.py` |
| **L2** | Hosted build service | GitHub Actions workflow + builder.id |
| **L3** | Hardened builds | _(планируется)_ |

### Верификация SLSA

```bash
python tools/verify-slsa.py
python tools/verify-slsa.py --min-level 2
```

---

## Верификация через Diffoscope

[Diffoscope](https://diffoscope.org/) сравнивает два бинарных артефакта и показывает побитовые различия.

```bash
# Установка (Debian/Ubuntu)
sudo apt-get install diffoscope

# Сравнение двух сборок одного commit
diffoscope build-a/artifact.tar.gz build-b/artifact.tar.gz
```

**Интерпретация:**
- Пустой diff → сборки воспроизводимы ✅
- Diff в timestamps/metadata → настроить `SOURCE_DATE_EPOCH`
- Diff в содержимом → проверить floating dependencies

---

## Подписанные теги и релизы

```bash
# Создание подписанного тега
git tag -s v0.3.0 -m "Release v0.3.0 — L3 Phase 2"
git push origin v0.3.0

# GitHub Release автоматически запускает slsa-verification.yml
```

---

## Чек-лист INT-L3

- [ ] SBOM актуален (`python tools/generate-sbom.py`)
- [ ] SLSA attestation сгенерирован (`.slsa/provenance.json`)
- [ ] `python tools/verify-slsa.py` → PASS
- [ ] `python tools/scanner-l3.py` → INT-L3 PASS
- [ ] Релизный тег подписан
- [ ] Diffoscope diff пуст для двух CI-сборок одного commit

---

## Связанные документы

- [L3 Overview](./README.md)
- [L3 Passport](../passport/L3-PASSPORT.md)
- [Zero-downtime Deployment](./zero-downtime-deployment.md)
- [tools/verify-slsa.py](../../tools/verify-slsa.py)
