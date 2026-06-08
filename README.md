<p align="center">
  <img src="assets/pyscope-banner.svg" alt="PyScope \u2014 Architectural Observatory" width="800">
</p>

<p align="center">
  <a href="https://github.com/Bertolzo/Pyscope/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square&logo=python&logoColor=white" alt="Python 3.12+"></a>
  <a href="#testes"><img src="https://img.shields.io/badge/tests-277%20passed-success.svg?style=flat-square" alt="277 tests"></a>
  <a href="#escopo"><img src="https://img.shields.io/badge/FASM-v2.0-informational.svg?style=flat-square" alt="FASM v2.0"></a>
  <a href="https://github.com/Bertolzo/Pyscope/actions"><img src="https://img.shields.io/badge/CI-passing-brightgreen.svg?style=flat-square" alt="CI"></a>
</p>

<p align="center">
  <sub>static observation &middot; AST-based &middot; reproducible &middot; 11 architectural regimes</sub>
</p>

---

## \ud83d\udd2d Filosofia

> **PyScope n\u00e3o adivinha. PyScope observa.**

PyScope \u00e9 uma ferramenta de **observa\u00e7\u00e3o arquitetural**, n\u00e3o de governan\u00e7a. Ela existe porque a maioria das ferramentas de arquitetura ainda **mistura m\u00e9tricas com infer\u00eancias** \u2014 entregando opini\u00f5es onde deveriam entregar dados.

O projeto se apoia em **tr\u00eas artefatos formais** que n\u00e3o podem ser confundidos:

| Artefato | Papel | O que define |
|----------|-------|-------------|
| **FASM** | Modelo formal | Ontologia, teoria, axiomas, m\u00e9tricas, invariantes \u2014 *o que* observar |
| **AGS** | Implementa\u00e7\u00e3o | GraphBuilder, parsers, engine de m\u00e9tricas, banco \u2014 *como* observar |
| **PyScope** | Observat\u00f3rio | ObservationSnapshot, RegimeClassification, protocolos C0/C1/C2 \u2014 observa\u00e7\u00e3o \u2192 FASM \u2192 evid\u00eancia |

> FASM n\u00e3o cont\u00eam c\u00f3digo Python. AGS n\u00e3o cria conceitos \u2014 apenas implementa. PyScope n\u00e3o cria teoria \u2014 apenas observa.

---

## \u2699\ufe0f Arquitetura

```
\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557
\u2551                            ENTRY POINTS                                     \u2551
\u2551                                                                            \u2551
\u2551   tools/c1_observe.py      python -m ags           pyscope.visualizer      \u2551
\u2551   (observação remota)      (CLI orquestrada)       (dashboard Observatory)  \u2551
\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u255d\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d
             \u2502                 \u2502                       \u2502
             \u25bc                 \u25bc                       \u2502
   \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510         \u2502
   \u2502         AGS ORCHESTRATOR                \u2502         \u2502
   \u2502      ags/orchestrator.py :: AGS         \u2502         \u2502
   \u2502                                         \u2502         \u2502
   \u2502   \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510  \u2502         \u2502
   \u2502   \u2502 GRAPH  \u2502\u2500\u25b6\u2502STRUCTURAL\u2502\u2500\u25b6\u2502COUPLING\u2502  \u2502         \u2502
   \u2502   \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518  \u2502         \u2502
   \u2502        \u2502           \u2502            \u2502       \u2502         \u2502
   \u2502        \u25bc           \u25bc            \u25bc       \u2502         \u2502
   \u2502   \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510  \u2502         \u2502
   \u2502   \u2502EVOLUTION\u2502\u2500\u25b6\u2502PREDICTION\u2502\u2500\u25b6\u2502GOVERN.  \u2502  \u2502         \u2502
   \u2502   \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518  \u2502         \u2502
   \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518         \u2502
            \u2502            \u2502            \u2502                  \u2502
            \u25bc            \u25bc            \u25bc                  \u25bc
   \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
   \u2502   MODELS + OBSERVATION   \u2502  \u2502       VISUALIZADOR (Observatory)        \u2502
   \u2502                          \u2502  \u2502                                        \u2502
   \u2502  ArchitecturalTwin       \u2502  \u2502  C1Result JSON                         \u2502
   \u2502  ObservationSnapshot     \u2502  \u2502  \u2192 DOT (paleta Observatory)         \u2502
   \u2502  RegimeClassification    \u2502  \u2502  \u2192 SVG                                 \u2502
   \u2502                          \u2502  \u2502  \u2192 HTML dashboard dark                 \u2502
   \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
                \u2502
                \u25bc
   \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
   \u2502     STORAGE (SQLite)     \u2502  \u2502     SYNTHETIC (C0.0)                   \u2502
   \u2502   Database (WAL mode)    \u2502  \u2502  11 regimes can\u00f4nicos                  \u2502
   \u2502   4 reposit\u00f3rios         \u2502  \u2502  CIR-1/2/3/4 invariantes                \u2502
   \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
```

