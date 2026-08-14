#!/usr/bin/env python3
"""
Генератор SBOM в формате CycloneDX JSON для проектов KON-MATRIX.

Анализирует pyproject.toml, собирает прямые и транзитивные зависимости (через pip),
вычисляет SHA-256 хэши компонентов.

Запуск: python3 tools/generate-sbom.py [--output sbom/sbom.cyclonedx.json] [путь_к_репо]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None  # type: ignore[assignment,misc]

DEFAULT_OUTPUT = "sbom/sbom.cyclonedx.json"
CYCLONEDX_SPEC_VERSION = "1.5"
LOGGER = logging.getLogger("kon-matrix.generate-sbom")

PROJECT_NAME_PATTERN = re.compile(r'^name\s*=\s*"([^"]+)"', re.MULTILINE)
PROJECT_VERSION_PATTERN = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)
PROJECT_DESC_PATTERN = re.compile(r'^description\s*=\s*"([^"]+)"', re.MULTILINE)
PROJECT_DEPS_PATTERN = re.compile(r"^dependencies\s*=\s*\[(.*?)\]", re.MULTILINE | re.DOTALL)
DEP_STRING_PATTERN = re.compile(r'"([^"]+)"')


def configure_logging() -> None:
    """Настроить structured logging в JSON-формате."""
    logging.basicConfig(
        level=logging.INFO,
        format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )


def _load_pyproject_regex(content: str) -> dict[str, Any]:
    """Fallback-парсер pyproject.toml для Python < 3.11."""
    if "[project]" not in content:
        raise ValueError("pyproject.toml: отсутствует секция [project]")
    project_block = content.split("[project]", 1)[1]
    for section in ("[build-system]", "[tool.", "["):
        if section in project_block:
            project_block = project_block.split(section, 1)[0]
            break

    name_match = PROJECT_NAME_PATTERN.search(project_block)
    version_match = PROJECT_VERSION_PATTERN.search(project_block)
    desc_match = PROJECT_DESC_PATTERN.search(project_block)
    deps_match = PROJECT_DEPS_PATTERN.search(project_block)

    if not name_match:
        raise ValueError("pyproject.toml: не найден ключ name в [project]")

    dependencies: list[str] = []
    if deps_match:
        dependencies = DEP_STRING_PATTERN.findall(deps_match.group(1))

    return {
        "name": name_match.group(1),
        "version": version_match.group(1) if version_match else "0.0.0",
        "description": desc_match.group(1) if desc_match else "",
        "dependencies": dependencies,
    }


def load_pyproject(repo_path: Path) -> dict[str, Any]:
    """
    Загрузить и распарсить pyproject.toml.

    Raises:
        FileNotFoundError: если файл отсутствует.
        ValueError: если секция [project] не найдена.
    """
    pyproject_path = repo_path / "pyproject.toml"
    if not pyproject_path.is_file():
        raise FileNotFoundError(f"pyproject.toml не найден в {repo_path}")

    if tomllib is not None:
        with pyproject_path.open("rb") as handle:
            data = tomllib.load(handle)
        project = data.get("project")
        if not isinstance(project, dict):
            raise ValueError("pyproject.toml: отсутствует секция [project]")
        return project

    return _load_pyproject_regex(pyproject_path.read_text(encoding="utf-8"))


def compute_sha256(path: Path) -> str:
    """Вычислить SHA-256 хэш файла."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_hash_entry(sha256: str) -> dict[str, str]:
    """Сформировать запись хэша CycloneDX."""
    return {"alg": "SHA-256", "content": sha256}


def build_root_component(project: dict[str, Any], repo_path: Path) -> dict[str, Any]:
    """Создать компонент для самого проекта."""
    pyproject_path = repo_path / "pyproject.toml"
    component: dict[str, Any] = {
        "type": "application",
        "name": project.get("name", repo_path.name),
        "version": project.get("version", "0.0.0"),
        "description": project.get("description", ""),
        "purl": f"pkg:pypi/{project.get('name', repo_path.name)}@{project.get('version', '0.0.0')}",
        "bom-ref": f"pkg:pypi/{project.get('name', repo_path.name)}@{project.get('version', '0.0.0')}",
    }
    if pyproject_path.is_file():
        component["hashes"] = [make_hash_entry(compute_sha256(pyproject_path))]
    return component


