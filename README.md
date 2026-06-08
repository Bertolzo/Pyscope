<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-blue?style=flat&logo=python" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat" alt="MIT License">
  <img src="https://img.shields.io/badge/tests-277%20passed-brightgreen?style=flat" alt="277 tests passing">
  <img src="https://img.shields.io/badge/version-2.0.0-orange?style=flat" alt="v2.0.0">
</p>

<h1 align="center">🔭 PyScope</h1>
<p align="center"><strong>Observatório Arquitetural para Python</strong><br>
Observação estática de grafos de imports · Métricas FASM · Artefatos auditáveis · Visualização</p>

---

## Índice

- [Filosofia](#filosofia)
- [Arquitetura](#arquitetura)
- [Módulos](#módulos)
  - [AGS — Architectural Governance System](#ags--architectural-governance-system)
  - [PyScope Visualizer](#pyscope-visualizer)
  - [Tools](#tools)
- [Escopo](#escopo)
- [Quick Start](#quick-start)
- [Uso](#uso)
  - [Observação C1](#observação-c1)
  - [Visualizador](#visualizador)
  - [CLI AGS](#cli-ags)
- [Ciclo de vida de uma observação](#ciclo-de-vida-de-uma-observação)
- [Design Decisions](#design-decisions)
- [Testes](#testes)
- [GitHub Actions](#github-actions)
- [Branching](#branching)
- [Contribuição](#contribuição)
- [Estrutura do Repositório](#estrutura-do-repositório)

---

## Filosofia

PyScope é uma ferramenta de **observação**, não de governança. Ela existe porque a maioria das ferramentas de arquitetura de software ainda **mistura métricas com inferências** — entregando opiniões onde deveriam entregar dados.

**PyScope não adivinha. PyScope observa.**

O projeto se apoia em três artefatos formais que **não podem ser confundidos**:

| Artefato | Papel | O que define |
|----------|-------|-------------|
| **FASM** | Modelo formal | Ontologia, teoria, axiomas, métricas, invariantes — *o que* observar |
| **AGS** | Implementação | GraphBuilder, parsers, engine de métricas, banco — *como* observar |
| **PyScope** | Observatório | ObservationSnapshot, RegimeClassification, protocolos C0/C1/C2 — conecta observação → FASM → evidência |

> FASM não contém código Python. AGS não cria conceitos — apenas implementa. PyScope não cria teoria — apenas observa.

---

## Arquitetura

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           ENTRY POINTS                                       │
│                                                                            │
│   tools/c1_observe.py     python -m ags          pyscope.visualizer        │
│   (observação remota)     (CLI orquestrada)      (visualização C1)         │
└──────────┬──────────────────────┬──────────────────────┬────────────────────┘
           │                      │                      │
           ▼                      ▼                      │
┌──────────────────────────────────────────────┐         │
│            AGS ORCHESTRATOR                   │         │
│         ags/orchestrator.py :: AGS            │         │
│                                              │         │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐   │         │
│  │GRAPH    │→ │STRUCTURAL│→ │ COUPLING   │   │         │
│  │Builder  │  │Analyzer  │  │ Analyzer   │   │         │
│  │Metrics  │  │Snapshot  │  │ Report     │   │         │
│  │Comm.    │  │          │  │            │   │         │
│  └────┬────┘  └────┬─────┘  └──────┬─────┘   │         │
│       │            │               │         │         │
│       ▼            ▼               ▼         │         │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐   │         │
│  │EVOLUTION│→ │PREDICTION│→ │GOVERNANCE  │   │         │
│  │Analyzer │  │Engine    │  │Engine      │   │         │
│  │Drift    │  │Forecast  │  │Guardian    │   │         │
│  └────┬────┘  └────┬─────┘  └──────┬─────┘   │         │
│       │            │               │         │         │
└───────┼────────────┼───────────────┼─────────┘         │
        │            │               │                   │
        ▼            ▼               ▼                   ▼
┌──────────────────────────────────────────┐  ┌─────────────────────┐
│         MODELS + OBSERVATION             │  │   VISUALIZADOR      │
│                                          │  │                     │
│  ArchitecturalStateVector (10-d embed)   │  │  C1Result JSON      │
│  ArchitecturalTwin (gêmeo digital)       │  │  → Graphviz DOT     │
│  ObservationSnapshot → RegimeClassif.    │  │  → SVG/PNG          │
│                                          │  │  → HTML report      │
└────────────────┬─────────────────────────┘  └─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐  ┌─────────────────────┐
│         STORAGE (SQLite)                 │  │   SYNTHETIC (C0.0)  │
│                                          │  │                     │
│  Database (WAL mode)                     │  │  FixtureSpec        │
│  ├─ SnapshotRepository                   │  │  → RegimeAwareGen   │
│  ├─ CouplingRepository                   │  │  → 11 regimes       │
│  ├─ EvolutionRepository                  │  │  → CIR-1/2/3/4      │
│  └─ GovernanceRepository                 │  │                     │
└──────────────────────────────────────────┘  └─────────────────────┘
```

### Fluxo de dados principal

```
[AST Python] ──► GraphBuilder ──► ArchitecturalGraph (NetworkX)
                  │
                  ├──► cycle_density, dependency_density, drift
                  ├──► detect_communities, contamination
                  │
                  ▼
            ObservationSnapshot
                  │
                  ├──► metrics [0,1]: ACP, DCI, leakage, cycle density
                  ├──► classify_from_snapshot() → RegimeClassification
                  │      └── contra REGIME_TAXONOMY (11 atratores)
                  │
                  ▼
            Relatório JSON + Visualizador HTML
```

---

## Módulos

### AGS — Architectural Governance System

O núcleo do PyScope. Organizado em 6 camadas que formam um pipeline de observação arquitetural.

#### `ags/core/graph/` — Grafo Arquitetural

| Componente | Responsabilidade |
|------------|-----------------|
| `ArchitecturalGraph` | Grafo direcionado (NetworkX) com `FileNode`, `ModuleNode`, `ImportEdge` |
| `GraphBuilder` | Parseia AST de projetos Python; resolve imports, submódulos, aliases |
| `cycle_density()` | Fração de arestas em ciclos |
| `dependency_density()` | Densidade do grafo de dependências |
| `graph_drift()` | Distância estrutural entre duas versões do grafo |
| `detect_communities()` | Detecção Louvain + contaminação entre fronteiras |

#### `ags/core/observation/` — Observação C1

| Componente | Responsabilidade |
|------------|-----------------|
| `ObservationSnapshot` | Métricas primitivas [0,1] no mesmo formato do sintético |
| `compute_observation_snapshot()` | Bridge entre mundo real e taxonomia de regimes |
| `RegimeClassification` | Classificação por distância euclidiana aos 11 regimes canônicos |
| `classify_from_snapshot()` | Retorna regime, nearest, second_nearest, margin, confidence |

#### `ags/core/models/` — Modelos de Estado

| Componente | Responsabilidade |
|------------|-----------------|
| `ArchitecturalStateVector` | Vetor canônico L3 com entropia, acoplamento, CRI, AGP (10 dimensões) |
| `ArchitecturalTwin` | Gêmeo digital: estado + evolução + predição + governança |

#### `ags/synthetic/` — Validação C0.0

| Componente | Responsabilidade |
|------------|-----------------|
| `RegimeTaxonomy` | 11 regimes canônicos (PERFECT, COUPLED, LEAKY, COLLAPSED, MODULAR_*, ENTANGLED_*, MIXED, PATHOLOGICAL, ACYCLIC_DOMINANT) |
| `RegimeAwareGraphGenerator` | Amostrador causal que constrói grafos a partir de `FixtureSpec` |
| `SyntheticGraphSet` | Coleção cobrindo todo o espaço de regimes |
| **CIR-1** | Consistência causal: regime é identificável a partir da estrutura |
| **CIR-2** | Estabilidade sob perturbação + separação entre regimes |
| **CIR-3** | Cobertura do espaço de grafos (topologia, densidade, grau) |
| **CIR-4** | Ortogonalidade das métricas primitivas |

#### `ags/intelligence/` — Evolução e Predição

| Componente | Responsabilidade |
|------------|-----------------|
| `EvolutionAnalyzer` | Deltas entre snapshots, gradiente de entropia (velocidade/aceleração), half-life |
| `PredictionEngine` | Projeção de entropia/CRI em 30/60/90d, confiança, risco de colapso |

#### `ags/storage/` — Persistência

| Componente | Responsabilidade |
|------------|-----------------|
| `Database` | SQLite WAL mode com schema versioning (5 tabelas) |
| `SnapshotRepository` | Snapshots estruturais + grafo JSON |
| `CouplingRepository` | Relatórios de acoplamento (ACP, DCI) |
| `EvolutionRepository` | Gradiente de entropia, drift, half-life |
| `GovernanceRepository` | Eventos de governança (merge gates, violações) |

---

### PyScope Visualizer

Converte resultados de observação C1 em artefatos visuais.

| Componente | Responsabilidade |
|------------|-----------------|
| `schema.py` | Schemas `Node`, `Edge`, `C1Result` com `from_json()` |
| `graphviz_builder.py` | Constrói string DOT com cor por regime, espessura por ACP/DCI |
| `renderer.py` | Renderiza DOT → SVG/PNG via Graphviz |
| `html_report.py` | Gera página HTML com SVG embutido + tabela de métricas |
| `cli.py` | CLI: `python -m pyscope.visualizer --input-json ... --output-dir ...` |

---

### Tools

Scripts operacionais para observação remota e utilitários.

| Script | Propósito |
|--------|-----------|
| `c1_observe.py` | Observação C1: clona repo, constrói grafo, classifica regime, exporta JSON |
| `c1_observe_requests.py` | Exemplo prático observando o repositório `psf/requests` |
| `verify_baseline.py` | Verifica integridade do baseline do projeto |
| `remote_runner.py` | Execução remota de observações |
| `resource_adapter.py` | Adaptador de recursos (local vs cloud) |
| `freetier_adapter.py` | Gerencia cache de promoções free tier |
| `mcp_register.py` | Registro de MCP providers |
| `providers/` | Providers cloud (AWS, OCI, Oracle) |

---

## Escopo

### ✅ Em escopo

- Projetos Python com estrutura de pacotes padrão
- Análise **estática** do grafo de imports (AST)
- Métricas FASM: ACP, DCI, boundary leakage, cycle density, CRI
- Classificação em 11 regimes arquiteturais
- Observação remota de repositórios (C1)
- Resultados auditáveis em JSON
- Visualização Graphviz + relatório HTML
- Geração sintética para validação de invariantes (C0.0)
- Pipeline GitHub Actions para CI/CD

### ❌ Fora de escopo (deliberadamente)

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
python -m pip install -e .[dev,intelligence]

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

Converta um resultado C1 em grafos e HTML:

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
└── index.html       # Relatório HTML com SVG + métricas
```

### CLI AGS

O núcleo AGS também pode ser usado via CLI:

```bash
# Analisar um projeto local
ags analyze /caminho/para/projeto

# Ver histórico de observações
ags history

# Projeção de métricas
ags forecast
```

---

## Ciclo de vida de uma observação

```
1. CLONE
   tools/c1_observe.py clona o repositório alvo
         │
2. PARSE (AST)
   GraphBuilder varre todos os .py, extrai imports
   → Resolve aliases: import a, b → 2 edges
   → Resolve submódulos: from pkg.sub import X → pkg/sub.py
         │
3. GRAFO
   ArchitecturalGraph (NetworkX direcionado)
   → Nós: FileNode (caminho real) + ModuleNode (pacote)
   → Arestas: ImportEdge (src → dst, com tipo)
         │
4. MÉTRICAS PRIMITIVAS
   ObservationSnapshot
   → cross_domain_ratio, intra_domain_ratio
   → boundary leakage
   → cycle density
   → observation_quality
         │
5. CLASSIFICAÇÃO
   classify_from_snapshot() contra REGIME_TAXONOMY
   → Distância euclidiana aos 11 centros de regime
   → Nearest, second_nearest, margin, confidence
         │
6. REPORT
   → JSON com métricas + classificação
   → Visualizador: DOT → SVG → HTML
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
├── cli/
│   ├── __init__.py
│   └── main.py                   # CLI Typer (analyze, history, forecast)
├── core/
│   ├── __init__.py
│   ├── coupling/
│   │   ├── analyzer.py           # CouplingAnalyzer
│   │   └── snapshot.py
│   ├── governance/
│   │   ├── engine.py             # GovernanceEngine
│   │   └── guardian.py           # ArchitecturalGuardian
│   ├── graph/
│   │   ├── architectural_graph.py # ArchitecturalGraph (NetworkX)
│   │   ├── builders.py           # GraphBuilder (AST parser)
│   │   ├── communities.py        # Louvain detection
│   │   └── metrics.py            # cycle_density, drift, fan_in/out
│   ├── models/
│   │   ├── state_vector.py       # ArchitecturalStateVector (10-d)
│   │   └── twin.py               # ArchitecturalTwin
│   ├── observation/
│   │   ├── primitives.py         # ObservationSnapshot
│   │   └── classification.py     # RegimeClassification
│   └── structural/
│       ├── analyzer.py           # StructuralAnalyzer
│       └── snapshot.py           # StructuralSnapshot
├── intelligence/
│   ├── __init__.py
│   ├── evolution/
│   │   ├── analyzer.py           # EvolutionAnalyzer, drift
│   │   └── models.py             # EntropyDynamics
│   └── prediction/
│       ├── engine.py             # PredictionEngine (30/60/90d)
│       └── __init__.py
├── storage/
│   ├── database.py               # SQLite WAL
│   └── repositories/
│       ├── base.py               # BaseRepository (CRUD genérico)
│       ├── snapshot_repo.py
│       ├── coupling_repo.py
│       ├── evolution_repo.py
│       └── governance_repo.py
└── synthetic/
    ├── __init__.py
    ├── coverage_audit.py         # CIR-3
    ├── generator.py              # RegimeAwareGraphGenerator
    ├── graph_set.py              # SyntheticGraphSet
    ├── orthogonality.py          # CIR-4
    ├── perturbation.py           # CIR-2
    ├── regimes.py                # REGIME_TAXONOMY (11 regimes)
    └── spec.py                   # FixtureSpec

pyscope/                          # Visualizador
├── __init__.py
├── core/
│   └── __init__.py
└── visualizer/
    ├── __init__.py
    ├── cli.py                    # CLI entry point
    ├── graphviz_builder.py       # DOT builder
    ├── html_report.py            # HTML report generator
    ├── renderer.py               # DOT → SVG/PNG
    └── schema.py                 # C1Result, Node, Edge

tools/                            # Scripts operacionais
├── c1_observe.py                 # Observação C1 remota
├── c1_observe_requests.py        # Exemplo com requests
├── verify_baseline.py            # Verificação de baseline
├── remote_runner.py              # Runner remoto
├── resource_adapter.py           # Adaptador de recursos
├── freetier_adapter.py           # Cache free tier
├── mcp_register.py               # Registro MCP
├── providers/                    # AWS, OCI, Oracle
└── ...

docs/                             # Modelo científico e limitações
├── FASM.md                       # Modelo formal completo
├── ARCHITECTURE.md               # Arquitetura do sistema
├── LIMITATIONS.md                # Limitações conhecidas
├── METRICS.md                    # Definição das métricas
├── THEORY.md                     # Base teórica
├── MEASUREMENT_THEORY.md         # Teoria da medição
├── CALIBRATION.md                # Calibração empírica
├── STATE_VECTOR.md               # Vetor de estado
├── INVARIANTS.md                 # Invariantes formais
├── C0_RESULTS.md                 # Resultados C0.0
├── C1_RESULTS.md                 # Resultados C1.0
└── ... (+20 arquivos)

tests/                            # Testes
├── conftest.py
├── fixtures/
│   ├── c1_example.json
│   └── sample_monolith/          # Projeto fixture
├── test_baseline.py
├── test_classification.py
├── test_graph.py
├── test_graph_invariants.py
├── test_graph_validation.py
├── test_math_invariants.py
├── test_observation.py
├── test_synthetic_c00.py
├── test_snapshot_consistency.py
├── test_visualizer/
│   ├── test_builder.py
│   ├── test_renderer.py
│   └── test_schema.py
└── ...

.github/                          # GitHub config
├── workflows/
│   ├── c1_observe.yml
│   └── visualizer-ci.yml
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── PULL_REQUEST_TEMPLATE.md
└── ISSUE_TEMPLATE/
    ├── bug_report.md
    └── feature_request.md
```

---

<p align="center">
  <strong>PyScope</strong> — transformando arquitetura Python em<br>
  <em>decisões técnicas fundadas, auditáveis e reproduzíveis.</em><br><br>
  <sub>Observação, não adivinhação. Dados, não opiniões.</sub>
</p>