### Fluxo de dados

```
[AST Python] \u2500\u2500\u25b6 GraphBuilder \u2500\u2500\u25b6 ArchitecturalGraph (NetworkX)
                  \u2502
                  \u251c\u2500\u2500\u25b6 cycle_density, dependency_density, drift
                  \u251c\u2500\u2500\u25b6 detect_communities, contamination
                  \u2502
                  \u25bc
            ObservationSnapshot
                  \u2502
                  \u251c\u2500\u2500\u25b6 metrics [0,1]: ACP, DCI, leakage, cycle density
                  \u251c\u2500\u2500\u25b6 classify_from_snapshot() \u2192 RegimeClassification
                  \u2502      \u2514\u2500\u2500 contra REGIME_TAXONOMY (11 atratores)
                  \u2502
                  \u25bc
            Relat\u00f3rio JSON + Dashboard HTML dark
```

---

## \ud83d\udcda M\u00f3dulos

### AGS \u2014 Architectural Governance System

<details>
<summary><strong>ags/core/graph/ \u2014 Grafo Arquitetural</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `ArchitecturalGraph` | Grafo direcionado (NetworkX) com `FileNode`, `ModuleNode`, `ImportEdge` |
| `GraphBuilder` | Parseia AST de projetos Python; resolve imports, subm\u00f3dulos, aliases |
| `cycle_density()` | Fra\u00e7\u00e3o de arestas em ciclos |
| `dependency_density()` | Densidade do grafo de depend\u00eancias |
| `graph_drift()` | Dist\u00e2ncia estrutural entre duas vers\u00f5es do grafo |
| `detect_communities()` | Detec\u00e7\u00e3o Louvain + contamina\u00e7\u00e3o entre fronteiras |

</details>

<details>
<summary><strong>ags/core/observation/ \u2014 Observa\u00e7\u00e3o C1</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `ObservationSnapshot` | M\u00e9tricas primitivas [0,1] no mesmo formato do sint\u00e9tico |
| `compute_observation_snapshot()` | Bridge entre mundo real e taxonomia de regimes |
| `RegimeClassification` | Classifica\u00e7\u00e3o por dist\u00e2ncia euclidiana aos 11 regimes can\u00f4nicos |
| `classify_from_snapshot()` | Retorna regime, nearest, second_nearest, margin, confidence |

</details>

<details>
<summary><strong>ags/core/models/ \u2014 Modelos de Estado</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `ArchitecturalStateVector` | Vetor can\u00f4nico L3 com entropia, acoplamento, CRI, AGP (10 dimens\u00f5es) |
| `ArchitecturalTwin` | G\u00eameo digital: estado + evolu\u00e7\u00e3o + predi\u00e7\u00e3o + governan\u00e7a |

</details>

