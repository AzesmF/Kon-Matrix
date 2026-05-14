#!/usr/bin/env python3
"""
KON-MATRIX L1 Scanner (MVP)
Проверяет базовый уровень (L1) четырёх принципов для Git-репозитория.
Запуск: python3 tools/scanner-l1.py [путь_к_репозиторию]
"""

import sys
import os
import subprocess
from pathlib import Path

def check_int_l1(repo_path: Path) -> tuple[bool, str]:
    """INT-L1: Наличие файла контрольных сумм."""
    candidates = ['checksums.txt', 'SHA256SUMS', 'asset_hashes.json', 'model_hashes.json']
    for f in candidates:
        if (repo_path / f).exists():
            return True, f"найден {f}"
    return False, "ни один из ожидаемых файлов контрольных сумм не обнаружен"

def check_pur_l1(repo_path: Path) -> tuple[bool, str]:
    """PUR-L1: Наличие манифеста зависимостей или описания состава."""
    candidates = ['package.json', 'sbom.json', 'cyclonedx.xml', 'Cargo.toml', 'go.mod', 'requirements.txt']
    for f in candidates:
        if (repo_path / f).exists():
            return True, f"найден {f}"
    # Дополнительно: наличие TEAM.md как манифеста для HR
    if (repo_path / 'TEAM.md').exists():
        return True, "найден TEAM.md (манифест команды)"
    # Проверим, что README или matrix-core содержат описание структуры (косвенно)
    readme = repo_path / 'README.md'
    if readme.exists():
        content = readme.read_text()
        if 'структура репозитория' in content.lower() or 'состав' in content.lower():
            return True, "README содержит описание состава системы"
    return False, "манифест зависимостей или описание состава не найдены"

def check_evo_l1(repo_path: Path) -> tuple[bool, str]:
    """EVO-L1: Наличие CHANGELOG.md."""
    changelog = repo_path / 'CHANGELOG.md'
    if changelog.exists():
        return True, "CHANGELOG.md присутствует"
    # Альтернатива: news.md, HISTORY.md
    for alt in ['news.md', 'HISTORY.md']:
        if (repo_path / alt).exists():
            return True, f"найден {alt}"
    return False, "CHANGELOG.md отсутствует"

def check_tra_l1(repo_path: Path) -> tuple[bool, str]:
    """TRA-L1: Наличие структурированных логов (через историю Git)."""
    try:
        result = subprocess.run(
            ['git', '-C', str(repo_path), 'log', '--oneline', '-n', '1'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return True, f"история коммитов доступна (последний: {result.stdout.strip()[:50]})"
        return False, "не удалось получить историю коммитов"
    except Exception as e:
        return False, f"ошибка проверки Git: {e}"

def main():
    repo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    print(f"KON-MATRIX L1 Scanner\nРепозиторий: {repo.resolve()}\n")

    checks = {
        "Целостность (INT-L1)": check_int_l1,
        "Чистота (PUR-L1)": check_pur_l1,
        "Развитие (EVO-L1)": check_evo_l1,
        "Прозрачность (TRA-L1)": check_tra_l1,
    }

    all_pass = True
    for name, func in checks.items():
        ok, msg = func(repo)
        status = "✅" if ok else "❌"
        if not ok:
            all_pass = False
        print(f"{status} {name}: {msg}")

    print(f"\nИтог: {'Все L1 критерии выполнены' if all_pass else 'Некоторые L1 критерии не выполнены'}")

if __name__ == '__main__':
    main()
