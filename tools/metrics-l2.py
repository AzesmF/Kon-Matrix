#!/usr/bin/env python3
"""
KON-MATRIX L2 Metrics Dashboard
Собирает базовые метрики репозитория для уровня TRA-L2 (Прозрачность).
"""

import subprocess
from pathlib import Path
from datetime import datetime

def run_cmd(cmd: list[str]) -> str:
    """Выполняет команду и возвращает вывод."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def get_commit_count() -> int:
    """Количество коммитов в репозитории."""
    return int(run_cmd(["git", "rev-list", "--count", "HEAD"]))

def get_contributor_count() -> int:
    """Количество уникальных авторов."""
    output = run_cmd(["git", "shortlog", "-sn", "--no-merges"])
    return len(output.split("\n")) if output else 0

def get_file_count() -> int:
    """Количество файлов в репозитории (без .git)."""
    output = run_cmd(["find", ".", "-type", "f", "-not", "-path", "./.git/*"])
    return len(output.split("\n")) if output else 0

def get_last_commit_date() -> str:
    """Дата последнего коммита."""
    return run_cmd(["git", "log", "-1", "--format=%ci"])

def get_open_issues() -> int:
    """Количество открытых Issues (через gh CLI)."""
    try:
        output = run_cmd(["gh", "issue", "list", "--state", "open", "--json", "id"])
        return output.count('"id"')
    except Exception:
        return -1  # gh не установлен или нет доступа

def get_open_prs() -> int:
    """Количество открытых PR (через gh CLI)."""
    try:
        output = run_cmd(["gh", "pr", "list", "--state", "open", "--json", "id"])
        return output.count('"id"')
    except Exception:
        return -1

def main():
    repo_path = Path.cwd()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         KON-MATRIX  ·  L2 Metrics Dashboard  ·  TRA-L2      ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"  Репозиторий: {repo_path.resolve()}")
    print(f"  Дата отчёта: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("──────────────────────────────────────────────────────────────")
    
    metrics = [
        ("📊 Коммиты", get_commit_count()),
        ("👥 Контрибьюторы", get_contributor_count()),
        ("📁 Файлы", get_file_count()),
        ("🕐 Последний коммит", get_last_commit_date()),
        (" Открытые Issues", get_open_issues()),
        ("🔀 Открытые PR", get_open_prs()),
    ]
    
    for name, value in metrics:
        print(f"  {name}: {value}")
    
    print("──────────────────────────────────────────────────────────────")
    print("  ️  Для production-систем: Prometheus + Grafana")
    print("  ℹ️  Для Kon-Matrix: метрики репозитория и статус CI/CD")
    print("╚══════════════════════════════════════════════════════════════╝")

if __name__ == "__main__":
    main()