<details>
<summary><strong>ags/synthetic/ \u2014 Valida\u00e7\u00e3o C0.0</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `RegimeTaxonomy` | 11 regimes can\u00f4nicos (PERFECT, COUPLED, LEAKY, COLLAPSED, MODULAR_*, ENTANGLED_*, MIXED, PATHOLOGICAL, ACYCLIC_DOMINANT) |
| `RegimeAwareGraphGenerator` | Amostrador causal que constr\u00f3i grafos a partir de `FixtureSpec` |
| `SyntheticGraphSet` | Cole\u00e7\u00e3o cobrindo todo o espa\u00e7o de regimes |
| **CIR-1** | Consist\u00eancia causal: regime \u00e9 identific\u00e1vel a partir da estrutura |
| **CIR-2** | Estabilidade sob perturba\u00e7\u00e3o + separa\u00e7\u00e3o entre regimes |
| **CIR-3** | Cobertura do espa\u00e7o de grafos (topologia, densidade, grau) |
| **CIR-4** | Ortogonalidade das m\u00e9tricas primitivas |

</details>

<details>
<summary><strong>ags/intelligence/ \u2014 Evolu\u00e7\u00e3o e Predi\u00e7\u00e3o</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `EvolutionAnalyzer` | Deltas entre snapshots, gradiente de entropia (velocidade/acelera\u00e7\u00e3o), half-life |
| `PredictionEngine` | Proje\u00e7\u00e3o de entropia/CRI em 30/60/90d, confian\u00e7a, risco de colapso |

</details>

<details>
<summary><strong>ags/storage/ \u2014 Persist\u00eancia</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `Database` | SQLite WAL mode com schema versioning (5 tabelas) |
| `SnapshotRepository` | Snapshots estruturais + grafo JSON |
| `CouplingRepository` | Relat\u00f3rios de acoplamento (ACP, DCI) |
| `EvolutionRepository` | Gradiente de entropia, drift, half-life |
| `GovernanceRepository` | Eventos de governan\u00e7a (merge gates, viola\u00e7\u00f5es) |

</details>

### PyScope Visualizer

Converte resultados de observa\u00e7\u00e3o C1 em artefatos visuais com **paleta Observatory**.

| Componente | Responsabilidade |
|------------|-----------------|
| `schema.py` | Schemas `Node`, `Edge`, `C1Result` com `from_json()` |
| `graphviz_builder.py` | Constr\u00f3i string DOT com cor por regime, espessura por ACP/DCI |
| `renderer.py` | Renderiza DOT \u2192 SVG/PNG via Graphviz |
| `html_report.py` | Dashboard HTML dark com cards, legend e hover sutis |
| `cli.py` | CLI: `python -m pyscope.visualizer --input-json ... --output-dir ...` |

**Paleta Observatory aplicada ao grafo:**

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

| Script | Prop\u00f3sito |
|--------|-----------|
| `c1_observe.py` | Observa\u00e7\u00e3o C1: clona repo, constr\u00f3i grafo, classifica regime, exporta JSON |
| `c1_observe_requests.py` | Exemplo pr\u00e1tico observando o reposit\u00f3rio `psf/requests` |
| `verify_baseline.py` | Verifica integridade do baseline do projeto |
| `remote_runner.py` | Execu\u00e7\u00e3o remota de observa\u00e7\u00f5es |
| `resource_adapter.py` | Adaptador de recursos (local vs cloud) |
| `providers/` | Providers cloud (AWS, OCI, Oracle) |

---

## \ud83c\udfaf Escopo

### \u2705 Em escopo

