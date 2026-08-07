#!/usr/bin/env python3
"""
Auto Changelog Generator for Kon-Matrix
Запускается из GitHub Actions при публикации релиза.
"""

import subprocess
import os
from datetime import date
from pathlib import Path

def run_cmd(cmd: list) -> str:
    """Выполняет команду и возвращает вывод."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def main():
    tag = os.environ.get("GITHUB_REF_NAME", "")
    if not tag:
        print("ERROR: GITHUB_REF_NAME not set")
        return 1
    
    today = date.today().isoformat()
    print(f"Updating CHANGELOG for tag: {tag}")
    
    # Получаем предыдущий тег
    try:
        prev = run_cmd(["git", "describe", "--tags", "--abbrev=0", "HEAD^"])
        if not prev:
            prev = ""
    except Exception:
        prev = ""
    
    print(f"Previous tag: {prev if prev else 'None (initial release)'}")
    
    # Получаем список коммитов между тегами
    if prev:
        commits = run_cmd(["git", "log", "--pretty=format:- %s (%h)", "--reverse", f"{prev}..HEAD"])
    else:
        commits = run_cmd(["git", "log", "--pretty=format:- %s (%h)", "--reverse"])
    
    if not commits:
        print("WARNING: No commits found")
        commits = "- Initial release"
    
    # Формируем новую запись
    new_entry = f"## [{tag}] - {today}\n\n### Changes\n{commits}\n\n"
    
    # Читаем текущий CHANGELOG
    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        print("ERROR: CHANGELOG.md not found")
        return 1
    
    content = changelog_path.read_text()
    
    # Вставляем после первой строки (заголовка)
    lines = content.split("\n", 1)
    if len(lines) == 2:
        new_content = lines[0] + "\n\n" + new_entry + lines[1]
    else:
        new_content = new_entry + content
    
    # Записываем обратно
    changelog_path.write_text(new_content)
    print("CHANGELOG.md updated successfully")
    
    # Обновляем SHA256SUMS
    print("Updating SHA256SUMS...")
    find_cmd = [
        "find", ".", "-type", "f",
        "(", "-name", "*.md", "-o", "-name", "*.py", "-o", "-name", "*.toml", "-o", "-name", "*.yml", ")",
        "!", "-path", "./.git/*", "!", "-name", "SHA256SUMS",
        "-exec", "sha256sum", "{}", ";"
    ]
    sha_output = run_cmd(find_cmd)
    
    Path("SHA256SUMS").write_text(sha_output + "\n" if sha_output else "")
    print("SHA256SUMS updated successfully")
    
    return 0

if __name__ == "__main__":
    exit(main())
