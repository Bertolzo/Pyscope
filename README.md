<p align="center">
  <img src="assets/header.svg" alt="PyScope — Architectural Observatory" width="100%">
</p>

<p align="center">
  <a href="https://github.com/Bertolzo/Pyscope/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-10B981?style=for-the-badge" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12+-8B5CF6?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12+"></a>
  <a href="#testes"><img src="https://img.shields.io/badge/tests-277%20passed-10B981?style=for-the-badge" alt="277 tests"></a>
  <a href="#escopo"><img src="https://img.shields.io/badge/FASM-v2.0-06B6D4?style=for-the-badge" alt="FASM v2.0"></a>
  <a href="https://github.com/Bertolzo/Pyscope/actions"><img src="https://img.shields.io/badge/CI-GitHub_Actions-F59E0B?style=for-the-badge&logo=githubactions&logoColor=white" alt="CI"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/observation-not_inference-8A8A9A?style=flat-square" alt="observation not inference">
  <img src="https://img.shields.io/badge/static-AST--based-8A8A9A?style=flat-square" alt="static AST-based">
  <img src="https://img.shields.io/badge/regimes-11_canonical-8A8A9A?style=flat-square" alt="11 regimes">
  <img src="https://img.shields.io/badge/reproducible-100%25-8A8A9A?style=flat-square" alt="100% reproducible">
</p>

<p align="center">
  <sub>
    <a href="#filosofia">Filosofia</a> &middot;
    <a href="#arquitetura">Arquitetura</a> &middot;
    <a href="#m\u00f3dulos">M\u00f3dulos</a> &middot;
    <a href="#escopo">Escopo</a> &middot;
    <a href="#quick-start">Quick Start</a> &middot;
    <a href="#uso">Uso</a> &middot;
    <a href="#design-decisions">Design</a> &middot;
    <a href="#testes">Testes</a>
  </sub>
</p>

---

## <span style="color:#8B5CF6">Filosofia</span>

> **PyScope n\u00e3o adivinha. PyScope observa.**

PyScope \u00e9 uma ferramenta de **observa\u00e7\u00e3o**, n\u00e3o de governan\u00e7a. Ela existe porque a maioria das ferramentas de arquitetura ainda **mistura m\u00e9tricas com infer\u00eancias** \u2014 entregando opini\u00f5es onde deveriam entregar dados.

O projeto se apoia em **tr\u00eas artefatos formais** que n\u00e3o podem ser confundidos:

<table>
<tr>
<th style="color:#8B5CF6">FASM</th>
<th style="color:#06B6D4">AGS</th>
<th style="color:#10B981">PyScope</th>
</tr>
<tr>
<td><strong>Modelo formal</strong></td>
<td><strong>Implementa\u00e7\u00e3o</strong></td>
<td><strong>Observat\u00f3rio</strong></td>
</tr>
<tr>
<td>Ontologia, teoria, axiomas, m\u00e9tricas, invariantes</td>
<td>GraphBuilder, parsers, engine de m\u00e9tricas, banco</td>
<td>ObservationSnapshot, RegimeClassification, protocolos C0/C1/C2</td>
</tr>
<tr>
<td><em>o que</em> observar</td>
<td><em>como</em> observar</td>
<td>observa\u00e7\u00e3o \u2192 FASM \u2192 evid\u00eancia</td>
</tr>
</table>

> FASM n\u00e3o cont\u00eam c\u00f3digo Python. AGS n\u00e3o cria conceitos \u2014 apenas implementa. PyScope n\u00e3o cria teoria \u2014 apenas observa.

---