- Projetos Python com estrutura de pacotes padr\u00e3o
- An\u00e1lise **est\u00e1tica** do grafo de imports (AST)
- M\u00e9tricas FASM: ACP, DCI, boundary leakage, cycle density, CRI
- Classifica\u00e7\u00e3o em 11 regimes arquiteturais
- Observa\u00e7\u00e3o remota de reposit\u00f3rios (C1)
- Resultados audit\u00e1veis em JSON
- Visualiza\u00e7\u00e3o Graphviz + dashboard HTML dark (paleta Observatory)
- Gera\u00e7\u00e3o sint\u00e9tica para valida\u00e7\u00e3o de invariantes (C0.0)
- Pipeline GitHub Actions para CI/CD

### \u274c Fora de escopo (deliberadamente)

- An\u00e1lise din\u00e2mica de runtime (profiling, tracing)
- Linguagens que n\u00e3o sejam Python
- Previs\u00f5es de futuro ou causalidade al\u00e9m da topologia estrutural
- Import condicional e `__import__()` com argumentos n\u00e3o literais
- Monorepos massivos sem estrat\u00e9gia de amostragem
- An\u00e1lise de qualidade de c\u00f3digo (linters, style checkers)

---

## \ud83d\ude80 Quick Start

```bash
# Clone
git clone https://github.com/Bertolzo/Pyscope.git
cd Pyscope

# Ambiente virtual
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# Instala\u00e7\u00e3o
python -m pip install -e ".[dev,intelligence]"

# Testes (277 testes \u2014 deve passar limpo)
python -m pytest -q --no-cov
```

---

## \ud83d\udd04 Uso

### Observa\u00e7\u00e3o C1

Observe a arquitetura de qualquer reposit\u00f3rio Python p\u00fablico:

```bash
python -m tools.c1_observe "requests" "https://github.com/psf/requests.git" c1_requests_remote
```

Sa\u00edda esperada:

```
\ud83d\udce6 Observando requests de https://github.com/psf/requests.git
\u251c\u2500\u2500 \u2705 Clone conclu\u00eddo
\u251c\u2500\u2500 \u2705 Grafo constru\u00eddo: 37 files, 81 edges
\u251c\u2500\u2500 \ud83d\udcca ObservationSnapshot
\u2502   \u251c\u2500\u2500 cross_domain_ratio:   0.00
\u2502   \u251c\u2500\u2500 intra_domain_ratio:   1.00
\u2502   \u251c\u2500\u2500 leakage:              0.00
\u2502   \u251c\u2500\u2500 cycle_density:        0.58
\u2502   \u2514\u2500\u2500 quality:              1.00
\u251c\u2500\u2500 \ud83c\udff7\ufe0f  RegimeClassification
\u2502   \u251c\u2500\u2500 regime:               MIXED
\u2502   \u251c\u2500\u2500 nearest:              MIXED (dist: 2.65)
\u2502   \u251c\u2500\u2500 margin:               0.15
\u2502   \u2514\u2500\u2500 confidence:           0.27
\u2514\u2500\u2500 \u2705 Artefato: c1_requests_result.json
```

### Visualizador

Converta um resultado C1 em grafo + dashboard HTML dark:

```bash
python -m pyscope.visualizer \
  --input-json tests/fixtures/c1_example.json \
  --output-dir out/visual
```

Gera:

```
out/
\u251c\u2500\u2500 graph.dot        # Grafo em formato DOT (paleta Observatory)
\u251c\u2500\u2500 graph.svg        # Renderiza\u00e7\u00e3o SVG
\u251c\u2500\u2500 graph.png        # Renderiza\u00e7\u00e3o PNG
\u2514\u2500\u2500 index.html       # Dashboard HTML dark
```

O dashboard HTML tem:

- **Header** limpo com t\u00edtulo em `var(--accent)` (`#38BDF8`)
- **Cards** coloridos por tipo de m\u00e9trica (accent/success/warn/danger)
- **SVG do grafo** com fundo `#0A0E17` e n\u00f3s coloridos por regime
- **Legend** com swatches de cores e borda
- **Hover effects** sutis (translateY, shadow leve)
- **Footer** com hash do artefato gerado

### CLI AGS

