# System Overview

## O que o sistema faz

O AGS (Architectural Governance System) é uma plataforma para observar,
medir e classificar a arquitetura de software a partir de snapshots estáticos
de código. O objetivo é fornecer sinais acionáveis para governança arquitetural
por meio de métricas, classificação de "regimes" e um protocolo científico de
validação (FASM/Scientific Change Protocol).

Resumo do fluxo principal:
- Construção do grafo arquitetural (`GraphBuilder` → `ArchitecturalGraph`).
- Extração de métricas primitivas em um `ObservationSnapshot`.
- Classificação do snapshot em um `RegimeClassification` usando a
  taxonomia sintética (`REGIME_TAXONOMY`).
- Gate checks (qualidade, margem, distância estrutural) e geração de relatório.

## Componentes principais

- `ags/core/graph/builders.py` — extrai arquivos, parseia imports e monta
  o `ArchitecturalGraph`.
- `ags/core/graph/architectural_graph.py` — representação central (NetworkX).
- `ags/core/observation/primitives.py` — `ObservationSnapshot` e função
  `compute_observation_snapshot()` que calcula ratios, ciclos e qualidade.
- `ags/core/observation/classification.py` — `RegimeClassification` e
  `classify_from_snapshot()` que calcula distâncias para a taxonomia.
- `ags/synthetic/regimes.py` — definição da taxonomia sintética (11 regimes).
- `tools/c1_observe.py` — script de observação para executar análise em
  repositórios reais e exportar `c1_<project>_result.json`.
- `tools/verify_baseline.py` — verificação de baseline FASM (hashes, CIR).
- `tests/` — suíte de testes automatizados cobrindo gráficos, observação,
  classificação e invariantes científicos.

## Métricas e definições relevantes

- cross_domain_ratio, intra_domain_ratio, file_level_leakage, cycle_density:
  métricas estruturais [0,1] extraídas do grafo de arquivos.
- observation_quality: fração de imports que foram efetivamente representados
  como arestas; usa `total_imports_attempted` quando disponível.
- confidence/margin/distance: atributos da classificação que guiam os gates.

## Resultado prático (C1.0)

- Aplicado a 4 projetos reais (Requests, FastAPI, Celery, Airflow).
- Exporta JSON com `snapshot`, `classification` e `gates`.
- Identificou que o gate de qualidade falha em ambientes com muitos
  imports dinâmicos não resolvidos (Airflow), daí a introdução de
  `total_imports_attempted` para calibrar `observation_quality`.

## Como executar localmente

Ativar o ambiente virtual e rodar testes:

```bash
source .venv/bin/activate
python -m pytest -q
```

Observar um projeto (exemplo Requests):

```bash
source .venv/bin/activate
python tools/c1_observe.py Requests https://github.com/psf/requests.git
```

Verificar baseline FASM:

```bash
source .venv/bin/activate
python tools/verify_baseline.py
```

## Confiabilidade e limitações

- O sistema é baseado em análise estática; imports dinâmicos e parsing
  incremental podem causar sub-observação.
- A taxonomia sintética é descritiva (classificação) e sujeita a
  expansão se projetos reais exibirem zonas não cobertas.
- Tamanho do projeto é tratado como metadado (structural_distance é
  empregado para decisões primárias).

## Próximos passos (curto prazo)

- Refinar `GraphBuilder` para reduzir sub-observação (streaming, heurísticas
  de import dinâmico).  (Tarefa no plano)
- Reavaliar thresholds de gate com base nas métricas reais de C1.0.
- Produzir um relatório curto com recomendações para C2.0.

---

Documento gerado automaticamente para referência rápida do sistema.