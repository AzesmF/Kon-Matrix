#!/usr/bin/env python3
"""
Верификация SLSA-аттестатов для KON-MATRIX L3 (INT-L3).

Проверяет наличие, структуру и минимальный уровень SLSA (Level 1+)
для in-toto Statement / SLSA Provenance v1.

Запуск:
  python3 tools/verify-slsa.py [путь_к_репозиторию]
  python3 tools/verify-slsa.py --attestation .slsa/provenance.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

SLSA_PROVENANCE_V1 = "https://slsa.dev/provenance/v1"
IN_TOTO_STATEMENT = "https://in-toto.io/Statement/v1"
MIN_SLSA_LEVEL = 1

ATTESTATION_SEARCH_PATHS: tuple[str, ...] = (
    ".slsa/provenance.json",
    ".slsa/attestation.json",
    "artifacts/slsa/provenance.json",
)

REQUIRED_PREDICATE_FIELDS: tuple[str, ...] = (
    "buildType",
    "builder",
    "invocation",
    "materials",
)

LOGGER = logging.getLogger("kon-matrix.verify-slsa")


def configure_logging() -> None:
    """Настроить structured logging в JSON-формате."""
    logging.basicConfig(
        level=logging.INFO,
        format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )


def load_attestation(path: Path) -> tuple[dict[str, Any] | None, str]:
    """
    Загрузить SLSA-аттестат из JSON-файла.

    Returns:
        Кортеж (данные или None, сообщение об ошибке).
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, f"не удалось прочитать {path}: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"невалидный JSON в {path.name}: {exc}"
    if not isinstance(data, dict):
        return None, f"{path.name}: аттестат должен быть JSON-объектом"
    return data, ""


def _extract_predicate(data: dict[str, Any]) -> dict[str, Any] | None:
    """Извлечь predicate из in-toto Statement или плоского формата."""
    if data.get("_type") == IN_TOTO_STATEMENT:
        predicate = data.get("predicate")
        return predicate if isinstance(predicate, dict) else None
    if data.get("predicateType") == SLSA_PROVENANCE_V1:
        predicate = data.get("predicate")
        return predicate if isinstance(predicate, dict) else None
    if "buildType" in data:
        return data
    return None


def infer_slsa_level(data: dict[str, Any]) -> int:
    """
    Определить уровень SLSA аттестата (эвристика для Level 1–2).

    Level 1: provenance с buildType и materials.
    Level 2: builder.id указывает на hosted CI + digest subjects или подпись.
    """
    predicate = _extract_predicate(data)
    if predicate is None:
        return 0

    level = 0
    if predicate.get("buildType") and predicate.get("materials"):
        level = 1

    builder = predicate.get("builder")
    if isinstance(builder, dict) and builder.get("id"):
        subjects = data.get("subject", [])
        has_digest = any(
            isinstance(subject, dict) and subject.get("digest")
            for subject in (subjects if isinstance(subjects, list) else [])
        )
        if has_digest:
            level = max(level, 2)

    if (data.get("signature") or data.get("payloadSignature")) and level >= 1:
        level = max(level, 2)

    return level


def validate_attestation_structure(data: dict[str, Any], path: Path) -> tuple[bool, str]:
    """
    Проверить структуру SLSA Provenance attestation.

    Returns:
        Кортеж (валиден, сообщение).
    """
    if data.get("_type") != IN_TOTO_STATEMENT:
        return False, f"{path.name}: ожидается in-toto Statement v1 (_type)"

    predicate_type = data.get("predicateType")
    if predicate_type != SLSA_PROVENANCE_V1:
        return (
            False,
            f"{path.name}: predicateType должен быть {SLSA_PROVENANCE_V1!r}, "
            f"получено {predicate_type!r}",
        )

    subjects = data.get("subject")
    if not isinstance(subjects, list) or not subjects:
        return False, f"{path.name}: отсутствует непустой массив subject"

    predicate = _extract_predicate(data)
    if predicate is None:
        return False, f"{path.name}: predicate отсутствует или повреждён"

    missing = [field for field in REQUIRED_PREDICATE_FIELDS if field not in predicate]
    if missing:
        return (
            False,
            f"{path.name}: в predicate отсутствуют поля: {', '.join(missing)}",
        )

    materials = predicate.get("materials")
    if not isinstance(materials, list) or not materials:
        return False, f"{path.name}: materials должен быть непустым массивом"

    return True, f"{path.name}: структура SLSA Provenance v1 валидна"


