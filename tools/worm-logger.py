#!/usr/bin/env python3
"""
WORM Logger для KON-MATRIX L3 (TRA-L3).
Реализует простую цепочку хешей (hash chain) для защиты логов от изменений.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("audit-logs/worm-chain.jsonl")

def ensure_dir():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def get_last_hash():
    if not LOG_FILE.exists():
        return "0" * 64
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if not lines:
            return "0" * 64
        last_entry = json.loads(lines[-1])
        return last_entry.get("current_hash", "0" * 64)

def append_event(event: str, detail: dict, actor: str):
    ensure_dir()
    prev_hash = get_last_hash()
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    payload = {
        "timestamp": timestamp,
        "actor": actor,
        "event": event,
        "detail": detail,
        "previous_hash": prev_hash
    }
    
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    current_hash = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
    
    entry = {**payload, "current_hash": current_hash}
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"✅ Событие '{event}' записано. Hash: {current_hash[:16]}...")

def verify_chain():
    if not LOG_FILE.exists():
        print("ℹ️ Лог-файл не найден. Цепочка пуста.")
        return True
        
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        entry = json.loads(line)
        expected_prev = "0" * 64 if i == 0 else json.loads(lines[i-1])["current_hash"]
        
        if entry["previous_hash"] != expected_prev:
            print(f"❌ Нарушение целостности в записи {i}!")
            return False
            
        # Пересчитываем хеш для проверки
        payload = {k: v for k, v in entry.items() if k != "current_hash"}
        payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        if hashlib.sha256(payload_str.encode('utf-8')).hexdigest() != entry["current_hash"]:
            print(f"❌ Хеш записи {i} не совпадает!")
            return False
            
    print(f"✅ Цепочка из {len(lines)} записей валидна. Целостность (TRA-L3) подтверждена.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WORM Logger KON-MATRIX")
    subparsers = parser.add_subparsers(dest="command")
    
    append_p = subparsers.add_parser("append")
    append_p.add_argument("--event", required=True)
    append_p.add_argument("--detail", default="{}")
    append_p.add_argument("--actor", default="system")
    
    subparsers.add_parser("verify")
    
    args = parser.parse_args()
    
    if args.command == "append":
        append_event(args.event, json.loads(args.detail), args.actor)
    elif args.command == "verify":
        sys.exit(0 if verify_chain() else 1)
    else:
        parser.print_help()