## <span style="color:#06B6D4">Arquitetura</span>

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                            ENTRY POINTS                                     ║
║                                                                            ║
║   tools/c1_observe.py      python -m ags           pyscope.visualizer      ║
║   (observação remota)      (CLI orquestrada)       (dashboard dark)        ║
╚════════════╤═════════════════╤═══════════════════════╤═══════════════════════╝
             │                 │                       │
             ▼                 ▼                       │
   ┌─────────────────────────────────────────┐         │
   │         AGS ORCHESTRATOR                │         │
   │      ags/orchestrator.py :: AGS         │         │
   │                                         │         │
   │   ┌────────┐  ┌──────────┐  ┌────────┐  │         │
   │   │ GRAPH  │─▶│STRUCTURAL│─▶│COUPLING│  │         │
   │   └────┬───┘  └────┬─────┘  └───┬────┘  │         │
   │        │           │            │       │         │
   │        ▼           ▼            ▼       │         │
   │   ┌─────────┐  ┌──────────┐  ┌────────┐  │         │
   │   │EVOLUTION│─▶│PREDICTION│─▶│GOVERN. │  │         │
   │   └────┬────┘  └────┬─────┘  └───┬────┘  │         │
   └────────┼────────────┼────────────┼────────┘         │
            │            │            │                  │
            ▼            ▼            ▼                  ▼
   ┌──────────────────────────┐  ┌────────────────────────────┐
   │   MODELS + OBSERVATION   │  │       VISUALIZADOR         │
   │                          │  │                            │
   │  ArchitecturalTwin       │  │  C1Result JSON             │
   │  ObservationSnapshot     │  │  → DOT (paleta Minimax)    │
   │  RegimeClassification    │  │  → SVG                     │
   │                          │  │  → HTML dashboard dark     │
   └────────────┬─────────────┘  └────────────────────────────┘
                │
                ▼
   ┌──────────────────────────┐  ┌────────────────────────────┐
   │     STORAGE (SQLite)     │  │     SYNTHETIC (C0.0)       │
   │   Database (WAL mode)    │  │  11 regimes canônicos      │
   │   4 repositórios         │  │  CIR-1/2/3/4 invariantes   │
   └──────────────────────────┘  └────────────────────────────┘
```

### <span style="color:#10B981">Fluxo de dados</span>

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
            Relatório JSON + Dashboard HTML dark
```

---

## <span style="color:#10B981">Módulos</span>

### AGS — Architectural Governance System

<details>
<summary><strong style="color:#8B5CF6">ags/core/graph/ — Grafo Arquitetural</strong></summary>

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
<summary><strong style="color:#06B6D4">ags/core/observation/ — Observação C1</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `ObservationSnapshot` | Métricas primitivas [0,1] no mesmo formato do sintético |
| `compute_observation_snapshot()` | Bridge entre mundo real e taxonomia de regimes |
| `RegimeClassification` | Classificação por distância euclidiana aos 11 regimes canônicos |
| `classify_from_snapshot()` | Retorna regime, nearest, second_nearest, margin, confidence |

</details>

<details>
<summary><strong style="color:#10B981">ags/core/models/ — Modelos de Estado</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `ArchitecturalStateVector` | Vetor canônico L3 com entropia, acoplamento, CRI, AGP (10 dimensões) |
| `ArchitecturalTwin` | Gêmeo digital: estado + evolução + predição + governança |

</details>

<details>
<summary><strong style="color:#F59E0B">ags/synthetic/ — Validação C0.0</strong></summary>

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
<summary><strong style="color:#F472B6">ags/intelligence/ — Evolução e Predição</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `EvolutionAnalyzer` | Deltas entre snapshots, gradiente de entropia (velocidade/aceleração), half-life |
| `PredictionEngine` | Projeção de entropia/CRI em 30/60/90d, confiança, risco de colapso |

</details>

<details>
<summary><strong style="color:#3B82F6">ags/storage/ — Persistência</strong></summary>

| Componente | Responsabilidade |
|------------|-----------------|
| `Database` | SQLite WAL mode com schema versioning (5 tabelas) |
| `SnapshotRepository` | Snapshots estruturais + grafo JSON |
| `CouplingRepository` | Relatórios de acoplamento (ACP, DCI) |
| `EvolutionRepository` | Gradiente de entropia, drift, half-life |
| `GovernanceRepository` | Eventos de governança (merge gates, violações) |

</details>

### <span style="color:#8B5CF6">PyScope Visualizer</span>

Converte resultados de observação C1 em artefatos visuais com **paleta Minimax dark**.

