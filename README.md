# PyScope

PyScope é um observatório arquitetural para código Python. Ele foca em observação estática do grafo de imports, métricas de arquitetura, artefatos auditáveis e visualizações claras.

## O que é PyScope

- uma ferramenta de observação, não de governança
- voltada para análise do estado atual do código
- produz resultados reproduzíveis e artefatos JSON
- integra visualização Graphviz para inspeção do grafo

## Visualizador

O módulo `pyscope.visualizer` converte um resultado C1 em um grafo Graphviz e gera um relatório HTML.

### Exemplo de uso

```bash
python -m pyscope.visualizer --input-json tests/fixtures/c1_example.json --output-dir out/visual
```

### Saída esperada

- `out/graph.dot`
- `out/graph.svg` (se Graphviz estiver instalado)
- `out/graph.png` (se Graphviz estiver instalado)
- `out/index.html`

## CI

A workflow `.github/workflows/visualizer-ci.yml` roda o visualizador em branches `scope/**` e publica artefatos.

## Estrutura do visualizador

- `pyscope/visualizer/schema.py`
- `pyscope/visualizer/graphviz_builder.py`
- `pyscope/visualizer/renderer.py`
- `pyscope/visualizer/html_report.py`
- `pyscope/visualizer/cli.py`
