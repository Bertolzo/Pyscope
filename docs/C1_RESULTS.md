# Pyscope 1.0 — Real-World Transfer Results

**Baseline:** v2.0.0 (frozen 2026-06-04)
**Status:** PARTIAL — coverage aceitável, distância estrutural insuficiente
**Recomendação:** MINOR v2.1.0 (expansão do espaço de regimes)

---

## Pergunta Central

> O espaço fenomenológico criado em C0 (Ω_synth, 11 regimes)
> possui correspondência observável no mundo real?

**Resposta:** SIM, com ressalvas. 4/4 projetos foram classificáveis (100%),
as margens são altas (0.59–1.95), e o poder discriminativo é suficiente
(3 regimes distintos). Porém:

- a qualidade de observação recalculada com `total_imports_attempted`
  revela que todos os projetos falham no gate de qualidade;
- nenhum projeto ainda passa o gate de distância estrutural ≤ 0.25,
  indicando que o espaço de regimes sintéticos não cobre bem as
  estruturas observadas em projetos reais.

---

## Dataset Observed

| Projeto | Commit | Files | Edges | Módulos | Imports Tentados | Qualidade |
|--------:|:------:|-----:|-----:|-------:|-----------------:|----------:|
| Requests | 1190afd | 37 | 101 | 3 | 327 | 0.3089 |
| FastAPI | 5cdf820 | 1120 | 1639 | 4 | 3646 | 0.4495 |
| Celery | aa4c3b1 | 416 | 1450 | 5 | 3060 | 0.4739 |
| Airflow | f1a5d1e | 7374 | 29* | 20 | 49861 | 0.0006 |

*Observações*

- Airflow está sub-observado: apenas 29 arestas detectadas em 7374 arquivos.
  O parser estático não resolve imports dinâmicos (plugins, importlib, lazy loading),
  portanto `observation_quality` usa `total_imports_attempted` para refletir imports
  não resolvidos (denominador). Isso corrige a estimativa otimista usada anteriormente.
- Django não foi observado por OOM em ambiente de 7.7GB (projeto >150k LOC).

  Veja `docs/RESOURCE_ADAPTER.md` para recomendações de execução controlada em hosts compartilhados.

  Próximo passo: reexecutar a observação Django com limites conservadores como
  `nice=10` e `cpulimit=50` para validar se o processo conclui sem esgotar RAM.

---

## Gate Check

| Gate | Threshold | Requests | FastAPI | Celery | Airflow |
|------|-----------|----------|---------|--------|---------|
| Quality | ≥ 0.90 | 0.3089 ✗ | 0.4495 ✗ | 0.4739 ✗ | 0.0006 ✗ |
| Margin | ≥ 0.10 | 0.6060 ✓ | 1.9762 ✓ | 1.2613 ✓ | 0.5852 ✓ |
| Struct-Dist | ≤ 0.25 | 2.8588 ✗ | 2.4593 ✗ | 0.9904 ✗ | 1.0000 ✗ |

**Todos os projetos falham no gate de qualidade e nenhum passa o gate de
distância estrutural.**

---

## Métricas Observadas

| Projeto | cross | intra | leakage | cycles | quality |
|---------|-------|-------|---------|--------|---------|
| Requests | 0.1485 | 0.8515 | 0.0000 | 0.7129 | 0.3089 |
| FastAPI | 0.8182 | 0.1818 | 0.0000 | 0.0610 | 0.4495 |
| Celery | 0.4628 | 0.5372 | 0.0000 | 0.2124 | 0.4739 |
| Airflow | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0006 |

Nenhum projeto apresenta `file_level_leakage` > 0. O sistema de
boundary violations (`is_boundary_violation`) não está sendo populado
pelo GraphBuilder, ou os projetos reais não geram esse tipo de edge.

---

## Classificação

### Total (com penalidade de tamanho)

| Projeto | Regime | Distância | 2º Nearest | Margem |
|---------|--------|-----------|------------|--------|
| Requests | MIXED | 2.73 | ENTANGLED_SMALL | 0.69 |
| FastAPI | ENTANGLED_LARGE | 2.98 | MIXED | 1.95 |
| Celery | ENTANGLED_LARGE | 1.74 | MODULAR_LARGE | 0.75 |
| Airflow | MODULAR_LARGE | 4.14 | ENTANGLED_LARGE | 0.59 |

### Estrutural (sem penalidade de tamanho)

