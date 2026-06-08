# PyScope

[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/downloads/release/python-3120/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**PyScope** é a plataforma de observação arquitetural para projetos Python.
Ela converte dependências estáticas em métricas auditáveis, classificações arquiteturais, artefatos reproduzíveis e visualizações claras.

> Observação arquitetural prática para decisões técnicas fundamentadas.

---

## O que é

PyScope é uma ferramenta de **observação**, não de governança. Ela foca em:

- **AGS (Architectural Governance System)** — núcleo de análise estática do grafo de imports, métricas FASM e classificação arquitetural
- **PyScope Visualizer** — conversão de resultados C1 em grafos Graphviz e relatórios HTML
- Resultados reproduzíveis e artefatos JSON auditáveis
- Workflows GitHub Actions para validação remota

## Por que PyScope existe

Muitas ferramentas conflitam métricas com inferências; **PyScope** foca em observação rigorosa e reproducibilidade:

- observação do estado atual do código Python
- métricas com escopo e limitações documentadas
- resultados reproduzíveis via GitHub Actions
- artefatos compactos para validação e auditoria

## Para quem é

- arquitetos e líderes técnicos Python
- equipes de modernização de arquitetura
- pesquisadores e early adopters que exigem pipelines auditáveis

## O que já está implementado

- análise estática do grafo de imports em Python
- parser robusto de imports que evita duplicação de arestas e resolve submódulos `from pkg import sub`
- detecção de imports múltiplos (`import a, b`) como arestas separadas
- métricas FASM: ACP, DCI, leakage, cycle density, CRI
- classificação de regimes arquiteturais
- observação C1 em repositórios reais
- geração de snapshots e resultados JSON
- visualizador Graphviz com relatório HTML
- workflow GitHub Actions para validação remota

## Escopo

### Em escopo

- projetos Python
- análise estática do import graph
- observação real de projetos (C1)
- resultados auditáveis em JSON
- documentação explícita de limitações

### Fora de escopo

- análise dinâmica de runtime
- linguagens não Python
- previsões de futuro ou causalidade além da topologia estrutural
- import condicional e reflection sem cobertura explícita

## Como começar

```bash
git clone https://github.com/Bertolzo/Pyscope.git
cd Pyscope
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest pytest-cov
```

## Uso rápido

### Observação C1

```bash
python -m tools.c1_observe "requests" "https://github.com/psf/requests.git" c1_requests_remote
```

### Visualizador

```bash
python -m pyscope.visualizer --input-json tests/fixtures/c1_example.json --output-dir out/visual
```

### Saída esperada do visualizador

- `out/graph.dot`
- `out/graph.svg` (se Graphviz estiver instalado)
- `out/graph.png` (se Graphviz estiver instalado)
- `out/index.html`

## GitHub-ready

Este projeto inclui:

- workflow de dispatch GitHub Actions (`c1_observe.yml`)
- workflow do visualizador (`visualizer-ci.yml`)
- upload de artifact com resultado JSON e repositório observado
- templates de PR e issue
- guia de contribuição e código de conduta

## Branching estratégico

- `main` — linha estável para early adopters
- `develop` — validação antes de promoção
- `feature/*` — novos recursos funcionais
- `exp/*` — experimentos e pesquisa
- `doc/*` — mudanças de escopo e contrato
- `hotfix/*` — correções urgentes
- `scope/*` — branches de escopo do visualizador

## Contribuição

1. Abra um issue com o caso de uso.
2. Escolha a branch adequada.
3. Preencha o template de PR.
4. Execute validações:

```bash
python -m pytest -q
python tools/verify_baseline.py
```

5. Atualize a documentação sempre que houver alteração de métricas ou comportamento.

## Estrutura do repositório

```
ags/                          # Núcleo AGS — Architectural Governance System
├── cli/                      # CLI (comando `ags`)
├── core/                     # Core: coupling, governance, graph, models, observation, structural
├── intelligence/             # Inteligência: evolução e predição
├── storage/                  # Armazenamento: banco e repositórios
└── synthetic/                # Geração sintética para validação

pyscope/                      # PyScope Visualizer
├── core/                     # Core do visualizador
└── visualizer/               # Módulo de visualização Graphviz
    ├── schema.py
    ├── graphviz_builder.py
    ├── renderer.py
    ├── html_report.py
    └── cli.py

tools/                        # Scripts operacionais
├── c1_observe.py             # Observação C1 remota
├── c1_observe_requests.py    # Exemplo com requests
├── providers/                # Providers cloud (AWS, OCI, Oracle)
└── ...

docs/                         # Modelo científico e limitações
tests/                        # Validação de comportamento
├── fixtures/                 # Fixtures de teste
├── test_visualizer/          # Testes do visualizador
└── ...
```

## Posicionamento

**PyScope** é uma plataforma de observação arquitetural para quem precisa de dados auditáveis e reproduzíveis. Use este repositório para transformar arquitetura Python em decisões técnicas fundadas e verificáveis.