```bash
# Analisar um projeto local
ags analyze /caminho/para/projeto

# Ver hist\u00f3rico de observa\u00e7\u00f5es
ags history

# Proje\u00e7\u00e3o de m\u00e9tricas
ags forecast
```

---

## \ud83d\udcdd Design Decisions

| Decis\u00e3o | Justificativa |
|---------|---------------|
| **M\u00e9tricas [0,1] em vez de scores [0,100]** | Alinhamento com o modelo formal FASM; permite compara\u00e7\u00e3o direta com a taxonomia sint\u00e9tica |
| **cycle_density = edges_in_cycles / total_edges** | Mede acoplamento c\u00edclico real (n\u00e3o complexidade ciclom\u00e1tica) |
| **intra_domain_ratio direto (n\u00e3o 1 - cross)** | Revela gaps de classifica\u00e7\u00e3o quando ambos s\u00e3o baixos |
| **Self-loops ignorados** | N\u00e3o representam depend\u00eancia arquitetural entre entidades distintas |
| **confidence = quality / (1 + distance)** | Mapeia qualquer dist\u00e2ncia a (0, 1]; quality penaliza observa\u00e7\u00f5es parciais |
| **Parser via AST (n\u00e3o regex)** | AST capta a sem\u00e2ntica real do c\u00f3digo; regex falha em imports condicionais e din\u00e2micos |
| **SQLite WAL mode** | Leitores n\u00e3o bloqueiam escritores; ideal para pipelines CI |
| **Twin digital separado do snapshot** | Snapshot \u00e9 o estado atual; twin \u00e9 o agregado estado + hist\u00f3rico + predi\u00e7\u00e3o |
| **Paleta Observatory no visualizador** | Identidade visual pr\u00f3pria: navy + sky-blue, sem neon |

---

## \ud83d\udcda Testes

O projeto possui **277 testes** organizados em:

| Suite | Testes | O que valida |
|-------|:------:|-------------|
| `test_graph*` | 65 | Grafo, builder, m\u00e9tricas, invariantes, serializa\u00e7\u00e3o |
| `test_observation` | 22 | ObservationSnapshot, quality, cycles, domains |
| `test_classification` | 18 | RegimeClassification, invariantes, confidence |
| `test_math_invariants` | 26 | Limites formais de ACP, DCI, leakage, CRI, AGP |
| `test_synthetic_c00` | 60 | CIR-1, CIR-2, CIR-3, CIR-4, ortogonalidade |
| `test_baseline` | 24 | Baseline file, parsing, verifica\u00e7\u00e3o, versionamento |
| `test_snapshot_consistency` | 5 | Roundtrip de snapshots, coupling, evolution, governance |
| `test_visualizer` | 3 | Schema, DOT builder, renderer |
| Demais | 54 | MCP, provisionamento, remote runner, resource adapter |

```bash
# Rodar todos os testes
python -m pytest -q --no-cov

# Com cobertura
python -m pytest --cov=ags --cov=pyscope --cov-report=term-missing

# Testes espec\u00edficos
python -m pytest tests/test_graph.py tests/test_observation.py -v
```

---

## \u2699\ufe0f GitHub Actions

| Workflow | Trigger | O que faz |
|----------|---------|-----------|
| `c1_observe.yml` | `workflow_dispatch` | Executa observa\u00e7\u00e3o C1 remota e publica artefato JSON |
| `visualizer-ci.yml` | Push em `scope/**` | Roda visualizador, valida sa\u00edda DOT/SVG/HTML |

---

## \ud83c\udf3f Branching

| Branch | Prop\u00f3sito |
|--------|-----------|
| `main` | Linha est\u00e1vel para early adopters |
| `develop` | Valida\u00e7\u00e3o antes de promo\u00e7\u00e3o para main |
| `feature/*` | Novos recursos funcionais |
| `exp/*` | Experimentos e pesquisa |
| `doc/*` | Mudan\u00e7as de escopo e contrato |
| `hotfix/*` | Corre\u00e7\u00f5es urgentes |
| `scope/*` | Branches de escopo do visualizador |

