#!/usr/bin/env python3
"""
KON-MATRIX L2 Scanner (MVP)
Проверяет продвинутый уровень (L2) четырёх принципов для Git-репозитория.
Запуск: python3 tools/scanner-l2.py [путь_к_репозиторию]
"""

import sys
import os
import subprocess
from pathlib import Path

def check_int_l2(repo_path: Path) -> tuple[bool, str]:
    """INT-L2: История линейна и защищена от перезаписи (нет force push)."""
    # Проверяем, есть ли удалённый origin
    try:
        result = subprocess.run(
            ['git', '-C', str(repo_path), 'remote', 'get-url', 'origin'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return False, "удалённый репозиторий origin не настроен, невозможно проверить force push"

        # Сравниваем локальную и удалённую ветки master
        subprocess.run(['git', '-C', str(repo_path), 'fetch', 'origin', 'master'], capture_output=True, timeout=15)
        local_rev = subprocess.run(
            ['git', '-C', str(repo_path), 'rev-list', '--count', 'HEAD'],
            capture_output=True, text=True
        ).stdout.strip()
        remote_rev = subprocess.run(
            ['git', '-C', str(repo_path), 'rev-list', '--count', 'origin/master'],
            capture_output=True, text=True
        ).stdout.strip()

        if local_rev == remote_rev:
            # Дополнительно проверим, что история не содержит diverged
            ahead = subprocess.run(
                ['git', '-C', str(repo_path), 'rev-list', '--count', 'HEAD', '^origin/master'],
                capture_output=True, text=True
            ).stdout.strip()
            behind = subprocess.run(
                ['git', '-C', str(repo_path), 'rev-list', '--count', 'origin/master', '^HEAD'],
                capture_output=True, text=True
            ).stdout.strip()
            if ahead == '0' and behind == '0':
                return True, "локальная и удалённая ветки синхронны, история не переписана"
            else:
                return False, f"расхождение: впереди {ahead}, позади {behind} коммитов (возможен force push)"
        else:
            return False, f"локальных коммитов {local_rev}, удалённых {remote_rev} (возможен force push)"
    except Exception as e:
        return False, f"ошибка проверки истории Git: {e}"

def check_pur_l2(repo_path: Path) -> tuple[bool, str]:
    """PUR-L2: Отсутствие критических уязвимостей (наличие отчётов сканеров)."""
    # Ищем файлы отчётов безопасности
    report_files = list(repo_path.glob('**/*trivy*')) + \
                   list(repo_path.glob('**/*sast*')) + \
                   list(repo_path.glob('**/*audit*')) + \
                   list(repo_path.glob('**/*vulnerability*'))
    if report_files:
        return True, f"найдены отчёты: {', '.join(f.name for f in report_files[:3])}"
    # Проверим, есть ли SBOM с проверкой уязвимостей
    sbom = repo_path / 'sbom.json'
    if sbom.exists():
        return True, "найден sbom.json (может содержать информацию об уязвимостях)"
    return False, "отчёты сканеров уязвимостей не найдены. Рекомендуется запустить Trivy или аналогичный инструмент"

def check_evo_l2(repo_path: Path) -> tuple[bool, str]:
    """EVO-L2: Фиксация архитектурных решений (ADR)."""
    adr_dir = repo_path / 'docs' / 'adr'
    if adr_dir.is_dir():
        files = list(adr_dir.glob('*'))
        if files:
            return True, f"найдено {len(files)} ADR в docs/adr/"
        else:
            return False, "папка docs/adr/ пуста"
    return False, "папка docs/adr/ отсутствует"

def check_tra_l2(repo_path: Path) -> tuple[bool, str]:
    """TRA-L2: Наблюдаемость в реальном времени (дашборд/статус-страница)."""
    # Проверим наличие status.md или упоминание в README
    status_file = repo_path / 'STATUS.md'
    if status_file.exists():
        return True, "найден STATUS.md"
    readme = repo_path / 'README.md'
    if readme.exists():
        content = readme.read_text().lower()
        if 'статус-страница' in content or 'status page' in content or 'дашборд' in content:
            return True, "README содержит упоминание статус-страницы или дашборда"
    # Может быть внешняя ссылка на статус-страницу
    return False, "нет явной ссылки на статус-страницу или дашборд. Рекомендуется добавить STATUS.md"

def main():
    repo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    print(f"KON-MATRIX L2 Scanner\nРепозиторий: {repo.resolve()}\n")

    checks = {
        "Целостность (INT-L2)": check_int_l2,
        "Чистота (PUR-L2)": check_pur_l2,
        "Развитие (EVO-L2)": check_evo_l2,
        "Прозрачность (TRA-L2)": check_tra_l2,
    }

    all_pass = True
    for name, func in checks.items():
        ok, msg = func(repo)
        status = "✅" if ok else "❌"
        if not ok:
            all_pass = False
        print(f"{status} {name}: {msg}")

    print(f"\nИтог: {'Все L2 критерии выполнены' if all_pass else 'Некоторые L2 критерии требуют внимания'}")

if __name__ == '__main__':
    main()
