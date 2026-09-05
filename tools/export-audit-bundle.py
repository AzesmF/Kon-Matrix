#!/usr/bin/env python3
"""
Экспорт аудиторского пакета для KON-MATRIX L3 (TRA-L3).

Собирает ключевые артефакты зрелости, вычисляет их контрольные суммы
и формирует manifest.json для передачи независимому аудитору.

Запуск:
  python3 tools/export-audit-bundle.py
"""

import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = REPO_ROOT / "audit-export"

# Список критических артефактов L3 для экспорта
ARTIFACTS = {
    "passport_l3": "docs/passport/L3-PASSPORT.md",
    "sbom": "sbom/sbom.cyclonedx.json",
    "slsa_provenance": ".slsa/provenance.json",
    "worm_log": "audit-logs/worm-chain.jsonl",
    "sha256sums": "SHA256SUMS",
    "matrix_core": "docs/matrix-core.md"
}

def get_file_hash(filepath: Path) -> str:
    """Вычисляет SHA-256 хэш файла."""
    if not filepath.exists():
        return "FILE_NOT_FOUND"
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main() -> int:
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║      KON-MATRIX  ·  L3 Audit Bundle Export  ·  TRA-L3        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "export_timestamp": datetime.utcnow().isoformat() + "Z",
        "kon_matrix_version": "L3-Phase-3",
        "artifacts": {}
    }
    
    all_present = True
    
    for name, rel_path in ARTIFACTS.items():
        filepath = REPO_ROOT / rel_path
        file_hash = get_file_hash(filepath)
        
        status = "✅ FOUND" if file_hash != "FILE_NOT_FOUND" else "⚠️ MISSING (Generated in CI)"
        print(f"  {status:<25} | {rel_path}")
        
        if file_hash == "FILE_NOT_FOUND":
            all_present = False
            
        manifest["artifacts"][name] = {
            "path": rel_path,
            "sha256": file_hash,
            "status": "present" if file_hash != "FILE_NOT_FOUND" else "missing"
        }

    # Сохраняем манифест
    manifest_path = OUTPUT_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print("\n" + "─" * 62)
    if all_present:
        print("  ✅ ИТОГ: Все артефакты L3 найдены. Пакет готов к передаче аудитору.")
        print(f"  📁 Пакет сохранён в: {OUTPUT_DIR}")
        print(f"  📄 Манифест: {manifest_path}")
        return 0
    else:
        print("  ⚠️ ИТОГ: Некоторые артефакты отсутствуют (возможно, требуют генерации в CI).")
        print(f"  📁 Частичный пакет сохранён в: {OUTPUT_DIR}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
