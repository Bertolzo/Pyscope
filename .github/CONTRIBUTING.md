# Contribuindo para AGS

Obrigado por contribuir com o AGS. Este projeto combina engenharia, pesquisa e governança de arquitetura. A colaboração deve ser prática, transparente e alinhada com o escopo do sistema.

## Como começar

1. Abra uma issue descrevendo seu caso de uso.
2. Se for funcional, use `feature/*`.
3. Se for pesquisa ou experimento, use `exp/*`.
4. Se alterar limites, use `doc/*`.
5. Se for correção urgente, use `hotfix/*`.

## Processo de contribution

### Issues
- Use `bug_report` para comportamentos fora do esperado.
- Use `feature_request` para novas métricas, flows ou integrações.
- O issue deve incluir:
  - contexto do projeto real
  - objetivo desejado
  - métrica de sucesso ou resultado esperado

### Pull Requests
- Relacione a PR ao issue correspondente.
- Preencha o template de PR.
- Inclua validação clara:
  - `python -m pytest`
  - `python tools/verify_baseline.py`
- Atualize documentação quando o escopo ou métricas mudarem.

## Qualquer mudança de escopo precisa ser justificada

Mudanças em `docs/LIMITATIONS.md`, na taxonomia de regimes ou no pipeline de observação exigem:

- justificativa clara no issue
- evidência de impacto em projeto real
- atualização de documentação e workflow

## Branching e nomenclatura

- `main` — pronto para early adopters e adoção controlada.
- `develop` — integração de recursos aprovados.
- `feature/<nome>` — novas capacidades e refinamentos.
- `exp/<nome>` — protótipos e experimentos.
- `doc/<nome>` — alterações de escopo, limitação ou auditoria.
- `hotfix/<nome>` — correções imediatas.

## Requisitos técnicos

- Python 3.12
- Dependências definidas em `pyproject.toml`

### Testes

Execute:

```bash
python -m pytest
python tools/verify_baseline.py
```

### Artefatos e validação

Para mudanças que afetam o observador, execute:

```bash
python -m tools.c1_observe "requests" "https://github.com/psf/requests.git" c1_requests_remote
```

Verifique se o artifact resultante contém:

- `c1_<project>_result.json`
- `/tmp/opencode/<workdir_name>`

## Código de conduta

Todos os colaboradores devem seguir o `CODE_OF_CONDUCT.md`.
