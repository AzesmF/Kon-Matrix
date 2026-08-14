# Zero-Downtime Deployment — KON-MATRIX L3

**Кон:** EVO-L3 (Развитие) — бесшовная эволюция без остановки сервиса  
**Цель:** обновлять систему без простоя, с контролируемым риском и быстрым откатом.

---

## Стратегии развёртывания

### Blue-Green Deployment

Две идентичные среды: **Blue** (текущая prod) и **Green** (новая версия).

```
                    ┌─────────┐
  Traffic ─────────►│  Blue   │  v1.0 (active)
                    └─────────┘
                    ┌─────────┐
                    │  Green  │  v1.1 (idle → health check → switch)
                    └─────────┘
```

**Процесс:**
1. Развернуть v1.1 в Green-среде.
2. Выполнить **health check** (smoke tests, L1/L2/L3 scanners).
3. Переключить трафик (DNS / load balancer / GitHub Pages alias).
4. Blue остаётся для **rollback** в течение N часов.

**Применение в Kon-Matrix:**
- GitHub Pages: preview deployment на `gh-pages-preview` → switch на `gh-pages`.
- CI: `kon-matrix-l1-check.yml` как gate перед switch.

---

### Canary Releases

Постепенное направление трафика на новую версию.

| Этап | % трафика на v1.1 | Длительность | Критерий продвижения |
|------|-------------------|--------------|----------------------|
| 1 | 5% | 15 мин | error rate < 0.1% |
| 2 | 25% | 30 мин | p99 latency stable |
| 3 | 50% | 1 h | MTTR events = 0 |
| 4 | 100% | — | full promotion |

**Мониторинг canary:**
- `tools/metrics-l2.py` — базовые метрики репозитория
- GitHub Actions status — CI pass rate
- Custom alerts — webhook на failed L3 scanner

---

## Rollback процедуры

### Автоматический rollback (triggers)

| Trigger | Действие | SLA |
|---------|----------|-----|
| Health check fail × 3 | Revert traffic to Blue | < 2 мин |
| L3 scanner FAIL post-deploy | Block promotion + alert | < 1 мин |
| Error rate > 1% | Canary halt at current % | < 3 мин |

### Ручной rollback

```bash
# 1. Переключить трафик обратно
git checkout v0.2.1   # последний stable tag

# 2. Запустить верификацию
python tools/scanner-l3.py
python tools/verify-slsa.py

# 3. Зафиксировать инцидент в WORM-логе
python tools/worm-logger.py append \
  --event "deploy.rollback" \
  --detail '{"from":"v0.3.0","to":"v0.2.1","reason":"health_check_fail"}' \
  --actor "oncall"
```

---

## Health Checks

### Pre-promotion gates (Kon-Matrix CI)

| Check | Команда | Критерий |
|-------|---------|----------|
| L1 Integrity | `python tools/scanner-l1.py` | 4/4 PASS |
| L3 Target | `python tools/scanner-l3.py` | ≥ 3/4 PASS |
| SLSA | `python tools/verify-slsa.py` | Level ≥ 1 |
| SBOM fresh | `python tools/generate-sbom.py` | no diff in CI |
| WORM chain | `python tools/worm-logger.py verify` | chain valid |

### Runtime health check (эмуляция)

```yaml
# .github/workflows/health-check.yml (концепт)
- name: Health check
  run: |
    python tools/scanner-l1.py || exit 1
    python tools/worm-logger.py verify || exit 1
```

---

## MTTR метрики (Mean Time To Recovery)

**Целевой MTTR для L3: < 5 мин**

| Метрика | Определение | Цель L3 |
|---------|-------------|---------|
| **MTTR** | Среднее время восстановления после инцидента | < 5 мин |
| **MTTD** | Mean Time To Detect | < 1 мин |
| **Deployment frequency** | Релизов в неделю | ≥ 1 |
| **Change failure rate** | % деплоев с rollback | < 5% |
| **Lead time** | Commit → production | < 1 день |

### Сбор метрик (Kon-Matrix)

```bash
# Базовые метрики репозитория
python tools/metrics-l2.py

# WORM-лог: время от deploy.fail до deploy.rollback
python tools/worm-logger.py export --output audit-logs/mttr-report.json
```

### Формула MTTR

```
MTTR = Σ(recovery_time_per_incident) / count(incidents)
```

Записывайте каждый инцидент через `worm-logger.py append --event "incident.resolved"`.

---

## Deployment Checklist (EVO-L3)

- [ ] Canary plan документирован (таблица % трафика)
- [ ] Blue-green среда настроена
- [ ] Health checks проходят в CI
- [ ] Rollback runbook протестирован
- [ ] MTTR < 5 мин (подтверждено WORM-логами)
- [ ] `python tools/scanner-l3.py` → EVO-L3 PASS

---

## Связанные документы

- [L3 Overview](./README.md)
- [Reproducible Builds](./reproducible-builds.md)
- [L3 Passport](../passport/L3-PASSPORT.md)
- [tools/worm-logger.py](../../tools/worm-logger.py)
