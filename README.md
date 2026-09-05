<img src="assets/images/logo.svg" alt="KON-MATRIX" width="200">

**Статус:** ✅ [L3 Verified](docs/passport/L3-PASSPORT.md) | [CI/CD](https://github.com/AzesmF/Kon-Matrix/actions) | [Dependabot](https://github.com/AzesmF/Kon-Matrix/security/dependabot)

**Методология оценки зрелости IT-систем и процессов разработки**

[![Лицензия: Field-CoCreation](https://img.shields.io/badge/License-Field--CoCreation-blue)](./LICENSE)

---

## Что это?

KON-MATRIX — это методология и набор инструментов для оценки зрелости процессов разработки и инфраструктуры IT-проектов.

Методология построена как подготовительный этап к международным стандартам — **ISO 27001:2022**, **SOC 2** и **OWASP ASVS 5.0**. В отличие от них, KON-MATRIX не требует внешнего аудитора для старта: она даёт инженеру конкретные чек-листы и автоматизированные скрипты, которые закрывают технические контроли стандартов *до* прихода аудитора.

В основе — матрица 4×3: четыре принципа (Кона) и три уровня зрелости. Каждый уровень подтверждается артефактами, которые можно проверить скриптом, а не декларацией.

> Маппинг на SOC 2 и ISO 27001: [docs/l3/SOC2-preparation.md](./docs/l3/SOC2-preparation.md) · [docs/l3/ISO27001-preparation.md](./docs/l3/ISO27001-preparation.md)

---

## Как устроена матрица

| <img src="assets/images/integrity.svg" width="20" alt=""> Целостность | <img src="assets/images/purity.svg" width="20" alt=""> Чистота | <img src="assets/images/evolution.svg" width="20" alt=""> Развитие | <img src="assets/images/transparency.svg" width="20" alt=""> Прозрачность |
|---|---|---|---|
| **L1 Базовый** | Контрольные суммы артефактов | Документированный состав системы | Журнал изменений (SemVer) | Структурированные логи |
| **L2 Продвинутый** | Подписанные коммиты (Verified) | Мониторинг CVE (Dependabot) | Архив архитектурных решений (ADR) | Дашборды метрик репозитория |
| **L3 Целевой** | SLSA + reproducible builds | SBOM (CycloneDX) + DAST (OWASP ZAP) | Zero-downtime + MTTR < 5 мин | WORM audit log + экспорт для аудитора |

> Полная таблица критериев, доказательств и методов проверки: [docs/matrix-core.md](./docs/matrix-core.md)

---

## Кому это нужно

- **Командам разработки** — чтобы выстроить инженерную культуру и подготовиться к внешнему аудиту без сюрпризов.
- **Техническим руководителям** — чтобы иметь измеримые критерии зрелости процессов, а не субъективные оценки.
- **Аудиторам** — чтобы получить машиночитаемый пакет доказательств (паспорт зрелости, SBOM, WORM-логи) вместо ручного сбора артефактов.

---

## Быстрый старт

1. Изучите [ядро методологии](./docs/matrix-core.md) — таблицу всех 12 ячеек.
2. Проверьте свой проект: `python3 tools/scanner-l1.py` (L1) → `python3 tools/scanner-l2.py` (L2) → `python3 tools/scanner-l3.py` (L3).
3. Для подготовки к стандартам — см. [гайды для аудиторов](./docs/l3/).
4. Для внедрения в свой проект — см. [примеры адаптации](./docs/examples/).

---

## L3 Features

Целевой уровень (L3) обеспечивает сквозную верифицируемость, независимый аудит и полную прозрачность:

| Кон | L3 инструмент / артефакт | Команда |
|-----|--------------------------|---------|
| Целостность | SLSA attestation, reproducible builds (Diffoscope) | `python3 tools/scanner-l3.py` |
| Чистота | CycloneDX SBOM + OWASP ZAP DAST | `python3 tools/generate-sbom.py` |
| Развитие | Zero-downtime deployment guide | см. [docs/l3/](./docs/l3/) |
| Прозрачность | WORM audit log + экспорт пакета аудитору | `python3 tools/export-audit-bundle.py` |

Подробнее: [docs/l3/README.md](./docs/l3/README.md) · [L3-PASSPORT.md](./docs/passport/L3-PASSPORT.md)

---

## Структура репозитория

<pre>
Kon-Matrix/
├── <a href="./README.md">README.md</a>
├── <a href="./LICENSE">LICENSE</a>
├── <a href="./CONTRIBUTING.md">CONTRIBUTING.md</a>
├── <a href="./ROADMAP.md">ROADMAP.md</a>
├── <a href="./CHANGELOG.md">CHANGELOG.md</a>
├── <a href="./SHA256SUMS">SHA256SUMS</a>
├── <a href="./pyproject.toml">pyproject.toml</a>
├── .github/
│   └── workflows/
│       ├── <a href="./.github/workflows/kon-matrix-l1-check.yml">kon-matrix-l1-check.yml</a>
│       ├── <a href="./.github/workflows/auto-changelog.yml">auto-changelog.yml</a>
│       ├── <a href="./.github/workflows/slsa-verification.yml">slsa-verification.yml</a>
│       ├── <a href="./.github/workflows/sbom-generation.yml">sbom-generation.yml</a>
│       ├── <a href="./.github/workflows/audit-log.yml">audit-log.yml</a>
│       ├── <a href="./.github/workflows/pur-l3-dast-scan.yml">pur-l3-dast-scan.yml</a>
│       └── <a href="./.github/workflows/int-l3-reproducible-build.yml">int-l3-reproducible-build.yml</a>
├── docs/
│   ├── <a href="./docs/matrix-core.md">matrix-core.md</a>
│   ├── passport/
│   │   ├── <a href="./docs/passport/L1-PASSPORT.md">L1-PASSPORT.md</a>
│   │   ├── <a href="./docs/passport/L2-PASSPORT.md">L2-PASSPORT.md</a>
│   │   └── <a href="./docs/passport/L3-PASSPORT.md">L3-PASSPORT.md</a>
│   ├── l3/
│   │   ├── <a href="./docs/l3/README.md">README.md</a>
│   │   ├── <a href="./docs/l3/reproducible-builds.md">reproducible-builds.md</a>
│   │   ├── <a href="./docs/l3/zero-downtime-deployment.md">zero-downtime-deployment.md</a>
│   │   ├── <a href="./docs/l3/independent-audit.md">independent-audit.md</a>
│   │   ├── <a href="./docs/l3/SOC2-preparation.md">SOC2-preparation.md</a>
│   │   └── <a href="./docs/l3/ISO27001-preparation.md">ISO27001-preparation.md</a>
│   ├── adr/
│   │   ├── <a href="./docs/adr/0001-python-scanner-choice.md">0001-python-scanner-choice.md</a>
│   │   └── <a href="./docs/adr/0002-auto-changelog-pr-strategy.md">0002-auto-changelog-pr-strategy.md</a>
│   ├── levels/
│   │   ├── <a href="./docs/levels/L1-basic.md">L1-basic.md</a>
│   │   ├── <a href="./docs/levels/L2-advanced.md">L2-advanced.md</a>
│   │   └── <a href="./docs/levels/L3-ideal.md">L3-ideal.md</a>
│   ├── examples/
│   │   ├── <a href="./docs/examples/ai-systems.md">ai-systems.md</a>
│   │   └── <a href="./docs/examples/self-audit.md">self-audit.md</a>
│   └── rfc/
│       └── <a href="./docs/rfc/RFC-v1.1.md">RFC-v1.1.md</a>
├── tools/
│   ├── <a href="./tools/scanner-l1.py">scanner-l1.py</a>
│   ├── <a href="./tools/scanner-l2.py">scanner-l2.py</a>
│   ├── <a href="./tools/scanner-l3.py">scanner-l3.py</a>
│   ├── <a href="./tools/generate-sbom.py">generate-sbom.py</a>
│   ├── <a href="./tools/verify-slsa.py">verify-slsa.py</a>
│   ├── <a href="./tools/worm-logger.py">worm-logger.py</a>
│   ├── <a href="./tools/export-audit-bundle.py">export-audit-bundle.py</a>
│   ├── <a href="./tools/metrics-l2.py">metrics-l2.py</a>
│   └── <a href="./tools/auto-changelog.py">auto-changelog.py</a>
└── assets/
    └── images/
</pre>

---

## Примеры адаптации

- [AI-системы и ML-пайплайны](./docs/examples/ai-systems.md)
- [Аудит GitHub-репозитория KON-MATRIX (самоприменение)](./docs/examples/self-audit.md)

---

## Использование методологии

Если вы хотите применить KON-MATRIX к своему проекту — напишите на ccf@azesmf.ru. Обсудим формат и ограничения лицензии.

---

## Связь

- 📧 **Email:** ccf@azesmf.ru
- 🔗 **Каноническая лицензия:** [Field-CoCreation](https://github.com/AzesmF/AI-Symbiosis-H/blob/main/Legal%2FField-CoCreation-Licenses%2FField-CoCreation.md)

---

## Лицензия

Данный проект распространяется под лицензией Field-CoCreation (Корневая).  
Полный текст см. в файле [LICENSE](./LICENSE).
