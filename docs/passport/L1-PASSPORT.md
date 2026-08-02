# KON-MATRIX PASSPORT — Уровень L1

**Проект:** Kon-Matrix  
**Уровень верификации:** L1 (Базовый)  
**Дата выдачи:** 2026-08-03  
**Верифицировал:** Павел (AzemF)  
**CI/CD статус:** ✅ [Автоматическая проверка L1](https://github.com/AzesmF/Kon-Matrix/actions)

---

## 📦 Артефакты L1

### 1. Целостность (INT-L1)
**Артефакт:** [SHA256SUMS](../../SHA256SUMS)  
**Проверка:** 26 файлов, все SHA-256 хэши совпадают  
**Инструмент:** `tools/scanner-l1.py` (реальная сверка через hashlib)

### 2. Чистота (PUR-L1)
**Артефакт:** [pyproject.toml](../../pyproject.toml)  
**Проверка:** Секция `[project]` и ключ `dependencies` объявлены  
**Инструмент:** Валидация TOML (tomllib/regex)

### 3. Становление (EVO-L1)
**Артефакт:** [CHANGELOG.md](../../CHANGELOG.md)  
**Проверка:** Найдена версия `[0.2.0]` с датой 2026-08-03  
**Формат:** SemVer (Keep a Changelog)

### 4. Прозрачность (TRA-L1)
**Артефакт:** Git-история  
**Проверка:** HEAD = `cd843d115c9d...`  
**Инструмент:** `git rev-parse HEAD`

---

## 🎯 Итоговая проверка

    ╔══════════════════════════════════════════════════════════════╗
    ║           KON-MATRIX  ·  L1 Scanner  ·  Базовый уровень      ║
    ╚══════════════════════════════════════════════════════════════╝
      INT-L1  ✅  PASS  SHA256SUMS: сверено 26 файлов
      PUR-L1  ✅  PASS  pyproject.toml: валиден
      EVO-L1  ✅  PASS  CHANGELOG.md: версия [0.2.0]
      TRA-L1  ✅  PASS  Git-история доступна
       Итог: PASS — все 4 критерия L1 выполнены (4/4)

---

## 🔗 Ссылки

- **Репозиторий:** https://github.com/AzesmF/Kon-Matrix
- **Методология:** [docs/matrix-core.md](../matrix-core.md)
- **Сканер L1:** [tools/scanner-l1.py](../../tools/scanner-l1.py)
- **CI/CD Workflow:** [.github/workflows/kon-matrix-l1-check.yml](../../.github/workflows/kon-matrix-l1-check.yml)

---
*Этот Passport сформирован на основе результатов scanner-l1.py*  
*Следующая верификация: при создании версии v0.3.0*