def resolve_dependencies_pip(dependencies: list[str]) -> list[dict[str, Any]]:
    """
    Разрешить транзитивные зависимости через pip install --dry-run --report.

    Returns:
        Список компонентов CycloneDX для каждого установленного пакета.
    """
    if not dependencies:
        return []

    report_path = Path("/tmp/kon-matrix-pip-report.json")
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--dry-run",
        "--report",
        str(report_path),
        *dependencies,
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired:
        LOGGER.warning("pip --report превысил лимит времени; используются только прямые зависимости")
        return _direct_dependency_components(dependencies)

    if result.returncode != 0 or not report_path.is_file():
        LOGGER.warning(
            "pip --report завершился с кодом %s: %s",
            result.returncode,
            result.stderr.strip()[:200],
        )
        return _direct_dependency_components(dependencies)

    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _direct_dependency_components(dependencies)

    components: list[dict[str, Any]] = []
    for item in report.get("install", []):
        metadata = item.get("metadata") or {}
        name = metadata.get("name") or item.get("download_info", {}).get("url", "unknown")
        version = metadata.get("version", "unknown")
        purl = f"pkg:pypi/{name}@{version}"
        comp: dict[str, Any] = {
            "type": "library",
            "name": name,
            "version": version,
            "purl": purl,
            "bom-ref": purl,
        }
        if metadata.get("sha256"):
            comp["hashes"] = [make_hash_entry(metadata["sha256"])]
        components.append(comp)
    return components


def _direct_dependency_components(dependencies: list[str]) -> list[dict[str, Any]]:
    """Сформировать компоненты только для прямых зависимостей (fallback)."""
    components: list[dict[str, Any]] = []
    for dep in dependencies:
        name = re_split_dep_name(dep)
        purl = f"pkg:pypi/{name}"
        components.append(
            {
                "type": "library",
                "name": name,
                "version": "unspecified",
                "purl": purl,
                "bom-ref": purl,
            }
        )
    return components


def re_split_dep_name(dep: str) -> str:
    """Извлечь имя пакета из строки зависимости PEP 508."""
    for separator in ("==", ">=", "<=", "!=", "~=", ">", "<", "[", ";"):
        if separator in dep:
            return dep.split(separator, 1)[0].strip()
    return dep.strip()


def hash_tooling_files(repo_path: Path) -> list[dict[str, Any]]:
    """Добавить компоненты для ключевых инструментов репозитория с хэшами."""
    tool_paths = sorted(repo_path.glob("tools/*.py"))
    components: list[dict[str, Any]] = []
    for tool_path in tool_paths:
        rel = tool_path.relative_to(repo_path).as_posix()
        components.append(
            {
                "type": "file",
                "name": rel,
                "version": "local",
                "purl": f"pkg:generic/{rel}@local",
                "bom-ref": f"pkg:generic/{rel}@local",
                "hashes": [make_hash_entry(compute_sha256(tool_path))],
            }
        )
    return components


def generate_sbom(repo_path: Path) -> dict[str, Any]:
    """
    Сгенерировать CycloneDX SBOM для репозитория.

    Args:
        repo_path: Корень Git-репозитория.

    Returns:
        Словарь CycloneDX BOM.
    """
    project = load_pyproject(repo_path)
    dependencies = project.get("dependencies", [])
    if not isinstance(dependencies, list):
        raise ValueError("pyproject.toml: [project].dependencies должен быть массивом")

    root = build_root_component(project, repo_path)
    dep_components = resolve_dependencies_pip(dependencies)
    tool_components = hash_tooling_files(repo_path)

    all_components = [root, *dep_components, *tool_components]
    # Дедупликация по bom-ref
    seen: set[str] = set()
    unique_components: list[dict[str, Any]] = []
    for comp in all_components:
        ref = comp.get("bom-ref", comp.get("name", ""))
        if ref in seen:
            continue
        seen.add(ref)
        unique_components.append(comp)

    now = datetime.now(timezone.utc).isoformat()
    return {
        "bomFormat": "CycloneDX",
        "specVersion": CYCLONEDX_SPEC_VERSION,
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": now,
            "tools": [
                {
                    "vendor": "KON-MATRIX",
                    "name": "generate-sbom.py",
                    "version": "0.1.0",
                }
            ],
            "component": root,
        },
        "components": unique_components,
    }


def write_sbom(sbom: dict[str, Any], output_path: Path) -> None:
    """Записать SBOM в JSON-файл."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(sbom, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Разобрать аргументы командной строки."""
    parser = argparse.ArgumentParser(description="Генератор CycloneDX SBOM для KON-MATRIX")
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Путь к корню репозитория (по умолчанию: текущая директория)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=DEFAULT_OUTPUT,
        help=f"Путь к выходному файлу (по умолчанию: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Точка входа CLI."""
    configure_logging()
    args = parse_args(argv or sys.argv[1:])
    repo_path = Path(args.repo_path).expanduser().resolve()
    output_path = (repo_path / args.output).resolve()

    try:
        sbom = generate_sbom(repo_path)
        write_sbom(sbom, output_path)
    except (FileNotFoundError, ValueError, OSError) as exc:
        LOGGER.error("Ошибка генерации SBOM: %s", exc)
        print(f"❌  {exc}", file=sys.stderr)
        return 1

    component_count = len(sbom.get("components", []))
    hashed = sum(1 for c in sbom["components"] if c.get("hashes"))
    print(f"✅  SBOM записан: {output_path.relative_to(repo_path)}")
    print(f"    CycloneDX {CYCLONEDX_SPEC_VERSION} · {component_count} компонент(ов) · {hashed} с хэшами")
    return 0


if __name__ == "__main__":
    sys.exit(main())
