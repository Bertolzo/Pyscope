# Pyscope Research Plan

## Objetivo

Estabelecer uma pesquisa pragmática para validar a aplicação de `ObservationSnapshot` e `RegimeClassification` em projetos reais, conectando o framework AGS/FASM/ADO a evidências de campo.

## Pergunta central

Como usar observação de snapshots e classificação de regimes para apoiar governança arquitetural realista, mantendo um protocolo científico de mudança?

## Etapas de pesquisa

1. Revisar literatura relevante
   - Governança arquitetural e architecture conformance/checking
   - Métricas de acoplamento, coesão e dependências de grafo
   - Evolução de software, change impact analysis e regime taxonomy
   - Validação científica de métricas e observações

2. Extrair técnicas aplicáveis
   - Normalização por ratios em vez de valores absolutos
   - Tratamento explícito de self-loops e ciclos
   - Confiança como atributo derivado da qualidade da observação e da distância estrutural

3. Mapear para o produto
   - `ObservationSnapshot`: métricas primárias + qualidade da observação
   - `RegimeClassification`: regime mais próximo, segunda distância, margem, confiança
   - Gate check: qualidade, margem e distância estrutural
   - Scientific Change Protocol: observação, comparação, inferência, validação

4. Executar estudo de caso Pyscope 1.0
   - Analisar os quatro projetos reais já observados (Requests, FastAPI, Celery, Airflow)
   - Medir qualidade de observação, distância estrutural e regime transferido
   - Identificar falhas de coverage e limites do espaço sintético

5. Refinar o sistema
   - Melhorar a captura de imports tentados e a estimação de edges desconhecidos
   - Revisar thresholds para real-world projects
   - Expandir a taxonomia de regimes conforme descobertas empíricas

6. Documentar e planejar C2.0
   - Criar reporte com resultados, limitações e recomendações
   - Planejar expansão de regimes e integração de visualização (Django)

## Ações concluídas aqui

- Corrigido o cálculo de qualidade da observação para usar `total_imports_attempted` quando disponível.
- Estendido `ObservationSnapshot` para armazenar `total_imports_attempted`.
- Adicionado suporte no `GraphBuilder` para contar todos os imports tentados.
- Atualizado `tools/c1_observe.py` para passar o total de imports para a snapshot.
- Incluído relatório de impressões no `c1_observe.py` com o total de imports avaliados.
- Criado cobertura de testes para o novo comportamento de qualidade e contagem de imports.

## Como validar

1. Executar `python -m pytest -q tests/test_observation.py`
2. Executar `python tools/c1_observe.py <name> <repo_url>` para um projeto real
3. Confirmar que `total_imports_attempted` aparece na snapshot e que a quality reflete import attempts

## Próximos passos

- Revisar os resultados de C1.0 com o novo cálculo de qualidade e ajustar o gate check
- Expandir a taxonomia sintética para incluir zonas de regimes observadas em projetos reais
- Planejar uma prova de conceito de visualização com Django para resumir regimes e confiança
- Adicionar testes de regressão para o comportamento de `total_imports_attempted`