---

## \ud83d\ude4f Contribui\u00e7\u00e3o

1. Abra um issue descrevendo o caso de uso
2. Escolha a branch adequada conforme a branching strategy
3. Preencha o template de PR
4. Execute as valida\u00e7\u00f5es obrigat\u00f3rias:

```bash
python -m pytest -q --no-cov
python tools/verify_baseline.py
```

5. Atualize a documenta\u00e7\u00e3o sempre que houver altera\u00e7\u00e3o de m\u00e9tricas, escopo ou comportamento
6. Submeta o PR para revis\u00e3o

---

## \ud83d\udcc1 Estrutura do Reposit\u00f3rio

```
ags/                              # N\u00facleo AGS
\u251c\u2500\u2500 __init__.py
\u251c\u2500\u2500 __main__.py                   # Entry point: python -m ags
\u251c\u2500\u2500 orchestrator.py               # Pipeline de 6 camadas
\u251c\u2500\u2500 cli/                          # CLI Typer (analyze, history, forecast)
\u251c\u2500\u2500 core/                         # Core: graph, observation, models, structural, coupling, governance
\u251c\u2500\u2500 intelligence/                 # Evolu\u00e7\u00e3o e predi\u00e7\u00e3o
\u251c\u2500\u2500 storage/                      # SQLite WAL + 4 reposit\u00f3rios
\u2514\u2500\u2500 synthetic/                    # Gera\u00e7\u00e3o sint\u00e9tica (11 regimes, CIR-1/2/3/4)

pyscope/                          # Visualizador (paleta Observatory)
\u2514\u2500\u2500 visualizer/
    \u251c\u2500\u2500 cli.py                    # CLI entry point
    \u251c\u2500\u2500 graphviz_builder.py       # DOT builder (paleta Observatory)
    \u251c\u2500\u2500 html_report.py            # Dashboard HTML dark
    \u251c\u2500\u2500 renderer.py               # DOT \u2192 SVG/PNG
    \u2514\u2500\u2500 schema.py                 # C1Result, Node, Edge

assets/                           # Recursos visuais
\u251c\u2500\u2500 pyscope-banner.svg            # Banner SVG do README
\u2514\u2500\u2500 favicon.svg                   # Favicon (32x32)

tools/                            # Scripts operacionais
\u251c\u2500\u2500 c1_observe.py                 # Observa\u00e7\u00e3o C1 remota
\u251c\u2500\u2500 c1_observe_requests.py        # Exemplo com requests
\u251c\u2500\u2500 verify_baseline.py
\u251c\u2500\u2500 remote_runner.py
\u251c\u2500\u2500 resource_adapter.py
\u2514\u2500\u2500 providers/                    # AWS, OCI, Oracle

docs/                             # Modelo cient\u00edfico e limita\u00e7\u00f5es
tests/                            # 277 testes
.github/                          # Workflows + templates
```

---

<p align="center">
  <img src="https://img.shields.io/badge/PyScope-v2.0.0-blue.svg?style=flat-square" alt="v2.0.0">
  <img src="https://img.shields.io/badge/observation-not_inference-informational.svg?style=flat-square" alt="observation">
  <img src="https://img.shields.io/badge/data-not_opinion-success.svg?style=flat-square" alt="data">
</p>

<p align="center">
  <strong>PyScope</strong> &mdash; transformando arquitetura Python em<br>
  <em>decis\u00f5es t\u00e9cnicas fundadas, audit\u00e1veis e reproduz\u00edveis.</em><br><br>
  <sub>Observa\u00e7\u00e3o, n\u00e3o adivinha\u00e7\u00e3o. Dados, n\u00e3o opini\u00f5es.</sub>
</p>
