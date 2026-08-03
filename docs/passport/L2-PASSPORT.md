# KON-MATRIX PASSPORT — Уровень L2

**Проект:** Kon-Matrix  
**Уровень верификации:** L2 (Продвинутый)  
**Дата выдачи:** 2026-08-03  
**Верифицировал:** Павел (AzemF)  

**Статусы:**
- CI/CD: [Автоматическая проверка L1](https://github.com/AzesmF/Kon-Matrix/actions)
- Dependabot: [Security Alerts Enabled](https://github.com/AzesmF/Kon-Matrix/security/dependabot)

---

## Артефакты L2

### 1. Целостность (INT-L2)
- **Артефакт:** [История коммитов](https://github.com/AzesmF/Kon-Matrix/commits/master)
- **Проверка:** Все коммиты подписаны SSH-ключом (Verified на GitHub)
- **Инструмент:** Git + SSH signature

### 2. Чистота (PUR-L2)
- **Артефакт:** [.github/dependabot.yml](../../.github/dependabot.yml)
- **Проверка:** Автоматическое сканирование CVE для pip и github-actions
- **Инструмент:** Dependabot

### 3. Становление (EVO-L2)
- **Артефакт:** [docs/adr/0001-python-scanner-choice.md](../../docs/adr/0001-python-scanner-choice.md)
- **Проверка:** Архитектурные решения зафиксированы с обоснованием
- **Инструмент:** ADR (Architecture Decision Records)

### 4. Прозрачность (TRA-L2)
- **Артефакт:** [tools/metrics-l2.py](../../tools/metrics-l2.py)
- **Проверка:** Метрики репозитория доступны в реальном времени
- **Инструмент:** Python-скрипт + GitHub Insights

---

## Ссылки

- **Репозиторий:** https://github.com/AzesmF/Kon-Matrix
- **L1 Passport:** [L1-PASSPORT.md](./L1-PASSPORT.md)
- **ADR:** [docs/adr/](../../docs/adr/)
- **GitHub Insights:** https://github.com/AzesmF/Kon-Matrix/pulse

*Этот Passport сформирован на основе артефактов L2*
