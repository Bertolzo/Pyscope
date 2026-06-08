# CODEX_CONTEXT

## Objetivo

Este documento documenta o contexto do experimento Pyscope 1.0, alinhando o propósito do projeto, a arquitetura e os resultados iniciais. O foco é esclarecer como Pyscope, FASM e ADO se relacionam, o que foi construído, quais descobertas foram feitas e quais decisões de design foram adotadas.

## Arquitetura

### Pyscope
`Pyscope` é a arquitetura principal do projeto: uma plataforma de observação arquitetural que modela sistemas por meio de grafos, estados, acoplamento e observação. Pyscope é o núcleo de análise e pretende ser uma infraestrutura genérica para medir propriedades de código e processos de mudança.

### FASM
FASM refere-se à Framework de Avaliação de Sistemas de Medição. Ela define a metodologia, métricas e invariantes de avaliação, incluindo o ciclo de calibração, análise de descobertas e validação científica das medições. FASM atua abaixo de Pyscope como disciplina de análise dos dados coletados.

### ADO
ADO é o domínio de Aplicação, Dados e Observação. É onde os dados reais entram no sistema: observações de software, mudanças, snapshots e classificações. ADO é o fluxo operacional que alimenta Pyscope e aplica FASM aos casos reais.

> Nota: Pyscope, FASM e ADO não são intercambiáveis. Pyscope é a arquitetura analítica, FASM é a metodologia de avaliação e ADO é o pipeline de dados/observação.

## Bridge Layer

A bridge layer conecta a observação bruta com a análise de regimes e fornece uma interface estável para as camadas superiores.

- `ObservationSnapshot`
  - representa um estado congelado do sistema observado
  - captura métricas, topologia e atributos relevantes para análise
  - serve como base para comparação entre estados e para inferência de mudanças

- `RegimeClassification`
  - traduz `ObservationSnapshot` em regimes comportamentais ou classes de mudança
  - aplica lógica de classificação para determinar regimes de estabilidade, perturbação ou risco
  - permite que análises de alto nível usem um formato unificado de regime em vez de dados brutos

A combinação `ObservationSnapshot + RegimeClassification` garante que a camada de análise permaneça desacoplada das fontes de dados e dos formatos de entrada específicos.

## Resultados Pyscope 1.0

O experimento Pyscope 1.0 foi aplicado a quatro projetos representativos, validando o pipeline de observação e a capacidade de gate check.

- Quatro projetos analisados
- Gate check implementado para validar a consistência dos snapshots e as regras de passagem
- Descobertas principais:
  - métricas de acoplamento e fluxo evidenciam regimes distintos entre projetos
  - self-loops e dependências cíclicas impactam os resultados de classificação
  - a confiança nas inferências varia com a qualidade dos dados de observação
  - o modelo de regime expõe padrões de mudança não triviais que indicam pontos de intervenção

Esses resultados confirmam que a arquitetura consegue capturar sinais relevantes e fornece uma base inicial para Pyscope 2.0.

## Decisões de Design

### Fórmulas de ratio

- As razões (`ratio`) foram adotadas como fórmulas para normalizar métricas entre projetos e estados.
- Ratio permite comparar propriedades relativas em vez de valores absolutos, reduzindo viés de escala entre módulos.
- A escolha de fórmulas seguiu a premissa de manter os indicadores interpretabili e aplicáveis a diferentes estruturas de código.

### Self-loops

- Self-loops são tratados explicitamente na análise do grafo.
- Eles não são ignorados: são um sinal relevante de acoplamento intra-módulo e podem afetar regimes de estabilidade.
- O design preserva informação de self-loop para evitar perda de dados em métricas de coesão e dependência.

### Confiança

- A confiança (`confidence`) é um atributo first-class nas inferências de regime.
- Ela quantifica a certeza das classificações com base nos dados observados e nas condições do gate check.
- A confiança orienta decisões posteriores, permitindo que consumidores do modelo saibam quando uma inferência deve ser tratada como forte ou provisória.

## Convenções

- Não usar comentários no código como fonte de verdade para análise de regime.
- O processo de validação segue o `Scientific Change Protocol`:
  - observação precisa e estruturada
  - comparação entre estados
  - inferência com métricas verificáveis
  - validação de resultados através de gates de consistência

Essas convenções garantem que o processo se mantenha científico e reprodutível.

## Próximos Passos

- Avançar para C2.0 com novos casos de uso e maior cobertura de projetos
- Expandir a taxonomia de regimes e classificações para suportar mais cenários de mudança
- Integrar a plataforma com Django para oferecer uma camada de aplicação web e visualização
- Refinar o gate check e as métricas de confiança com base nos resultados de C1.0

---

`CODEX_CONTEXT.md` salvo e pronto para suportar o roadmap do projeto.