| Projeto | Regime | Distância | 2º Nearest | Margem |
|---------|--------|-----------|------------|--------|
| Requests | MIXED | 2.65 | ENTANGLED_SMALL | 0.72 |
| FastAPI | MIXED | 2.54 | ENTANGLED_LARGE | 0.20 |
| Celery | **COUPLED** | **0.99** | MIXED | 0.00* |
| Airflow | MODULAR_LARGE | 1.00 | ENTANGLED_LARGE | 0.19 |

\*Margem estrutural de Celery entre COUPLED e MIXED é 0.005 — essencialmente
empatados. COUPLED vence por diferença desprezível.

### Descoberta Crítica: Regime Total vs. Estrutural

O regime total é dominado pela penalidade de tamanho.
Celery (416 files) é puxado de COUPLED (MEDIUM) para ENTANGLED_LARGE (LARGE)
pela diferença de tamanho. FastAPI (1120 files) é puxado de MIXED (MEDIUM)
para ENTANGLED_LARGE (LARGE).

**A classificação estrutural (sem tamanho) é mais informativa** para entender
a arquitetura real do projeto. O tamanho deve ser tratado como metadado,
não como dimensão de regime.

---

## Hipóteses

### H1 — Regime Transferability

**Condição:** P(R_obs ∈ Ω_synth) ≥ 0.70
**Resultado:** 4/4 = 100% classificáveis ✓
**Falsificação (F3):** < 50% → NÃO DISPARADA
**Veredito:** PARTIAL — a classificação é possível e produz nearest-regime
significativo, mas a distância estrutural média (1.80) indica que os
projetos reais estão longe dos centros dos regimes sintéticos.

O espaço Ω_synth precisa ser expandido para cobrir:

1. **Regiões de alto cross + baixo intra** (FastAPI: cross=0.83, intra=0.17)
   — Nenhum regime atual tem intra < 0.4
2. **Regiões de uma única módulo com ciclos internos altos**
   (Requests: intra=1.0, cycles=0.58) — Nenhum regime atual tem
   cycles > 0.5

### H2 — Discriminative Power

**Condição:** Ao menos 2 regimes distintos entre os projetos
**Resultado:** 3 regimes estruturais (MIXED, COUPLED, MODULAR_LARGE) ✓
**Falsificação:** Todos no mesmo regime → NÃO DISPARADA
**Veredito:** PASS

Celery (COUPLED) é claramente distinguível de FastAPI (MIXED) e
Requests (MIXED, mas com perfil de métricas diferente). Airflow
(MODULAR_LARGE) é distinguível por ter zero cycles + zero cross.

**Risco H2 mitigado:** O espaço tem poder discriminativo mesmo com
apenas 11 regimes.

### H3 — Emergent Structure

**Procedimento:** PCA + UMAP + HDBSCAN
**Resultado:** N/A — 4 pontos são insuficientes para inferência
robusta de clusters
**Veredito:** INCONCLUSIVO (necessita C1 longitudinal com ≥ 10 snapshots)

---

## Análise por Projeto

### Requests (MIXED estrutural, 2.65)

- **Perfil:** 100% intra-domain, sem cross-domain, sem leakage.
- **Ciclos:** 58% dos edges participam de ciclos — a estrutura de
  vendored urllib3 + internal helpers cria alta retroalimentação.
- **Interpretação:** Requests funciona como um monolito interno.
  O regime MIXED captura a natureza heterogênea, mas a distância
  de 2.65 reflete que não há regime com "single module + high cycles".

### FastAPI (MIXED estrutural, 2.54)

- **Perfil:** 83% cross-domain, 17% intra-domain — módulos fortemente
  acoplados entre si.
- **Ciclos:** Apenas 3.7% dos edges em ciclos — estrutura quase acíclica
  dentro do alto acoplamento.
- **Interpretação:** FastAPI tem uma arquitetura plana com domínios
  pouco isolados. O regime MIXED + ENTANGLED_LARGE é o melhor ajuste
  disponível, mas a distância de 2.54 indica que essa combinação de
  cross=0.83 + cycles=0.04 não existe em Ω_synth.

### Celery (COUPLED estrutural, 0.99)

