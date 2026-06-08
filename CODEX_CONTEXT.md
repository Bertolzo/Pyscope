# ADO — Architectural Dynamics Observatory

## Contexto do Projeto

Sistema formal para observação, classificação e análise da dinâmica arquitetural
de software. Três artefatos distintos que **não podem ser confundidos**:

1. **FASM** — Modelo formal (ontologia, teoria, axiomas, fenómenos, espaço de
   estados, métricas, invariantes). Define o *que* observar.
2. **AGS** — Implementação (GraphBuilder, parsers, métricas engine, banco).
   Define *como* observar.
3. **ADO** — Observatório (ObservationSnapshot, RegimeClassification,
   protocolos C0/C1/C2). Conecta observação → FASM → evidência.
   **Não cria teoria nem implementação.**

Documentos FASM NÃO contêm código Python nem paths de implementação AGS.
AGS NÃO cria conceitos — apenas implementa.

## Estado Atual

**Baseline:** v2.0.0 (frozen 2026-06-04)
**Status da Sessão:** C1.0 concluído — PARTIAL (v2.1.0 MINOR recomendado)

## O Que Foi Construído

### Bridge Layer (ags/core/observation/)

```
ags/core/observation/
├── __init__.py          # Exports: ObservationSnapshot, compute_observation_snapshot,
│                        #          RegimeClassification, classify_from_snapshot
├── primitives.py        # ObservationSnapshot + compute_observation_snapshot()
└── classification.py    # RegimeClassification + classify_from_snapshot()
```

**ObservationSnapshot** (dataclass):
- Métricas [0,1]: cross_domain_ratio, intra_domain_ratio, file_level_leakage, cycle_density
- observation_quality [0,1]: 1 - unknown_edges / total_edges (0 se total_edges==0)
- Contagens: total_nodes, total_edges, cross_domain_edges, intra_domain_edges,
  unknown_unresolved_edges, unknown_dynamic_edges
- Proveniência: parser_version, graph_builder_version, timestamp

**RegimeClassification** (dataclass frozen):
- regime, nearest_regime, second_nearest_regime (RegimeName)
- distance_1 (com penalidade de tamanho), structural_distance_1 (só métricas)
- margin = distance_2 - distance_1
- confidence = observation_quality / (1 + distance_1)
- all_distances: sorted list of (name, distance) para todos os 11 regimes

**classify_from_snapshot(snapshot, graph_size=None, size_mode="synthetic")**:
- "synthetic": targets SMALL=6, MEDIUM=20, LARGE=50, divisor 20
- "real": targets ln(15), ln(60), ln(500), divisor ln(2)

**compute_observation_snapshot(graph, total_imports_attempted=None)**:
- Pula edges module-to-module (import_type=="module")
- Pula self-loops (u == v)
- unknown_dynamic = total_imports_attempted - total_edges - unknown_unresolved

### Testes (256 total, 0 falhas)

- tests/test_observation.py (22): empty, self-loop, DAG, cycles, domains, quality
- tests/test_classification.py (18): empty, perfect, leaky, coupled, invariants

## C1.0 — Observações Reais

Script: tools/c1_observe.py <name> <repo_url>

### Resultados

| Projeto | Files | Edges | cross | intra | cycles | Regime (estrutural) | Struct-Dist |
|---------|-------|-------|-------|-------|--------|--------------------|-------------|
| Requests | 37 | 81 | 0.00 | 1.00 | 0.58 | MIXED | 2.65 |
| FastAPI | 1120 | 1576 | 0.83 | 0.17 | 0.04 | MIXED | 2.54 |
| Celery | 416 | 1130 | 0.42 | 0.58 | 0.12 | COUPLED | 0.99 |
| Airflow* | 7362 | 29 | 0.00 | 1.00 | 0.00 | MODULAR_LARGE | 1.00 |

*Airflow sub-observado (parser estático não capta imports dinâmicos).

### Gate Check

- quality ≥ 0.90: 4/4 PASS
- margin ≥ 0.10: 4/4 PASS
- struct-dist ≤ 0.25: 0/4 FAIL (menor: Celery 0.99)

### Descobertas Principais

1. **Regime estrutural difere do total** — tamanho domina a distância total.
   Celery é estruturalmente COUPLED (não ENTANGLED_LARGE). Usar
   `structural_distance_1` para decisões.

2. **Ω_synth não cobre projetos reais** — Nenhum regime atual tem
   intra < 0.4 (FastAPI tem 0.17) ou cycles > 0.5 (Requests tem 0.58).

3. **observation_quality é enganosa sem total_imports_attempted** —
   Airflow reporta quality=1.0 mas só 29/7362 edges foram detectados.

4. **Django OOM** — GraphBuilder não escala para 150k+ LOC.

### Recomendações v2.1.0

Adicionar à REGIME_TAXONOMY:
- MIXED_CYCLIC: cross 0.0-0.2, intra 0.8-1.0, cycles 0.4-0.7
- CROSS_DOMINANT: cross 0.7-0.9, intra 0.1-0.3, cycles 0.0-0.1
- COUPLED_BALANCED: cross 0.4-0.6, intra 0.4-0.6, cycles 0.1-0.2

### Arquivos Exportados

- c1_requests_result.json, c1_fastapi_result.json
- c1_celery_result.json, c1_airflow_result.json

## Decisões de Design

- **ratio formulas** (não scores [0,100]): bridge layer usa [0,1] como C0
- **cycle_density = edges_in_cycles / total_edges** (não cyclomatic complexity)
- **intra_domain_ratio direto** (não 1 - cross): revela classification gaps
- **confidence = quality / (1 + distance)**: mapeia qualquer distância a (0, 1]
- **Self-loops ignorados**: não representam dependência arquitetural

## Convenções de Código

- Sem comentários inline em código
- FASM/AGS/ADO não se misturam
- Scientific Change Protocol (8 perguntas) antes de qualquer mudança
- Nenhum MAJOR bump sem 8 perguntas respondidas

## Próximos Passos (Pendentes)

1. C2.0 — expandir REGIME_TAXONOMY (MIXED_CYCLIC, CROSS_DOMINANT)
2. Implementar total_imports_attempted no parser AGS
3. Ajustar gate check para struct-dist ≤ 0.50
4. Django: modo streaming no GraphBuilder
5. Gerar dados sintéticos C2.0
6. Re-observar projetos contra novo Ω_synth

## Comandos Úteis

```bash
# Rodar testes
python -m pytest tests/ -q --no-cov

# Observar projeto real
python tools/c1_observe.py <name> <repo_url>

# Rodar suíte completa
python -m pytest --no-cov -q
```
