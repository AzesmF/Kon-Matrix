#!/usr/bin/env python3
"""
KON-MATRIX L2 Metrics Dashboard
Собирает базовые метрики репозитория для уровня TRA-L2 (Прозрачность).
"""

import subprocess
from pathlib import Path
from datetime import datetime

def run_cmd(cmd: list) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def main():
    repo_path = Path.cwd()
    
    commits = run_cmd(["git", "rev-list", "--count", "HEAD"]) or "0"
    contributors_out = run_cmd(["git", "shortlog", "-sn", "--no-merges"])
    contributors = str(len(contributors_out.split("\n"))) if contributors_out else "0"
    files_out = run_cmd(["find", ".", "-type", "f", "-not", "-path", "./.git/*"])
    files = str(len(files_out.split("\n"))) if files_out else "0"
    last_commit = run_cmd(["git", "log", "-1", "--format=%ci"]) or "N/A"
    
    try:
        issues_out = run_cmd(["gh", "issue", "list", "--state", "open", "--json", "id"])
        issues = str(issues_out.count('"id"'))
    except Exception:
        issues = "N/A"

    try:
        prs_out = run_cmd(["gh", "pr", "list", "--state", "open", "--json", "id"])
        prs = str(prs_out.count('"id"'))
    except Exception:
        prs = "N/A"

    print("KON-MATRIX L2 Metrics Dashboard (TRA-L2)")
    print(f"Репозиторий: {repo_path.resolve()}")
    print(f"Дата отчёта: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-" * 50)
    print(f"Коммиты:          {commits}")
    print(f"Контрибьюторы:    {contributors}")
    print(f"Файлы:            {files}")
    print(f"Последний коммит: {last_commit}")
    print(f"Открытые Issues:  {issues}")
    print(f"Открытые PR:      {prs}")
    print("-" * 50)
    print("Информация:")
    print("- Для production систем используется Prometheus + Grafana")
    print("- Для Kon-Matrix используются метрики репозитория и CI/CD статус")

if __name__ == "__main__":
    main()
