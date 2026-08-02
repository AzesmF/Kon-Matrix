#!/usr/bin/env python3
"""
KON-MATRIX L1 Scanner.

Проверяет базовый уровень (L1) четырёх принципов для Git-репозитория:
INT-L1 (Целостность), PUR-L1 (Чистота), EVO-L1 (Становление), TRA-L1 (Прозрачность).

Запуск: python3 tools/scanner-l1.py [путь_к_репозиторию]
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

# --- Константы и шаблоны ---

CHECKSUM_CANDIDATES: tuple[str, ...] = ("checksums.txt", "SHA256SUMS")
DEPENDENCY_CANDIDATES: tuple[str, ...] = ("requirements.txt", "pyproject.toml")
CHANGELOG_FILE = "CHANGELOG.md"

SHA256_LINE_PATTERN = re.compile(
    r"^[0-9a-fA-F]{64}\s+\S+",
    re.MULTILINE,
)
VERSION_HEADER_PATTERN = re.compile(
    r"^##\s+\[[^\]]+\]",
    re.MULTILINE,
)
CHANGELOG_TITLE_PATTERN = re.compile(
    r"(?i)^#\s+.*\bchangelog\b",
    re.MULTILINE,
)
REQUIREMENTS_LINE_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._\-]*"
    r"(?:\s*[=<>!~]+\s*[^\s#]+|\s*\[[^\]]+\])?\s*$",
)
PYPROJECT_SECTION_PATTERN = re.compile(
    r"^\[project\]",
    re.MULTILINE,
)
PYPROJECT_DEPENDENCIES_PATTERN = re.compile(
    r"(?i)^dependencies\s*=",
    re.MULTILINE,
)

CheckResult = tuple[bool, str]
CheckFunc = Callable[[Path], CheckResult]


def _read_text(path: Path) -> tuple[str | None, str]:
    """
    Безопасно прочитать текстовый файл.

    Returns:
        Кортеж (содержимое или None, сообщение об ошибке при неудаче).
    """
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"не удалось прочитать файл {path.name}: {exc}"
    if not content.strip():
        return None, f"файл {path.name} пуст"
    return content, ""


def _find_first_existing(repo_path: Path, names: tuple[str, ...]) -> Path | None:
    """Найти первый существующий файл из списка имён в корне репозитория."""
    for name in names:
        candidate = repo_path / name
        if candidate.is_file():
            return candidate
    return None


def _validate_sha256_checksums(content: str, filename: str) -> CheckResult:
    """
    Проверить, что текст содержит хотя бы одну строку формата SHA-256.

    Ожидаемый формат: 64 hex-символа, пробел(ы), имя файла.
    """
    matches = SHA256_LINE_PATTERN.findall(content)
    if not matches:
        return (
            False,
            f"файл {filename} не содержит строк в формате SHA-256 "
            "(ожидается: 64 hex-символа, пробел, имя файла)",
        )
    return True, f"файл {filename}: найдено {len(matches)} валидных записей SHA-256"


def _parse_requirements(content: str) -> CheckResult:
    """
    Базовая проверка синтаксиса requirements.txt.

    Допускаются строки зависимостей, комментарии (#) и директивы -r/-e.
    """
    valid_lines = 0
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("-r ", "--requirement ", "-e ", "--editable ")):
            valid_lines += 1
            continue
        if REQUIREMENTS_LINE_PATTERN.match(line):
            valid_lines += 1
            continue
        return (
            False,
            f"requirements.txt содержит строку с неверным форматом: «{raw_line.strip()[:60]}»",
        )
    if valid_lines == 0:
        return False, "requirements.txt не содержит распознанных зависимостей"
    return True, f"requirements.txt: распознано {valid_lines} строк зависимостей"


def _parse_pyproject(content: str) -> CheckResult:
    """
    Базовая проверка pyproject.toml (PEP 621) на наличие [project] и dependencies.

    Пустой список dependencies = [] допустим — инструмент может опираться
    только на стандартную библиотеку Python.
    """
    if not PYPROJECT_SECTION_PATTERN.search(content):
        return False, "pyproject.toml не содержит секции [project] (PEP 621)"
    if not PYPROJECT_DEPENDENCIES_PATTERN.search(content):
        return (
            False,
            "pyproject.toml: в секции [project] отсутствует ключ dependencies",
        )
    return True, "pyproject.toml: секция [project] и ключ dependencies объявлены"


def check_int_l1(repo_path: Path) -> CheckResult:
    """
    INT-L1 (Целостность): проверка файла контрольных сумм.

    Файл checksums.txt (или SHA256SUMS) должен существовать и содержать
    хотя бы одну строку формата SHA-256.
    """
    checksum_path = _find_first_existing(repo_path, CHECKSUM_CANDIDATES)
    if checksum_path is None:
        expected = ", ".join(CHECKSUM_CANDIDATES)
        return False, f"файл контрольных сумм не найден (ожидается один из: {expected})"

    content, error = _read_text(checksum_path)
    if content is None:
        return False, error

    return _validate_sha256_checksums(content, checksum_path.name)


def check_pur_l1(repo_path: Path) -> CheckResult:
    """
    PUR-L1 (Чистота): проверка манифеста зависимостей.

    Должен существовать requirements.txt или pyproject.toml с непустым
    и базово валидным содержимым.
    """
    dep_path = _find_first_existing(repo_path, DEPENDENCY_CANDIDATES)
    if dep_path is None:
        expected = ", ".join(DEPENDENCY_CANDIDATES)
        return False, f"манифест зависимостей не найден (ожидается один из: {expected})"

    content, error = _read_text(dep_path)
    if content is None:
        return False, error

    if dep_path.name == "requirements.txt":
        return _parse_requirements(content)
    return _parse_pyproject(content)


def check_evo_l1(repo_path: Path) -> CheckResult:
    """
    EVO-L1 (Становление): проверка журнала изменений CHANGELOG.md.

    Файл должен содержать маркер версии (## [x.y.z]) или заголовок Changelog.
    """
    changelog_path = repo_path / CHANGELOG_FILE
    if not changelog_path.is_file():
        return False, f"файл {CHANGELOG_FILE} отсутствует"

    content, error = _read_text(changelog_path)
    if content is None:
        return False, error

    if VERSION_HEADER_PATTERN.search(content):
        return True, f"{CHANGELOG_FILE}: обнаружен маркер версии (## [x.y.z])"

    if CHANGELOG_TITLE_PATTERN.search(content):
        return True, f"{CHANGELOG_FILE}: обнаружен заголовок Changelog"

    return (
        False,
        f"{CHANGELOG_FILE} не содержит маркера версии "
        "(ожидается «## [x.y.z]» или заголовок «# … Changelog»)",
    )


def check_tra_l1(repo_path: Path) -> CheckResult:
    """
    TRA-L1 (Прозрачность): проверка Git-истории.

    Директория должна быть Git-репозиторием с хотя бы одним коммитом.
    """
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        return False, "директория не является Git-репозиторием (отсутствует .git)"

    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except FileNotFoundError:
        return False, "команда git не найдена в PATH"
    except subprocess.TimeoutExpired:
        return False, "проверка Git превысила лимит времени (10 с)"

    if result.returncode != 0:
        stderr = result.stderr.strip() or "неизвестная ошибка"
        return False, f"Git-репозиторий не содержит коммитов: {stderr}"

    head = result.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        return False, f"получен некорректный идентификатор HEAD: {head!r}"

    short_head = head[:12]
    return True, f"Git-история доступна, HEAD = {short_head}…"


def _format_verdict(ok: bool, message: str) -> str:
    """Сформировать строку вердикта для одной проверки."""
    status = "PASS" if ok else "FAIL"
    icon = "✅" if ok else "❌"
    return f"{icon}  {status:<4}  {message}"


def run_checks(repo_path: Path) -> tuple[bool, list[tuple[str, bool, str]]]:
    """
    Выполнить все L1-проверки.

    Returns:
        Кортеж (все_пройдены, список (название, ok, сообщение)).
    """
    checks: tuple[tuple[str, CheckFunc], ...] = (
        ("INT-L1  Целостность", check_int_l1),
        ("PUR-L1  Чистота", check_pur_l1),
        ("EVO-L1  Становление", check_evo_l1),
        ("TRA-L1  Прозрачность", check_tra_l1),
    )

    results: list[tuple[str, bool, str]] = []
    all_pass = True

    for title, check_func in checks:
        ok, message = check_func(repo_path)
        results.append((title, ok, message))
        if not ok:
            all_pass = False

    return all_pass, results


def print_report(repo_path: Path, all_pass: bool, results: list[tuple[str, bool, str]]) -> None:
    """Вывести читаемый отчёт о проверке L1 в консоль."""
    separator = "─" * 62
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║           KON-MATRIX  ·  L1 Scanner  ·  Базовый уровень      ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    print(f"  Репозиторий: {repo_path.resolve()}")
    print()
    print(separator)

    for title, ok, message in results:
        print(f"  {title}")
        print(f"  {_format_verdict(ok, message)}")
        print(separator)

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print()
    if all_pass:
        print(f"  🎯  Итог: PASS — все {total} критерия L1 выполнены ({passed}/{total})")
    else:
        print(
            f"  ⚠️   Итог: FAIL — выполнено {passed} из {total} критериев L1"
        )
    print()


def resolve_repo_path(argv: list[str]) -> Path:
    """
    Определить путь к репозиторию из аргументов CLI.

    Args:
        argv: Список аргументов (обычно sys.argv).

    Returns:
        Path к корню репозитория.
    """
    if len(argv) > 1:
        return Path(argv[1]).expanduser().resolve()
    return Path.cwd().resolve()


def main() -> int:
    """Точка входа CLI. Возвращает код выхода: 0 при успехе, 1 при ошибках."""
    repo_path = resolve_repo_path(sys.argv)

    if not repo_path.is_dir():
        print(f"❌  Указанный путь не является директорией: {repo_path}", file=sys.stderr)
        return 1

    all_pass, results = run_checks(repo_path)
    print_report(repo_path, all_pass, results)
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