| Componente | Responsabilidade |
|------------|-----------------|
| `schema.py` | Schemas `Node`, `Edge`, `C1Result` com `from_json()` |
| `graphviz_builder.py` | Constrói string DOT com cor por regime, espessura por ACP/DCI |
| `renderer.py` | Renderiza DOT → SVG/PNG via Graphviz |
| `html_report.py` | Dashboard HTML dark com cards, gradientes e legend interativo |
| `cli.py` | CLI: `python -m pyscope.visualizer --input-json ... --output-dir ...` |

**Paleta de cores Minimax aplicada ao grafo:**

<table>
<tr><th>Regime</th><th>Cor</th><th>Uso</th></tr>
<tr><td><code>perfect</code></td><td><span style="color:#10B981">■</span> #10B981</td><td>emerald</td></tr>
<tr><td><code>modular_*</code></td><td><span style="color:#8B5CF6">■</span> #8B5CF6</td><td>violet</td></tr>
<tr><td><code>layered</code></td><td><span style="color:#06B6D4">■</span> #06B6D4</td><td>cyan</td></tr>
<tr><td><code>entangled_*</code></td><td><span style="color:#F59E0B">■</span> #F59E0B</td><td>amber</td></tr>
<tr><td><code>coupled</code></td><td><span style="color:#EF4444">■</span> #EF4444</td><td>red</td></tr>
<tr><td><code>leaky</code></td><td><span style="color:#F472B6">■</span> #F472B6</td><td>pink</td></tr>
<tr><td><code>collapsed</code></td><td><span style="color:#DC2626">■</span> #DC2626</td><td>deep red</td></tr>
<tr><td><code>mixed</code></td><td><span style="color:#A78BFA">■</span> #A78BFA</td><td>light violet</td></tr>
<tr><td><code>acyclic_dominant</code></td><td><span style="color:#22D3EE">■</span> #22D3EE</td><td>light cyan</td></tr>
</table>

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

## <span style="color:#F472B6">Escopo</span>

### <span style="color:#10B981">✅ Em escopo</span>

- Projetos Python com estrutura de pacotes padrão
- Análise **estática** do grafo de imports (AST)
- Métricas FASM: ACP, DCI, boundary leakage, cycle density, CRI
- Classificação em 11 regimes arquiteturais
- Observação remota de repositórios (C1)
- Resultados auditáveis em JSON
- Visualização Graphviz + dashboard HTML dark (paleta Minimax)
- Geração sintética para validação de invariantes (C0.0)
- Pipeline GitHub Actions para CI/CD

### <span style="color:#EF4444">❌ Fora de escopo (deliberadamente)</span>

- Análise dinâmica de runtime (profiling, tracing)
- Linguagens que não sejam Python
- Previsões de futuro ou causalidade além da topologia estrutural
- Import condicional e `__import__()` com argumentos não literais
- Monorepos massivos sem estratégia de amostragem
- Análise de qualidade de código (linters, style checkers)

---

## <span style="color:#06B6D4">Quick Start</span>

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

## <span style="color:#8B5CF6">Uso</span>

### <span style="color:#10B981">Observação C1</span>

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

### <span style="color:#06B6D4">Visualizador</span>

Converta um resultado C1 em grafo + dashboard HTML dark:

```bash
python -m pyscope.visualizer \
  --input-json tests/fixtures/c1_example.json \
  --output-dir out/visual
```

Gera:

```
out/
├── graph.dot        # Grafo em formato DOT (paleta Minimax)
├── graph.svg        # Renderização SVG
├── graph.png        # Renderização PNG
└── index.html       # Dashboard HTML dark (cards, gradientes, legend)
```

O dashboard HTML tem:

- **Header** com gradiente roxo→ciano→verde
- **Cards** coloridos por tipo de métrica (purple/cyan/emerald/amber/pink)
- **SVG do grafo** com fundo `#0D0D0F` e nós coloridos por regime
- **Legend interativa** com swatches de cores
- **Hover effects** sutis (translateY, shadow roxo)
- **Footer** com hash do artefato gerado

### <span style="color:#F59E0B">CLI AGS</span>

```bash
# Analisar um projeto local
ags analyze /caminho/para/projeto

# Ver histórico de observações
ags history

# Projeção de métricas
ags forecast
```

---

## <span style="color:#F59E0B">Ciclo de vida de uma observação</span>

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
   → Visualizador: DOT (paleta Minimax) → SVG → Dashboard HTML dark
