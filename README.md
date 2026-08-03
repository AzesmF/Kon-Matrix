<img src="assets/images/logo.svg" alt="KON-MATRIX" width="200">

**Статус:** ✅ [L2 Verified](docs/passport/L2-PASSPORT.md) | [CI/CD](https://github.com/AzesmF/Kon-Matrix/actions) | [Dependabot](https://github.com/AzesmF/Kon-Matrix/security/dependabot)

**Метод оценки зрелости систем и процессов**

[![Лицензия: Field-CoCreation](https://img.shields.io/badge/License-Field--CoCreation-blue)](./LICENSE)  
[![Грант: Создай НАШЕ](https://img.shields.io/badge/Грант-Создай%20НАШЕ-orange)](#)

---

## Что это?

KON-MATRIX — это универсальный чек-лист из 12 пунктов для проверки надёжности, безопасности, управляемости и прозрачности любого проекта: от веб-сайта до HR-отдела.  
Методология основана на четырёх базовых принципах и трёх уровнях зрелости, что позволяет применять её как в стартапах, так и в крупных корпоративных системах.

---

## Как устроена матрица

| <img src="assets/images/integrity.svg" width="20" alt=""> Целостность | <img src="assets/images/purity.svg" width="20" alt=""> Чистота | <img src="assets/images/evolution.svg" width="20" alt=""> Развитие | <img src="assets/images/transparency.svg" width="20" alt=""> Прозрачность |
|---|---|---|---|
| **L1 Базовый** | Контрольные суммы артефактов | Документированный состав системы | Журнал изменений | Структурированные логи |
| **L2 Продвинутый** | Неизменная история изменений | Отсутствие критических уязвимостей | Архив архитектурных решений | Дашборды в реальном времени |
| **L3 Целевой** | Сквозная верификация от сборки до продуктива | Подтверждённая независимым аудитом безопасность | Бесшовная эволюция без остановки сервиса | Полный аудит действий и экспорт данных |

> Полная таблица критериев, доказательств и методов проверки: [docs/matrix-core.md](./docs/matrix-core.md)

---

## Кому и зачем это нужно

- **Бизнесу** — чтобы снизить операционные риски, быть готовым к аудиту и повысить доверие клиентов.
- **Разработчикам** — чтобы получить единый стандарт качества кода и процессов, понятный заказчику.
- **Пользователям** — чтобы понимать, насколько можно доверять системе и как контролируется безопасность их данных.

---

## Быстрый старт

1. Прочитайте [ядро методологии](./docs/matrix-core.md) — таблицу всех 12 ячеек.
2. Посмотрите [примеры адаптации](./docs/examples/) — веб-разработка, AI, производство, HR и самоаудит.
3. Возьмите шаблон оценки для вашего домена и проверьте свой проект.

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
├── docs/
│   ├── <a href="./docs/matrix-core.md">matrix-core.md</a>
│   ├── levels/
│   │   ├── <a href="./docs/levels/L1-basic.md">L1-basic.md</a>
│   │   ├── <a href="./docs/levels/L2-advanced.md">L2-advanced.md</a>
│   │   └── <a href="./docs/levels/L3-ideal.md">L3-ideal.md</a>
│   ├── examples/
│   │   ├── <a href="./docs/examples/web-development.md">web-development.md</a>
│   │   ├── <a href="./docs/examples/ai-systems.md">ai-systems.md</a>
│   │   ├── <a href="./docs/examples/offline-business.md">offline-business.md</a>
│   │   ├── <a href="./docs/examples/hr-processes.md">hr-processes.md</a>
│   │   └── <a href="./docs/examples/self-audit.md">self-audit.md</a>
│   └── rfc/
│       └── <a href="./docs/rfc/RFC-v1.1.md">RFC-v1.1.md</a>
├── tools/
│   └── <a href="./tools/scanner-l1.py">scanner-l1.py</a>
└── assets/
    └── images/
</pre>

---

## Примеры

- [Веб-студия / Разработка сайтов](./docs/examples/web-development.md)
- [AI-системы](./docs/examples/ai-systems.md)
- [Производство и офлайн-бизнес](./docs/examples/offline-business.md)
- [Команда / HR-процессы](./docs/examples/hr-processes.md)
- [Аудит GitHub-репозитория KON-MATRIX (самоприменение)](./docs/examples/self-audit.md)

---

## Участие в гранте

Проект участвует в конкурсе **«Создай НАШЕ»**. Мы ищем пилотные проекты для тестирования методологии и сбора обратной связи.

---

## Связь

- 📧 **Email:** ccf@azesmf.ru
- 🔗 **Каноническая лицензия:** [Field-CoCreation](https://github.com/AzesmF/AI-Symbiosis-H/blob/main/Legal%2FField-CoCreation-Licenses%2FField-CoCreation.md)

---

## Лицензия

Данный проект распространяется под лицензией Field-CoCreation (Корневая).  
Полный текст см. в файле [LICENSE](./LICENSE).
