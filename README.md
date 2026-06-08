# PyScope

PyScope é um observatório arquitetural para projetos Python. Ele foca em observação estática do grafo de imports, métricas de arquitetura e artefatos auditáveis.

Este repositório ainda mantém o núcleo atual em `ags/`, mas o posicionamento público é PyScope: um observatório, não uma plataforma de governança.

## O que é PyScope

- um observatório arquitetural para código Python
- uma ferramenta de visão, não de governança
- focada no estado atual do projeto
- produz resultados reproduzíveis e artefatos JSON

## Visualizador

O módulo `pyscope.visualizer` converte resultados C1 em um grafo Graphviz e gera um relatório HTML.

### Exemplo

```bash
python -m pyscope.visualizer --input-json tests/fixtures/c1_example.json --output-dir out/visual
```

### Artefatos gerados

- `out/graph.dot`
- `out/graph.svg` (se Graphviz estiver instalado)
- `out/graph.png` (se Graphviz estiver instalado)
- `out/index.html`

## CI

A workflow `.github/workflows/visualizer-ci.yml` roda o visualizador em branches `scope/**` e publica os artefatos.

## Estrutura do visualizador

- `pyscope/visualizer/schema.py`
- `pyscope/visualizer/graphviz_builder.py`
- `pyscope/visualizer/renderer.py`
- `pyscope/visualizer/html_report.py`
- `pyscope/visualizer/cli.py`

## Observação

PyScope é um experimento de observabilidade; ele não implementa políticas de governança nem decisões de arquitetura automáticas.
