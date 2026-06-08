# Architectural Observatory

[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/Bertolzo/architectural-governance/.github/workflows/c1_observe.yml?branch=main)](https://github.com/Bertolzo/architectural-governance/actions)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/downloads/release/python-3120/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## O que é

`AGS` é a plataforma de governança arquitetural observacional para projetos Python.
Ele converte dependências estáticas em métricas confiáveis, classificações arquiteturais e artefatos auditáveis.

> Observação arquitetural real para decisões técnicas sem ambiguidade.

## Por que AGS existe

Muitas ferramentas ainda misturam métricas e inferências. O AGS entrega:

- observação do estado atual do código Python
- métricas com contrato de escopo e limitações claras
- resultados reproduzíveis via GitHub Actions
- artefatos compactos para validação externa

## Para quem é

- arquitetos e líderes técnicos Python
- equipes de modernização de arquitetura
- early adopters que testam métricas em código real
- pesquisadores que exigem pipeline auditável

## O que já está implementado

- análise estática de grafo de imports em Python
- métricas FASM: ACP, DCI, leakage, cycle density, CRI
- classificação de regimes arquiteturais
- observação C1 em repositórios reais
- geração de snapshots e resultados JSON
- workflow GitHub Actions para validação remota

## Escopo

### Em escopo

- projetos Python
- análise de import graph estático
- observação real de projetos (C1)
- resultados auditáveis em JSON
- documentação explícita de limitações

### Fora de escopo

- análise dinâmica de runtime
- linguagens não Python
- previsões de futuro
- causalidade além da descrição estrutural
- monorepos massivos sem estratégia de amostragem
- import condicional e reflection

## Como começar

```bash
git clone https://github.com/Bertolzo/architectural-governance.git
cd architectural-governance
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest pytest-cov
```

## Uso rápido

```bash
python -m tools.c1_observe "requests" "https://github.com/psf/requests.git" c1_requests_remote
```

## Validação imediata

Verifique que o artefato contém:

- `c1_requests_result.json`
- `/tmp/opencode/c1_requests_remote`

## GitHub-ready

Este projeto já possui:

- workflow de dispatch GitHub Actions
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

## Contribuição

1. Abra um issue com o caso de uso.
2. Escolha a branch adequada.
3. Preencha o template de PR.
4. Execute validações:

```bash
python -m pytest -q
python tools/verify_baseline.py
```

5. Atualize a documentação sempre que houver alteração de métricas ou escopo.

## Estrutura do repositório

- `ags/` — núcleo do sistema
- `tools/` — scripts operacionais
- `docs/` — modelo científico e limitações
- `tests/` — validação de comportamento

## Posicionamento

O AGS é uma plataforma de governança arquitetural para quem precisa de observação, não de adivinhação.
Use este repositório para transformar arquitetura Python em decisões técnicas fundadas e auditáveis.
