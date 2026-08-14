#!/usr/bin/env python3
"""
KON-MATRIX L3 Scanner.

Проверяет целевой уровень (L3) четырёх принципов для Git-репозитория:
INT-L3 (сквозная верификация), PUR-L3 (независимый аудит), EVO-L3 (бесшовная эволюция),
TRA-L3 (полный аудит-лог и экспорт).

Запуск: python3 tools/scanner-l3.py [путь_к_репозиторию]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Callable

# --- Константы ---

SLSA_ATTESTATION_GLOBS: tuple[str, ...] = (
    ".slsa/**/*.json",
    "artifacts/slsa/**/*.json",
    "**/*provenance*.json",
    "**/*attestation*.json",
)
SLSA_WORKFLOW_CANDIDATES: tuple[str, ...] = (
    ".github/workflows/slsa-verification.yml",
    ".github/workflows/slsa-provenance.yml",
)
REPRODUCIBLE_BUILDS_DOC = "docs/l3/reproducible-builds.md"

SBOM_CANDIDATES: tuple[str, ...] = (
    "sbom/sbom.cyclonedx.json",
    "sbom.cyclonedx.json",
    "sbom.json",
    "bom.json",
    "sbom/spdx.json",
)

ZERO_DOWNTIME_DOC = "docs/l3/zero-downtime-deployment.md"
ZERO_DOWNTIME_KEYWORDS: tuple[str, ...] = (
    "blue-green",
    "canary",
    "rollback",
    "health check",
    "mttr",
)

WORM_LOG_DIRS: tuple[str, ...] = ("audit-logs", "worm-logs", "data/worm")
WORM_LOGGER_TOOL = "tools/worm-logger.py"
EXPORT_API_TOOL = "tools/export-api.py"
EXPORT_API_DOC = "docs/l3/export-api.md"

SLSA_LEVEL_PATTERN = re.compile(r'"buildType"\s*:|slsa\.provenance|"predicateType"\s*:\s*"https://slsa\.dev/provenance/', re.IGNORECASE)

CheckResult = tuple[bool, str]
CheckFunc = Callable[[Path], CheckResult]


def _glob_existing(repo_path: Path, pattern: str) -> list[Path]:
    """Найти файлы по glob-паттерну относительно корня репозитория."""
    return sorted(p for p in repo_path.glob(pattern) if p.is_file())


def _read_json(path: Path) -> tuple[dict | list | None, str]:
    """Прочитать и распарсить JSON-файл."""
    try:
        content = path.read_text(encoding="utf-8")
        return json.loads(content), ""
    except OSError as exc:
        return None, f"не удалось прочитать {path.relative_to(path.parents[len(path.parents) - 1])}: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"невалидный JSON в {path.name}: {exc}"


def _find_slsa_attestations(repo_path: Path) -> list[Path]:
    """Найти файлы SLSA-аттестатов в репозитории."""
    found: list[Path] = []
    for pattern in SLSA_ATTESTATION_GLOBS:
        found.extend(_glob_existing(repo_path, pattern))
    return sorted(set(found))


def _validate_slsa_attestation(path: Path, data: dict | list) -> CheckResult:
    """Проверить минимальную структуру SLSA-аттестата (Level 1+)."""
    if not isinstance(data, dict):
        return False, f"{path.name}: аттестат должен быть JSON-объектом"

    raw = json.dumps(data)
    if not SLSA_LEVEL_PATTERN.search(raw):
        return (
            False,
            f"{path.name}: не обнаружены поля SLSA Provenance (buildType / predicateType)",
        )

    predicate = data.get("predicate") or data.get("payload")
    if isinstance(predicate, dict):
        build_type = predicate.get("buildType") or predicate.get("builder", {}).get("id")
        if build_type:
            return True, f"{path.name}: SLSA Provenance, builder={build_type!r}"

    if data.get("_type") == "https://in-toto.io/Statement/v1":
        return True, f"{path.name}: in-toto Statement v1 (SLSA-совместимый формат)"

    return True, f"{path.name}: SLSA-аттестат распознан (минимальный Level 1)"


def check_int_l3(repo_path: Path) -> CheckResult:
    """
    INT-L3 (Целостность): сквозная верификация сборок.

    Проверяет наличие SLSA-аттестата, workflow верификации или гайда
    по reproducible builds.
    """
    attestations = _find_slsa_attestations(repo_path)
    for attestation_path in attestations:
        data, error = _read_json(attestation_path)
        if data is None:
            return False, error
        ok, message = _validate_slsa_attestation(attestation_path, data)
        if ok:
            rel = attestation_path.relative_to(repo_path)
            return True, f"SLSA-аттестат найден: {rel} — {message}"

    for workflow_rel in SLSA_WORKFLOW_CANDIDATES:
        workflow_path = repo_path / workflow_rel
        if workflow_path.is_file():
            content = workflow_path.read_text(encoding="utf-8")
            if "slsa" in content.lower() or "provenance" in content.lower():
                return True, f"workflow SLSA верификации: {workflow_rel}"

    repro_doc = repo_path / REPRODUCIBLE_BUILDS_DOC
    if repro_doc.is_file() and repro_doc.stat().st_size > 200:
        return True, f"документированы reproducible builds: {REPRODUCIBLE_BUILDS_DOC}"

    return (
        False,
        "не найден SLSA-аттестат, workflow slsa-verification.yml "
        f"или {REPRODUCIBLE_BUILDS_DOC}",
    )


def _validate_cyclonedx_sbom(data: dict, path: Path) -> CheckResult:
    """Проверить структуру CycloneDX SBOM."""
    if data.get("bomFormat") != "CycloneDX":
        return False, f"{path.name}: bomFormat должен быть «CycloneDX»"
    if not data.get("specVersion"):
        return False, f"{path.name}: отсутствует specVersion"
    components = data.get("components", [])
    if not isinstance(components, list):
        return False, f"{path.name}: components должен быть массивом"
    if not components:
        return False, f"{path.name}: SBOM не содержит компонентов"
    hashed = sum(
        1 for c in components if isinstance(c, dict) and c.get("hashes")
    )
    return (
        True,
        f"{path.name}: CycloneDX {data.get('specVersion')}, "
        f"{len(components)} компонент(ов), {hashed} с хэшами",
    )


def _validate_spdx_sbom(data: dict, path: Path) -> CheckResult:
    """Проверить структуру SPDX SBOM."""
    if not data.get("spdxVersion"):
        return False, f"{path.name}: отсутствует spdxVersion"
    packages = data.get("packages", [])
    if not isinstance(packages, list) or not packages:
        return False, f"{path.name}: SBOM не содержит packages"
    return True, f"{path.name}: SPDX {data.get('spdxVersion')}, {len(packages)} пакет(ов)"


def check_pur_l3(repo_path: Path) -> CheckResult:
    """
    PUR-L3 (Чистота): независимый аудит — наличие валидного SBOM.

    Поддерживаются форматы CycloneDX JSON и SPDX JSON.
    """
    for sbom_rel in SBOM_CANDIDATES:
        sbom_path = repo_path / sbom_rel
        if not sbom_path.is_file():
            continue
        data, error = _read_json(sbom_path)
        if data is None:
            return False, error
        if not isinstance(data, dict):
            return False, f"{sbom_rel}: SBOM должен быть JSON-объектом"
        if data.get("bomFormat") == "CycloneDX":
            return _validate_cyclonedx_sbom(data, sbom_path)
        if "spdxVersion" in data:
            return _validate_spdx_sbom(data, sbom_path)
        return False, f"{sbom_rel}: неизвестный формат SBOM (ожидается CycloneDX или SPDX)"

    generator = repo_path / "tools" / "generate-sbom.py"
    if generator.is_file():
        return (
            False,
            "SBOM не найден; запустите: python tools/generate-sbom.py",
        )
    return False, "SBOM (CycloneDX/SPDX) не найден и generate-sbom.py отсутствует"


def check_evo_l3(repo_path: Path) -> CheckResult:
    """
    EVO-L3 (Развитие): zero-downtime deployment конфигурация.

    Проверяет документ со стратегиями blue-green, canary, rollback и MTTR.
    """
    doc_path = repo_path / ZERO_DOWNTIME_DOC
    if not doc_path.is_file():
        return False, f"отсутствует {ZERO_DOWNTIME_DOC}"

    content = doc_path.read_text(encoding="utf-8").lower()
    missing = [kw for kw in ZERO_DOWNTIME_KEYWORDS if kw not in content]
    if missing:
        return (
            False,
            f"{ZERO_DOWNTIME_DOC}: отсутствуют разделы — {', '.join(missing)}",
        )
    return True, f"{ZERO_DOWNTIME_DOC}: стратегии zero-downtime документированы"


def _worm_storage_valid(repo_path: Path) -> CheckResult | None:
    """Проверить наличие WORM-хранилища аудит-логов."""
    logger_tool = repo_path / WORM_LOGGER_TOOL
    if logger_tool.is_file():
        for log_dir_name in WORM_LOG_DIRS:
            log_dir = repo_path / log_dir_name
            if log_dir.is_dir() and any(log_dir.iterdir()):
                entries = list(log_dir.glob("*.json"))
                return True, f"WORM-логгер + {len(entries)} записей в {log_dir_name}/"

    for log_dir_name in WORM_LOG_DIRS:
        log_dir = repo_path / log_dir_name
        if not log_dir.is_dir():
            continue
        manifest = log_dir / ".worm-manifest.json"
        entries = list(log_dir.glob("*.json"))
        if manifest.is_file() or entries:
            count = len(entries)
            if manifest.is_file():
                return True, f"WORM-хранилище {log_dir_name}/ ({count} записей, manifest)"
            return True, f"WORM-хранилище {log_dir_name}/ ({count} JSON-записей)"
    return None


def check_tra_l3(repo_path: Path) -> CheckResult:
    """
    TRA-L3 (Прозрачность): WORM audit log и API экспорта данных.
    """
    worm_result = _worm_storage_valid(repo_path)
    export_tool = repo_path / EXPORT_API_TOOL
    export_doc = repo_path / EXPORT_API_DOC

    has_export = export_tool.is_file()
    if has_export:
        content = export_tool.read_text(encoding="utf-8")
        required_endpoints = ("/passport", "/metrics", "/audit-log", "/sbom")
        missing_endpoints = [ep for ep in required_endpoints if ep not in content]
        if missing_endpoints:
            return (
                False,
                f"{EXPORT_API_TOOL}: отсутствуют endpoints {', '.join(missing_endpoints)}",
            )
    elif export_doc.is_file():
        has_export = True
    else:
        return (
            False,
            f"отсутствуют {EXPORT_API_TOOL} и {EXPORT_API_DOC}",
        )

    if worm_result is None:
        return (
            False,
            f"WORM-хранилище не найдено (ожидается {WORM_LOGGER_TOOL} "
            f"или каталог {'/'.join(WORM_LOG_DIRS)})",
        )

    worm_ok, worm_msg = worm_result
    export_label = EXPORT_API_TOOL if export_tool.is_file() else EXPORT_API_DOC
    if worm_ok and has_export:
        return True, f"{worm_msg}; API экспорта: {export_label}"
    return False, "TRA-L3: не выполнены требования WORM или export API"


def _format_verdict(ok: bool, message: str) -> str:
    """Сформировать строку вердикта для одной проверки."""
    status = "PASS" if ok else "FAIL"
    icon = "✅" if ok else "❌"
    return f"{icon}  {status:<4}  {message}"


def run_checks(repo_path: Path) -> tuple[bool, list[tuple[str, bool, str]]]:
    """Выполнить все L3-проверки."""
    checks: tuple[tuple[str, CheckFunc], ...] = (
        ("INT-L3  Целостность", check_int_l3),
        ("PUR-L3  Чистота", check_pur_l3),
        ("EVO-L3  Развитие", check_evo_l3),
        ("TRA-L3  Прозрачность", check_tra_l3),
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
    """Вывести читаемый отчёт о проверке L3 в консоль."""
    separator = "─" * 62
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║          KON-MATRIX  ·  L3 Scanner  ·  Целевой уровень       ║")
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
        print(f"  🎯  Итог: PASS — все {total} критерия L3 выполнены ({passed}/{total})")
    else:
        print(f"  ⚠️   Итог: FAIL — выполнено {passed} из {total} критериев L3")
    print()


def resolve_repo_path(argv: list[str]) -> Path:
    """Определить путь к репозиторию из аргументов CLI."""
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
