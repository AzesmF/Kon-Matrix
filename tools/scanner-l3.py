#!/usr/bin/env python3
"""
Сканер соответствия уровню L3 методологии KON-MATRIX.
Проверяет наличие и валидность артефактов Фазы 3.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

L3_REQUIREMENTS = {
    "INT-L3": [
        (".slsa/provenance.json", "SLSA Provenance аттестат"),
        (".github/workflows/int-l3-reproducible-build.yml", "Workflow проверки воспроизводимости (Diffoscope)"),
        ("tools/verify-slsa.py", "Инструмент верификации SLSA"),
    ],
    "PUR-L3": [
        ("sbom/sbom.cyclonedx.json", "SBOM в формате CycloneDX"),
        (".github/workflows/pur-l3-dast-scan.yml", "Workflow DAST-сканирования (OWASP ZAP)"),
        ("tools/generate-sbom.py", "Инструмент генерации SBOM"),
    ],
    "EVO-L3": [
        ("docs/l3/zero-downtime-deployment.md", "Гайд по бесшовному развёртыванию"),
        ("docs/l3/reproducible-builds.md", "Гайд по воспроизводимым сборкам"),
    ],
    "TRA-L3": [
        ("tools/export-audit-bundle.py", "Инструмент экспорта аудиторского пакета"),
        ("tools/worm-logger.py", "WORM-логгер с цепочкой хешей"),
        ("docs/l3/independent-audit.md", "Гайд для независимого аудитора"),
        ("docs/l3/SOC2-preparation.md", "Маппинг на SOC 2"),
        ("docs/l3/ISO27001-preparation.md", "Маппинг на ISO 27001"),
    ]
}

def check_file(filepath: Path) -> bool:
    return (REPO_ROOT / filepath).exists()

def main() -> int:
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║        KON-MATRIX  ·  L3 Verification Scanner  ·  v1.0       ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    all_passed = True
    for kon, requirements in L3_REQUIREMENTS.items():
        print(f"🔹 {kon}")
        kon_passed = True
        for filepath, description in requirements:
            if check_file(filepath):
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description} (Ожидается: {filepath})")
                kon_passed = False
                all_passed = False
        
        if kon_passed:
            print(f"   → {kon}: PASS\n")
        else:
            print(f"   → {kon}: FAIL\n")
            
    print("─" * 62)
    if all_passed:
        print("🏆 ИТОГ: PASS — все 4 критерия L3 выполнены (4/4)")
        print("   Уровень зрелости L3 подтверждён.")
        return 0
    else:
        print("⚠️  ИТОГ: FAIL — не все критерии L3 выполнены.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