def validate_signature_presence(data: dict[str, Any], path: Path) -> tuple[bool, str]:
    """
    Проверить наличие блока подписи (Level 2 readiness).

    Полная криптографическая верификация требует внешних ключей;
    здесь проверяем декларацию подписи в аттестате.
    """
    if data.get("signature") or data.get("payloadSignature"):
        return True, f"{path.name}: обнаружена декларация подписи"
    return False, f"{path.name}: подпись не объявлена (допустимо для SLSA Level 1)"


def verify_attestation(path: Path, min_level: int = MIN_SLSA_LEVEL) -> tuple[bool, str]:
    """
    Полная верификация одного SLSA-аттестата.

    Args:
        path: Путь к JSON-файлу аттестата.
        min_level: Минимально допустимый уровень SLSA.

    Returns:
        Кортеж (успех, отчёт).
    """
    data, error = load_attestation(path)
    if data is None:
        return False, error

    ok, structure_msg = validate_attestation_structure(data, path)
    if not ok:
        return False, structure_msg

    level = infer_slsa_level(data)
    if level < min_level:
        return (
            False,
            f"{path.name}: SLSA Level {level} < требуемого Level {min_level}",
        )

    _sig_ok, sig_msg = validate_signature_presence(data, path)
    predicate = _extract_predicate(data) or {}
    builder_id = predicate.get("builder", {}).get("id", "unknown")

    report = f"{structure_msg}; SLSA Level {level}; builder={builder_id!r}; {sig_msg}"
    LOGGER.info("Verified %s: level=%s", path, level)
    return True, report


def find_attestations(repo_path: Path) -> list[Path]:
    """Найти SLSA-аттестаты в стандартных расположениях."""
    found: list[Path] = []
    for rel in ATTESTATION_SEARCH_PATHS:
        candidate = repo_path / rel
        if candidate.is_file():
            found.append(candidate)
    for pattern in (".slsa/**/*.json", "artifacts/slsa/**/*.json"):
        for candidate in repo_path.glob(pattern):
            if candidate.is_file() and candidate not in found:
                found.append(candidate)
    return sorted(set(found))


def print_report(results: list[tuple[Path, bool, str]]) -> bool:
    """Вывести отчёт верификации. Returns: все успешны."""
    separator = "─" * 62
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         KON-MATRIX  ·  SLSA Verification  ·  INT-L3          ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(separator)
    all_ok = True
    for path, ok, message in results:
        icon = "✅" if ok else "❌"
        status = "PASS" if ok else "FAIL"
        print(f"  {icon}  {status:<4}  {path.name}")
        print(f"         {message}")
        print(separator)
        if not ok:
            all_ok = False
    passed = sum(1 for _, ok, _ in results if ok)
    print(f"\n  Итог: {passed}/{len(results)} аттестат(ов) прошли верификацию\n")
    return all_ok


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Разобрать аргументы CLI."""
    parser = argparse.ArgumentParser(description="Верификация SLSA-аттестатов KON-MATRIX")
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Путь к корню репозитория",
    )
    parser.add_argument(
        "--attestation",
        "-a",
        action="append",
        dest="attestations",
        help="Путь к конкретному аттестату (можно указать несколько раз)",
    )
    parser.add_argument(
        "--min-level",
        type=int,
        default=MIN_SLSA_LEVEL,
        help=f"Минимальный SLSA Level (по умолчанию: {MIN_SLSA_LEVEL})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Точка входа CLI."""
    configure_logging()
    args = parse_args(argv or sys.argv[1:])
    repo_path = Path(args.repo_path).expanduser().resolve()

    if args.attestations:
        paths = [Path(p).expanduser().resolve() for p in args.attestations]
    else:
        paths = find_attestations(repo_path)

    if not paths:
        print("❌  SLSA-аттестаты не найдены", file=sys.stderr)
        return 1

    results: list[tuple[Path, bool, str]] = []
    for path in paths:
        ok, message = verify_attestation(path, args.min_level)
        results.append((path, ok, message))

    all_ok = print_report(results)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
