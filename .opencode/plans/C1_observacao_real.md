# C1.0 — Real-World Transfer Sanity Check

**Baseline:** v2.0.0 (frozen 2026-06-04)
**Status:** Planejado (bridge layer necessária)
**Pré-requisito:** `ObservationSnapshot` + `compute_observation_snapshot()` no AGS

---

## Objetivo

Avaliar se o espaço de regimes sintéticos definido em C0 possui
correspondência observável em sistemas de software reais.

Esta etapa existe para **falsificar a hipótese de transferência**
antes de investir em análise longitudinal.

---

## Pergunta Central

> O espaço fenomenológico criado em C0 (Ω_synth, 11 regimes)
> possui correspondência observável no mundo real?

Ou, na forma operacional:

> Dado um projeto real (Django, FastAPI, Celery, Airflow, Requests),
> podemos extrair um ObservationSnapshot e classificá-lo dentro
> de Ω_synth com confiança ≥ 0.70?

---

## Pré-requisito Técnico: Bridge Layer

### Problema Descoberto

O sistema sintético (C0) computa métricas primitivas como **razões [0,1]**:

- `ACP = cross_domain_edges / total_edges`
- `DCI = 1 - cross_module_ratio`
- `cycle_density = min(1, cyclomatic / max(e,1))`

O sistema real (AGS) computa métricas como **scores [0,100]**:

- `ACP = 100 - (cross / max_acceptable) * 50` (penalidade)
- `DCI = 100 - contamination_ratio * 100` (score)
- `cycle_density` — **não computado** na pipeline real

Essas são **semânticas diferentes**, não apenas escalas diferentes.
`classify_observed_regime()` espera [0,1] razões diretas.

### Solução: ObservationSnapshot

Nova camada bridge entre `ArchitecturalGraph` (real) e `classify_observed_regime()` (sintético).

### ObservationSnapshot (dataclass)

```python
@dataclass
class ObservationSnapshot:
    cross_domain_ratio: float      # [0,1]
    intra_domain_ratio: float      # [0,1]
    file_level_leakage: float      # [0,1]
    cycle_density: float           # [0,1]

    observation_quality: float     # [0,1] — 1 - unknown_edges_ratio
    classification_confidence: float  # [0,1] — observation_quality

    total_nodes: int
    total_edges: int
    cross_domain_edges: int
    intra_domain_edges: int
    unknown_edges: int
```

### Algoritmos Bridge

**cross_domain_ratio** = `cross_domain_edges / total_edges`

**intra_domain_ratio** = `intra_domain_edges / total_edges`
- Computado DIRETAMENTE (não como `1 - cross_domain_ratio`)
- Projetos reais podem ter `unknown_edges`

**unknown_edges_ratio** = `1 - (cross_domain_edges + intra_domain_edges) / total_edges`

**file_level_leakage** = `boundary_violations / total_edges`

**cycle_density** = `edges_in_cycles / total_edges`
- Usa `nx.simple_cycles()` para detectar edges participantes de ciclos
- Preserva o domínio conceitual arquitetural

**observation_quality** = `1 - unknown_edges / max(total_edges, 1)`

### Arquivos Novos

| Arquivo | Conteúdo |
|---------|----------|
| `ags/core/observation/__init__.py` | Package init, exporta ObservationSnapshot e compute_observation_snapshot |
| `ags/core/observation/primitives.py` | compute_observation_snapshot() — bridge entre ArchitecturalGraph e sintético |
| `tests/test_observation.py` | Testes com sample_graph + Requests |

### Baseline Impact

`ags/core/observation/` **não está** no baseline. **Nenhum bump**.

---

## Hipóteses

### H1 — Regime Transferability

**Condição formal:** `P(R_obs ∈ Ω_synth) ≥ 0.70`
**Falsificação (F3):** `< 50%` classificáveis em Ω_synth

### H2 — Discriminative Power

**Condição formal:** Ao menos 2 regimes distintos entre os 5 projetos
**Falsificação:** Todos no mesmo regime (ex: todos MIXED)

### H3 — Emergent Structure

**Procedimento:** PCA + UMAP + HDBSCAN sobre vetores observados
**Falsificação:** Nenhuma estrutura de cluster significativa
**Descoberta:** Clusters estáveis fora de Ω_synth = novo fenômeno candidato

---

## Dataset

| Projeto | Versão | LOC | Observação |
|---------|--------|-----|------------|
| Django | 5.x | 150k+ | Framework web mais usado |
| FastAPI | 0.115.x | 30k | Framework moderno, design limpo |
| Celery | 5.4.x | 50k | Sistema distribuído |
| Airflow | 2.10.x | 200k+ | Grande, regimes complexos |
| Requests | 2.32.x | 15k | Pequeno e estável (controle) |

**N = 5** snapshots (apenas HEAD, sem histórico).

---

## Critérios de Sucesso

| Resultado | Significado | Ação |
|-----------|-------------|------|
| **PASS** | ≥70% coverage + >1 regime | Prosseguir para C1 longitudinal |
| **PARTIAL** | Coverage aceitável, recalibração | MINOR v2.1.0 |
| **FAIL** | <50% OU single-regime OU clusters inexplicados | MAJOR v3.0.0 |

---

## Scientific Change Protocol

1. **O que está sendo observado?** Regimes arquiteturais em projetos reais
2. **Que fenômeno isso representa?** Transferência de Ω_synth para Ω_real
3. **Que hipótese está sendo adicionada?** H1: regimes sintéticos são observáveis em reais
4. **Como ela pode ser falsificada?** F3: <50% coverage real
5. **Que métrica irá observá-la?** observation_quality, coverage_rate
6. **Que documento FASM será alterado?** C1_RESULTS.md (novo)
7. **Isso exige?** Bridge layer (sem bump) ou MAJOR se F3 disparar
8. **O baseline será invalidado?** Apenas se MAJOR (v3.0.0)
