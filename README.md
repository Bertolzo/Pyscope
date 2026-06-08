<p align="center">
  <img src="assets/header.svg" alt="PyScope — Architectural Observatory" width="100%">
</p>

<p align="center">
  <a href="https://github.com/Bertolzo/Pyscope/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12+-blue.svg?logo=python&logoColor=white" alt="Python 3.12+"></a>
  <a href="#testes"><img src="https://img.shields.io/badge/tests-277_passed-brightgreen.svg" alt="277 tests"></a>
  <a href="#escopo"><img src="https://img.shields.io/badge/FASM-v2.0-lightgrey.svg" alt="FASM v2.0"></a>
  <a href="https://github.com/Bertolzo/Pyscope/actions"><img src="https://img.shields.io/badge/CI-passing-brightgreen.svg" alt="CI"></a>
</p>

<p align="center">
  <b>static observation · AST-based · reproducible · 11 architectural regimes</b>
</p>

---

## Índice

- [Filosofia](#filosofia)
- [Arquitetura](#arquitetura)
- [Módulos](#módulos)
- [Escopo](#escopo)
- [Quick Start](#quick-start)
- [Uso](#uso)
- [Design Decisions](#design-decisions)
- [Testes](#testes)
- [Estrutura do Repositório](#estrutura-do-repositório)

---

## Filosofia

> **PyScope não adivinha. PyScope observa.**

PyScope é uma ferramenta de **observação arquitetural**, não de governança. Ela existe porque a maioria das ferramentas de arquitetura ainda **mistura métricas com inferências** — entregando opiniões onde deveriam entregar dados.

O projeto se apoia em **três artefatos formais** que não podem ser confundidos:

| Artefato | Papel | O que define |
|----------|-------|-------------|
| **FASM** | Modelo formal | Ontologia, teoria, axiomas, métricas, invariantes — *o que* observar |
| **AGS** | Implementação | GraphBuilder, parsers, engine de métricas, banco — *como* observar |
| **PyScope** | Observatório | ObservationSnapshot, RegimeClassification, protocolos C0/C1/C2 — observação → FASM → evidência |

> FASM não contém código Python. AGS não cria conceitos — apenas implementa. PyScope não cria teoria — apenas observa.

---

## Arquitetura

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            ENTRY POINTS                                     │
│                                                                            │
│   tools/c1_observe.py      python -m ags           pyscope.visualizer      │
│   (observação remota)      (CLI orquestrada)       (dashboard HTML)        │
└──────────┬────────────────────┬───────────────────────┬──────────────────────┘
           │                    │                       │
           ▼                    ▼                       │
   ┌─────────────────────────────────────────┐         │
   │         AGS ORCHESTRATOR                │         │
   │      ags/orchestrator.py :: AGS         │         │
   │                                         │         │
   │   ┌────────┐  ┌──────────┐  ┌────────┐  │         │
   │   │ GRAPH  │─▶│STRUCTURAL│─▶│COUPLING│  │         │
   │   └────────┘  └──────────┘  └────────┘  │         │
   │        │           │            │       │         │
   │        ▼           ▼            ▼       │         │
   │   ┌─────────┐  ┌──────────┐  ┌────────┐  │         │
   │   │EVOLUTION│─▶│PREDICTION│─▶│GOVERN. │  │         │
   │   └─────────┘  └──────────┘  └────────┘  │         │
   └────────┼─────────────┼──────────────┼────┘         │
            │             │              │              │
            ▼             ▼              ▼              ▼
   ┌──────────────────────────┐  ┌────────────────────────────┐
   │   MODELS + OBSERVATION   │  │       VISUALIZADOR         │
   │                          │  │                            │
   │  ArchitecturalTwin       │  │  C1Result JSON             │
   │  ObservationSnapshot     │  │  → DOT (paleta própria)    │
   │  RegimeClassification    │  │  → SVG                     │
   │                          │  │  → HTML dashboard          │
   └────────────┬─────────────┘  └────────────────────────────┘
                │
                ▼
   ┌──────────────────────────┐  ┌────────────────────────────┐
   │     STORAGE (SQLite)     │  │     SYNTHETIC (C0.0)       │
   │   Database (WAL mode)    │  │  11 regimes canônicos      │
   │   4 repositórios         │  │  CIR-1/2/3/4 invariantes   │
   └──────────────────────────┘  └────────────────────────────┘
```

### Fluxo de dados

```
[AST Python] ──▶ GraphBuilder ──▶ ArchitecturalGraph (NetworkX)
                  │
                  ├──▶ cycle_density, dependency_density, drift
                  ├──▶ detect_communities, contamination
                  │
                  ▼
            ObservationSnapshot
                  │
                  ├──▶ metrics [0,1]: ACP, DCI, leakage, cycle density
                  ├──▶ classify_from_snapshot() → RegimeClassification
                  │      └── contra REGIME_TAXONOMY (11 atratores)
                  │
                  ▼
            Relatório JSON + Dashboard HTML
```

---

## Módulos

### AGS — Architectural Governance System

<details>
<summary><strong>ags/core/graph/ — Grafo Arquitetural</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `ArchitecturalGraph` | Grafo direcionado (NetworkX) com `FileNode`, `ModuleNode`, `ImportEdge` |
| `GraphBuilder` | Parseia AST de projetos Python; resolve imports, submódulos, aliases |
| `cycle_density()` | Fração de arestas em ciclos |
| `dependency_density()` | Densidade do grafo de dependências |
| `graph_drift()` | Distância estrutural entre duas versões do grafo |
| `detect_communities()` | Detecção Louvain + contaminação entre fronteiras |

</details>

<details>
<summary><strong>ags/core/observation/ — Observação C1</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `ObservationSnapshot` | Métricas primitivas [0,1] no mesmo formato do sintético |
| `compute_observation_snapshot()` | Bridge entre mundo real e taxonomia de regimes |
| `RegimeClassification` | Classificação por distância euclidiana aos 11 regimes canônicos |
| `classify_from_snapshot()` | Retorna regime, nearest, second_nearest, margin, confidence |

</details>

<details>
<summary><strong>ags/core/models/ — Modelos de Estado</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `ArchitecturalStateVector` | Vetor canônico L3 com entropia, acoplamento, CRI, AGP (10 dimensões) |
| `ArchitecturalTwin` | Gêmeo digital: estado + evolução + predição + governança |

</details>

<details>
<summary><strong>ags/synthetic/ — Validação C0.0</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `RegimeTaxonomy` | 11 regimes canônicos (PERFECT, COUPLED, LEAKY, COLLAPSED, MODULAR_*, ENTANGLED_*, MIXED, PATHOLOGICAL, ACYCLIC_DOMINANT) |
| `RegimeAwareGraphGenerator` | Amostrador causal que constrói grafos a partir de `FixtureSpec` |
| `SyntheticGraphSet` | Coleção cobrindo todo o espaço de regimes |
| **CIR-1** | Consistência causal: regime é identificável a partir da estrutura |
| **CIR-2** | Estabilidade sob perturbação + separação entre regimes |
| **CIR-3** | Cobertura do espaço de grafos (topologia, densidade, grau) |
| **CIR-4** | Ortogonalidade das métricas primitivas |

</details>

<details>
<summary><strong>ags/intelligence/ — Evolução e Predição</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `EvolutionAnalyzer` | Deltas entre snapshots, gradiente de entropia (velocidade/aceleração), half-life |
| `PredictionEngine` | Projeção de entropia/CRI em 30/60/90d, confiança, risco de colapso |

</details>

<details>
<summary><strong>ags/storage/ — Persistência</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `Database` | SQLite WAL mode com schema versioning (5 tabelas) |
| `SnapshotRepository` | Snapshots estruturais + grafo JSON |
| `CouplingRepository` | Relatórios de acoplamento (ACP, DCI) |
| `EvolutionRepository` | Gradiente de entropia, drift, half-life |
| `GovernanceRepository` | Eventos de governança (merge gates, violações) |

</details>

### PyScope Visualizer

Converte resultados de observação C1 em artefatos visuais.

| Componente | Responsabilidade |
|------------|-----------------|
| `schema.py` | Schemas `Node`, `Edge`, `C1Result` com `from_json()` |
| `graphviz_builder.py` | Constrói string DOT com cor por regime, espessura por ACP/DCI |
| `renderer.py` | Renderiza DOT → SVG/PNG via Graphviz |
| `html_report.py` | Dashboard HTML com cards, legend e hover sutis |
| `cli.py` | CLI: `python -m pyscope.visualizer --input-json ... --output-dir ...` |

**Paleta de cores aplicada ao grafo:**

| Regime | Cor | Uso |
|--------|-----|-----|
| `perfect` | `#22C55E` | green |
| `modular_*` | `#38BDF8` | sky blue |
| `layered` | `#60A5FA` | light blue |
| `entangled_*` | `#F59E0B` | amber |
| `coupled` | `#EF4444` | red |
| `leaky` | `#EC4899` | pink |
| `collapsed` | `#991B1B` | deep red |
| `mixed` | `#A78BFA` | violet |
| `acyclic_dominant` | `#67E8F9` | light cyan |

### Tools

| Script | Propósito |
|--------|-----------|
| `c1_observe.py` | Observação C1: clona repo, constrói grafo, classifica regime, exporta JSON |
| `c1_observe_requests.py` | Exemplo prático observando o repositório `psf/requests` |
| `verify_baseline.py` | Verifica integridade do baseline do projeto |
| `remote_runner.py` | Execução remota de observações |
| `resource_adapter.py` | Adaptador de recursos (local vs cloud) |
| `providers/` | Providers cloud (AWS, OCI, Oracle) |

---

## Escopo

### Em escopo

- Projetos Python com estrutura de pacotes padrão
- Análise **estática** do grafo de imports (AST)
- Métricas FASM: ACP, DCI, boundary leakage, cycle density, CRI
- Classificação em 11 regimes arquiteturais
- Observação remota de repositórios (C1)
- Resultados auditáveis em JSON
- Visualização Graphviz + dashboard HTML
- Geração sintética para validação de invariantes (C0.0)
- Pipeline GitHub Actions para CI/CD

### Fora de escopo (deliberadamente)

- Análise dinâmica de runtime (profiling, tracing)
- Linguagens que não sejam Python
- Previsões de futuro ou causalidade além da topologia estrutural
- Import condicional e `__import__()` com argumentos não literais
- Monorepos massivos sem estratégia de amostragem
- Análise de qualidade de código (linters, style checkers)

---

## Quick Start

```bash
# Clone
git clone https://github.com/Bertolzo/Pyscope.git
cd Pyscope

# Ambiente virtual
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# Instalação
python -m pip install -e ".[dev,intelligence]"

# Testes (277 testes — deve passar limpo)
python -m pytest -q --no-cov
```

---

## Uso

### Observação C1

Observe a arquitetura de qualquer repositório Python público:

```bash
python -m tools.c1_observe "requests" "https://github.com/psf/requests.git" c1_requests_remote
```

Saída esperada:

```
📦 Observando requests de https://github.com/psf/requests.git
├── ✅ Clone concluído
├── ✅ Grafo construído: 37 files, 81 edges
├── 📊 ObservationSnapshot
│   ├── cross_domain_ratio:   0.00
│   ├── intra_domain_ratio:   1.00
│   ├── leakage:              0.00
│   ├── cycle_density:        0.58
│   └── quality:              1.00
├── 🏷️  RegimeClassification
│   ├── regime:               MIXED
│   ├── nearest:              MIXED (dist: 2.65)
│   ├── margin:               0.15
│   └── confidence:           0.27
└── ✅ Artefato: c1_requests_result.json
```

### Visualizador

Converta um resultado C1 em grafo + dashboard HTML:

```bash
python -m pyscope.visualizer \
  --input-json tests/fixtures/c1_example.json \
  --output-dir out/visual
```

Gera:

```
out/
├── graph.dot        # Grafo em formato DOT
├── graph.svg        # Renderização SVG
├── graph.png        # Renderização PNG
└── index.html       # Dashboard HTML com SVG + métricas
```

O dashboard HTML tem:

- Header com título e metadados do repositório
- Cards coloridos por tipo de métrica
- SVG do grafo com nós coloridos por regime
- Legend interativa com swatches de cores
- Hover effects sutis
- Footer com hash do artefato gerado

### CLI AGS

```bash
# Analisar um projeto local
ags analyze /caminho/para/projeto

# Ver histórico de observações
ags history

# Projeção de métricas
ags forecast
```

---

## Design Decisions

| Decisão | Justificativa |
|---------|---------------|
| **Métricas [0,1] em vez de scores [0,100]** | Alinhamento com o modelo formal FASM; permite comparação direta com a taxonomia sintética |
| **cycle_density = edges_in_cycles / total_edges** | Mede acoplamento cíclico real (não complexidade ciclomática) |
| **intra_domain_ratio direto (não 1 - cross)** | Revela gaps de classificação quando ambos são baixos |
| **Self-loops ignorados** | Não representam dependência arquitetural entre entidades distintas |
| **confidence = quality / (1 + distance)** | Mapeia qualquer distância a (0, 1]; quality penaliza observações parciais |
| **Parser via AST (não regex)** | AST capta a semântica real do código; regex falha em imports condicionais e dinâmicos |
| **SQLite WAL mode** | Leitores não bloqueiam escritores; ideal para pipelines CI |
| **Twin digital separado do snapshot** | Snapshot é o estado atual; twin é o agregado estado + histórico + predição |

---

## Testes

O projeto possui **277 testes** organizados em:

| Suite | Testes | O que valida |
|-------|:------:|-------------|
| `test_graph*` | 65 | Grafo, builder, métricas, invariantes, serialização |
| `test_observation` | 22 | ObservationSnapshot, quality, cycles, domains |
| `test_classification` | 18 | RegimeClassification, invariantes, confidence |
| `test_math_invariants` | 26 | Limites formais de ACP, DCI, leakage, CRI, AGP |
| `test_synthetic_c00` | 60 | CIR-1, CIR-2, CIR-3, CIR-4, ortogonalidade |
| `test_baseline` | 24 | Baseline file, parsing, verificação, versionamento |
| `test_snapshot_consistency` | 5 | Roundtrip de snapshots, coupling, evolution, governance |
| `test_visualizer` | 3 | Schema, DOT builder, renderer |
| Demais | 54 | MCP, provisionamento, remote runner, resource adapter |

```bash
# Rodar todos os testes
python -m pytest -q --no-cov

# Com cobertura
python -m pytest --cov=ags --cov=pyscope --cov-report=term-missing

# Testes específicos
python -m pytest tests/test_graph.py tests/test_observation.py -v
```

---

## GitHub Actions

| Workflow | Trigger | O que faz |
|----------|---------|-----------|
| `c1_observe.yml` | `workflow_dispatch` | Executa observação C1 remota e publica artefato JSON |
| `visualizer-ci.yml` | Push em `scope/**` | Roda visualizador, valida saída DOT/SVG/HTML |

---

## Branching

| Branch | Propósito |
|--------|-----------|
| `main` | Linha estável para early adopters |
| `develop` | Validação antes de promoção para main |
| `feature/*` | Novos recursos funcionais |
| `exp/*` | Experimentos e pesquisa |
| `doc/*` | Mudanças de escopo e contrato |
| `hotfix/*` | Correções urgentes |
| `scope/*` | Branches de escopo do visualizador |

---

## Contribuição

1. Abra um issue descrevendo o caso de uso
2. Escolha a branch adequada conforme a branching strategy
3. Preencha o template de PR
4. Execute as validações obrigatórias:

```bash
python -m pytest -q --no-cov
python tools/verify_baseline.py
```

5. Atualize a documentação sempre que houver alteração de métricas, escopo ou comportamento
6. Submeta o PR para revisão

---

## Estrutura do Repositório

```
ags/                              # Núcleo AGS
├── __init__.py
├── __main__.py                   # Entry point: python -m ags
├── orchestrator.py               # Pipeline de 6 camadas
├── cli/                          # CLI Typer (analyze, history, forecast)
├── core/                         # graph, observation, models, structural, coupling, governance
├── intelligence/                 # Evolução e predição
├── storage/                      # SQLite WAL + 4 repositórios
└── synthetic/                    # Geração sintética (11 regimes, CIR-1/2/3/4)

pyscope/                          # Visualizador
└── visualizer/
    ├── cli.py                    # CLI entry point
    ├── graphviz_builder.py       # DOT builder
    ├── html_report.py            # Dashboard HTML
    ├── renderer.py               # DOT → SVG/PNG
    └── schema.py                 # C1Result, Node, Edge

assets/                           # Recursos visuais
└── header.svg                    # Banner SVG do README

tools/                            # Scripts operacionais
├── c1_observe.py                 # Observação C1 remota
├── c1_observe_requests.py        # Exemplo com requests
├── verify_baseline.py
├── remote_runner.py
├── resource_adapter.py
└── providers/                    # AWS, OCI, Oracle

docs/                             # Modelo científico e limitações
tests/                            # 277 testes
.github/                          # Workflows + templates
```

---

<p align="center">
  <img src="https://img.shields.io/badge/PyScope-v2.0.0-blue.svg" alt="v2.0.0">
  <img src="https://img.shields.io/badge/observation-not_inference-lightgrey.svg" alt="observation">
  <img src="https://img.shields.io/badge/data-not_opinion-success.svg" alt="data">
</p>

<p align="center">
  <strong>PyScope</strong> — transformando arquitetura Python em<br>
  <em>decisões técnicas fundadas, auditáveis e reproduzíveis.</em><br><br>
  <sub>Observação, não adivinhação. Dados, não opiniões.</sub>
</p>
