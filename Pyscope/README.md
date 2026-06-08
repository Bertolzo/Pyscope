# Pyscope — Observatório Arquitetural para Python

Pyscope é um observatório: coleta, modela e relata a estrutura de código Python.

Visão rápida
- Não é uma ferramenta de governança — é um instrumento de visão.
- Produz artefatos auditáveis (JSON), métricas FASM e relatórios estáticos.

Instalação (desenvolvimento)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Uso (exemplo)
```bash
python -m pyscope.visualizer --input-json tests/fixtures/c1_example.json --output-dir out/visual
```

Contribuição
- Experimentos: crie `scope/*` e abra PR contra `develop`.
- Mudanças de contrato/escopo: crie `contract/*`.