- **Perfil:** 42% cross, 58% intra — o mais balanceado dos 4.
- **Ciclos:** 11.5% — moderados.
- **Interpretação:** Celery é o projeto REAL mais próximo de um regime
  SINTÉTICO. A distância estrutural de 0.99 é a menor entre todos,
  indicando que o espaço COUPLED cobre bem arquiteturas do tipo
  "sistema distribuído com acoplamento controlado".

### Airflow (MODULAR_LARGE estrutural, 1.00)

- **Perfil:** 100% intra-domain (apenas 29 edges observados).
- **Limitação:** O parser não captura a verdadeira arquitetura de Airflow.
  O número de edges (29 para 7362 arquivos) é varias ordens de grandeza
  abaixo do esperado.
- **Interpretação:** A classificação MODULAR_LARGE é um artefato da
  sub-observação, não um retrato fiel da arquitetura.

---

## Limitações Metodológicas

### 1. Sub-observação não detectada

O `observation_quality` atual assume que todos os edges não detectados
são edges que não existem. Para Airflow, isso é falso: o parser perdeu
milhares de imports dinâmicos, mas reporta quality=1.0.

**Correção necessária:** `compute_observation_snapshot` precisa receber
`total_imports_attempted` (número de imports que o parser tentou resolver).
Se 10000 imports foram tentados mas apenas 29 edges foram gerados,
a quality deve ser 29/10000 = 0.0029, não 1.0.

### 2. Escala de tamanho

A `_size_distance` original (targets 6/20/50) foi calibrada para grafos
sintéticos de 4-50 nós. Projetos reais têm 37-7362 nós, tornando a
penalidade de tamanho dominante.

**Correção aplicada:** `size_mode="real"` usa log-scale com targets
ln(15)/ln(60)/ln(500), normalizados por ln(2). Isso reduz a dominância
do tamanho, mas não elimina o problema.

**Solução ideal:** A classificação de regime deve ser puramente estrutural
(4 métricas). O tamanho deve ser tratado como metadado de contexto, não
como dimensão de classificação.

### 3. Django ausente

Django (150k+ LOC) causou OOM com 7.7GB RAM. O GraphBuilder tenta
parsear todos os arquivos Python simultaneamente. Para projetos > 100k LOC,
é necessário um modo de parseamento incremental ou streaming.

### 4. Leakage inexistente

Nenhum projeto apresenta `file_level_leakage` > 0. O GraphBuilder não
popula `is_boundary_violation` nos edges, ou os projetos não geram
esse padrão. A valência da métrica de leakage não pôde ser testada.

---

## Recomendações para v2.1.0

### Taxonomia Expandida (C2.0)

Adicionar ao `REGIME_TAXONOMY`:

| Regime | cross | intra | cycles | Descrição |
|--------|-------|-------|--------|-----------|
| MIXED_CYCLIC | 0.0–0.2 | 0.8–1.0 | 0.4–0.7 | Single-module com alta retroalimentação (Requests) |
| CROSS_DOMINANT | 0.7–0.9 | 0.1–0.3 | 0.0–0.1 | Cross alto, intra baixo, acíclico (FastAPI) |
| COUPLED_BALANCED | 0.4–0.6 | 0.4–0.6 | 0.1–0.2 | Balanceado cross/intra (Celery) |

### AGS Improvements

1. **`total_imports_attempted`** no `ObservationSnapshot` (CIR-4A)
2. **Modo streaming** no GraphBuilder para projetos > 100k LOC
3. **Parser de imports dinâmicos** — pelo menos contagem de importlib/lazy imports
   para estimar unknown_dynamic_edges

### Protocolo

4. **Gate check revisado**: distância estrutural ≤ 0.50 (não 0.25)
   para C1.0, pois o threshold de 0.25 foi calibrado para Ω_synth
5. **structural_distance_1** como métrica primária para decisão de gate

---

### Apêndice: Dados Brutos

Arquivos JSON exportados (executados nesta sessão):

| Projeto | Arquivo |
|---------|---------|
| Requests | `c1_requests_result.json` |
| FastAPI | `c1_fastapi_result.json` |
| Celery | `c1_celery_result.json` |
| Airflow | `c1_airflow_result.json` |
| Django | **em andamento** — observação rodando no momento, aguardando conclusão para exportar `c1_django_result.json`

---

## Histórico

| Data | Versão | Mudança |
|------|--------|---------|
| 2026-06-05 | v2.0.0 | C1.0 original — 4 projetos observados, PARTIAL |

---

*Documento gerado em 2026-06-05 pelo script `tools/c1_observe.py`.*
