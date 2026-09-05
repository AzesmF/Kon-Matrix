# Журнал изменений (Changelog)

## [v0.4.0] - 2026-09-05

### Changes
- docs: auto-update CHANGELOG and SHA256SUMS for v0.3.0 (#7) (fed4e25)
- feat(l3): завершение Фаз 1 и 2 (Целостность и Прозрачность) (03ea1ad)
- ci: переделать workflows sbom и audit-log на создание PR (соблюдение INT-L3) (b0cd7de)
- fix: исправить audit-log workflow (9f46d29)
- feat(l3-tra): добавлен инструмент экспорта аудиторского пакета (32685c2)
- build(deps): bump actions/upload-artifact from 4 to 7 (#8) (be96368)
- build(deps): bump actions/setup-python from 5 to 7 (#9) (d6f8230)
- build(deps): bump actions/checkout from 4 to 7 (#10) (792ef1a)
- build(deps): bump peter-evans/create-pull-request from 6 to 8 (#11) (fecdda3)
- feat(l3-pur): добавлен workflow DAST-сканирования (OWASP ZAP) (#12) (af81168)
- Feat/int l3 diffoscope (#13) (ed4b356)
- feat(l3-docs): добавлены гайды для аудиторов (SOC 2, ISO 27001, Independent Audit) (#14) (8cc99c8)
- feat(l3-core): финальное обновление scanner-l3.py для валидации Фазы 3 (#15) (5b39bc9)


## [v0.3.0] - 2026-08-14

### Changes
- docs: auto-update CHANGELOG and SHA256SUMS for v0.2.1 (e0edbd6)
- docs: актуализация README.md для GitHub Pages (597d984)
- docs: актуализация L3-PASSPORT.md (56b6d06)
- build(deps): bump actions/checkout from 4 to 7 (#6) (8632971)
- build(deps): bump actions/setup-python from 5 to 7 (#5) (04e353f)
- ci: use PAT_TOKEN for auto-changelog workflow (e0c3e53)
- ci: переход на создание PR для auto-changelog (соблюдение INT-L3) (22d52d5)


## [v0.2.1] - 2026-08-07

### Changes
- init: ствол методологии KON-MATRIX v2.0, примеры адаптации, лицензия (2016964)
- добавлены доказательства IPFS и TON timestamping (8b8b1e2)
- ребрендинг: деловая лексика, добавлены RFC v1.1, CHANGELOG, PHILOSOPHY (fa490d2)
- обновлён BLOCKCHAIN.md: добавлена временная метка версии после ребрендинга (eaebab9)
- добавлены SVG-иконки, логотип, _config.yml для GitHub Pages (491782f)
- исправлены ссылки для GitHub Pages, добавлен индекс примеров, самоаудит (2b4c23b)
- добавлен авто-сканер L1 и SHA256SUMS для целостности (b9585e4)
- автоматизация SHA256SUMS через pre-commit hook, обновлены matrix-core и README (f71ba74)
- добавлены шаблоны Issues: proposal и bug report (839d035)
- Merge pull request #1 from AzesmF/feature/issue-templates (52f5972)
- исправлена структура репозитория через HTML-дерево для Pages (83507cc)
- добавлен L2-сканер для проверки продвинутого уровня (5ac7578)
- Merge pull request #2 from AzesmF/feature/scanner-l2 (3e907f5)
- добавлен первый ADR: выбор лицензии Field-CoCreation (e2c18e4)
- актуализирован CHANGELOG: добавлены изменения за 14 мая 2026 (d16a436)
- feat: add Kon-Matrix L1 CI workflow (cd843d1)
- feat: update CHANGELOG to SemVer format and regenerate SHA256SUMS (47ca9da)
- docs: add Kon-Matrix L1 Passport and update README badge (89672f3)
- feat(l2): add Dependabot security scanning and initial ADR (d81f941)
- Bump actions/checkout from 4 to 7 (#4) (905b846)
- Bump actions/setup-python from 5 to 7 (#3) (e599aa7)
- feat(l2): add TRA-L2 metrics dashboard and update Passport to L2 (4f6345f)
- fix: исправить ошибки L2 артефактов и обновить статус (c6841ac)
- ci: add auto-changelog workflow for releases (3300046)
- feat: add Python-based auto-changelog workflow (ec750db)


## [0.2.0] - 2026-08-03

### Added
- Усилен scanner-l1.py: реальная проверка SHA-256 хэшей файлов (INT-L1)
- Добавлена валидация pyproject.toml с поддержкой tomllib (PUR-L1)
- Внедрён строгий SemVer формат для CHANGELOG (EVO-L1)
- Настроен GitHub Actions workflow для автоматической проверки L1
- Добавлен pyproject.toml для декларации зависимостей Python-инструмента

### Changed
- Обновлена структура CHANGELOG с переходом на формат Keep a Changelog

## [0.1.0] - 2026-05-14

### Added
- Первоначальная версия методологии Kon-Matrix
- Базовый scanner-l1.py для проверки L1
- Документация по 4 Абсолютным Конам
- SHA256SUMS для контроля целостности артефактов

## 2026-05-14 — Инструментальное усиление: сканеры, ADR, шаблоны

**Цель:** оснастить репозиторий инструментами автоматической проверки и подготовить к внешнему аудиту.

### Добавлено
- `tools/scanner-l1.py` — автоматическая проверка L1-критериев (INT, PUR, EVO, TRA).
- `tools/scanner-l2.py` — автоматическая проверка L2-критериев.
- `.githooks/pre-commit` — автоматическое обновление `SHA256SUMS` перед каждым коммитом.
- `docs/adr/001-field-cocreation-license.md` — первая запись об архитектурном решении.
- `.github/ISSUE_TEMPLATE/` — шаблоны для предложений и замечаний.
- SVG-иконки принципов и логотип в `assets/images/`.

### Изменено
- `README.md` — интерактивная структура репозитория с HTML-деревом и ссылками.
- `docs/matrix-core.md` — добавлены иконки принципов.

### Результат
- L1-сканер: все критерии пройдены.
- L2-сканер: все критерии пройдены.
- GitHub Pages: полноценная навигация по документации.

---

## 2026-05-07 — Ребрендинг лексики и деловая унификация

**Цель:** привести тексты репозитория к деловому, прагматичному стилю в соответствии с Техническим Заданием.

### Изменённые файлы

- `README.md` — полностью переписан в деловом тоне, удалены эзотерические формулировки, добавлены разделы «Кому и зачем», обновлена структура.
- `docs/matrix-core.md` — переименованы разделы (Принципы), унифицирована терминология: «артефакт» → «проверяемый объект», «L3 Идеальный» → «L3 Целевой», добавлены пояснения «Зачем это бизнесу».
- `docs/levels/L1-basic.md` — лексика приведена к единому стандарту.
- `docs/levels/L2-advanced.md` — лексика приведена к единому стандарту.
- `docs/levels/L3-ideal.md` — переименован в «Целевой», скорректирован текст.
- `docs/examples/web-development.md` — обновлены заголовки, удалены сакральные термины.
- `docs/examples/ai-systems.md` — обновлены заголовки, терминология.
- `docs/examples/offline-business.md` — обновлены заголовки, терминология.
- `docs/examples/hr-processes.md` — обновлены заголовки, терминология.
- `CONTRIBUTING.md` — переписаны названия принципов, заменён «Кон» на «Принцип», удалены эзотерические замены.
- `ROADMAP.md` — актуализирован план, добавлены текущие задачи.
- Добавлен `PHILOSOPHY.md` — личное видение автора вынесено из деловых документов.

### Ключевые замены

| Было | Стало |
|------|-------|
| Кон Целостности / INT | Принцип целостности |
| Кон Чистоты / PUR | Принцип чистоты |
| Кон Становления / EVO | Принцип развития |
| Кон Прозрачности / TRA | Принцип прозрачности |
| Абсолютные Коны | Четыре базовых принципа / 4 Pillars |
| Артефакт | Проверяемый объект |
| L3 Идеальный | L3 Целевой |
| Матрица Конов | Оценочная матрица / KON-MATRIX |

Все изменения направлены на восприятие репозитория как инструмента делового аудита.