```

---

## <span style="color:#A78BFA">Design Decisions</span>

<table>
<tr>
<th style="color:#8B5CF6">Decisão</th>
<th style="color:#06B6D4">Justificativa</th>
</tr>
<tr>
<td><strong>Métricas [0,1] em vez de scores [0,100]</strong></td>
<td>Alinhamento com o modelo formal FASM; permite comparação direta com a taxonomia sintética</td>
</tr>
<tr>
<td><strong>cycle_density = edges_in_cycles / total_edges</strong></td>
<td>Mede acoplamento cíclico real (não complexidade ciclomática)</td>
</tr>
<tr>
<td><strong>intra_domain_ratio direto (não 1 - cross)</strong></td>
<td>Revela gaps de classificação quando ambos são baixos</td>
</tr>
<tr>
<td><strong>Self-loops ignorados</strong></td>
<td>Não representam dependência arquitetural entre entidades distintas</td>
</tr>
<tr>
<td><strong>confidence = quality / (1 + distance)</strong></td>
<td>Mapeia qualquer distância a (0, 1]; quality penaliza observações parciais</td>
</tr>
<tr>
<td><strong>Parser via AST (não regex)</strong></td>
<td>AST capta a semântica real do código; regex falha em imports condicionais e dinâmicos</td>
</tr>
<tr>
<td><strong>SQLite WAL mode</strong></td>
<td>Leitores não bloqueiam escritores; ideal para pipelines CI</td>
</tr>
<tr>
<td><strong>Twin digital separado do snapshot</strong></td>
<td>Snapshot é o estado atual; twin é o agregado estado + histórico + predição</td>
</tr>
<tr>
<td><strong>Paleta dark Minimax no visualizador</strong></td>
<td>Contraste forte, hierarquia visual clara, identidade diferenciada</td>
</tr>
</table>

---

## <span style="color:#22D3EE">Testes</span>

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

## <span style="color:#06B6D4">GitHub Actions</span>

| Workflow | Trigger | O que faz |
|----------|---------|-----------|
| `c1_observe.yml` | `workflow_dispatch` | Executa observação C1 remota e publica artefato JSON |
| `visualizer-ci.yml` | Push em `scope/**` | Roda visualizador, valida saída DOT/SVG/HTML |

---

## <span style="color:#10B981">Branching</span>

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

## <span style="color:#8B5CF6">Contribuição</span>

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

## <span style="color:#22D3EE">Estrutura do Repositório</span>

```
ags/                              # Núcleo AGS
├── __init__.py
├── __main__.py                   # Entry point: python -m ags
├── orchestrator.py               # Pipeline de 6 camadas
├── cli/                          # CLI Typer (analyze, history, forecast)
├── core/                         # Core: graph, observation, models, structural, coupling, governance
├── intelligence/                 # Evolução e predição
├── storage/                      # SQLite WAL + 4 repositórios
└── synthetic/                    # Geração sintética (11 regimes, CIR-1/2/3/4)

pyscope/                          # Visualizador (paleta Minimax)
├── __init__.py
└── visualizer/
    ├── cli.py                    # CLI entry point
    ├── graphviz_builder.py       # DOT builder (paleta Minimax)
    ├── html_report.py            # Dashboard HTML dark
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
├── providers/                    # AWS, OCI, Oracle
└── ...

docs/                             # Modelo científico e limitações
tests/                            # 277 testes
.github/                          # Workflows + templates
```

---

<p align="center">
  <img src="https://img.shields.io/badge/PyScope-v2.0.0-8B5CF6?style=for-the-badge" alt="v2.0.0">
  <img src="https://img.shields.io/badge/observation-not_inference-06B6D4?style=for-the-badge" alt="observation">
  <img src="https://img.shields.io/badge/data-not_opinion-10B981?style=for-the-badge" alt="data">
</p>

<p align="center">
  <strong>PyScope</strong> &mdash; transformando arquitetura Python em<br>
  <em>decisões técnicas fundadas, auditáveis e reproduzíveis.</em><br><br>
  <sub>Observação, não adivinhação. Dados, não opiniões.</sub>
</p>
