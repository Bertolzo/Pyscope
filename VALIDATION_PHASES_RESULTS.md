# Validation Phases Results

## Context
- Target analyzed: `AGS` repository itself
- Workspace path: `/home/vector/Documentos/testabilidade`
- Environment: Python virtualenv `.venv`
- Validation helper: `tools/ags_validation_phases.py`

## Phase 1 — Cobertura de imports

### Executado
- Raw Python import statements in repo (excluindo `.venv`/`.git`): `708`
- Total AST import entries extracted: `1865`
- Project-internal AST imports (top-level modules `ags`, `tests`, `tools`, `mutants`): `350`
- AGS graph edges total: `285`
- AGS graph distinct internal targets: `64`
- Import comparison unresolved internal imports: `0`

### Conclusão
- A Fase 1 é viável.
- A métrica de comparação precisa ser adaptada: o AGS representa dependências como arestas de grafo/arquivo, enquanto o grep conta linhas de import.
- O comparador interno foi ajustado para normalizar caminhos absolutos no grafo AGS, e após a correção todos os imports internos detectados pelo AST foram cobertos pelo grafo.

### Comandos usados
```bash
cd /home/vector/Documentos/testabilidade
source .venv/bin/activate
python tools/ags_validation_phases.py analyze . --db tools/ags_validation.db --report tools/ags_validation_report.json --graph tools/ags_validation_graph.json
python tools/ags_validation_phases.py extract-imports . --output tools/ags_ast_imports.json
python tools/ags_validation_phases.py compare-imports . --ags-graph tools/ags_validation_graph.json --ast-imports tools/ags_ast_imports.json --output tools/ags_import_comparison.json
```

## Phase 2 — Inspeção visual do grafo

### O que foi tentado
- Primary: `pydeps` (tentativa de gerar `tools/ags_graph_pydeps.png`)
- Fallback 1: `pyreverse` via `pylint` (gerou `tools/classes_AGS.dot` e `tools/packages_AGS.dot`)

### Resultado
- `pydeps` não pôde gerar a imagem porque o sistema não possui o executável `dot` do Graphviz.
- `pyreverse` gerou com sucesso os arquivos DOT para visualização de classes e pacotes.
- Também foram gerados dois DOTs de comparação interna:
  - `tools/ags_graph_internal.dot` — grafo interno do AGS
  - `tools/ags_graph_ast.dot` — grafo de imports AST extraídos

### Pair Ask
- Q: O que foi validado nesta fase?
  - A: Se o grafo externo de dependências é coerente com o grafo interno do AGS.
- Q: Qual ferramenta foi usada como primária?
  - A: `pydeps`, mas ela foi bloqueada por dependência de sistema (`dot`).
- Q: Qual foi o fallback bem-sucedido?
  - A: `pyreverse` gerou os arquivos DOT necessários.
- Q: O que podemos comparar hoje?
  - A: estruturas de grafo e clusters nas representações DOT, mais do que a renderização final.

### Artefatos gerados
- `tools/classes_AGS.dot` (39 arestas)
- `tools/packages_AGS.dot` (96 arestas)
- `tools/ags_graph_internal.dot` (285 arestas)
- `tools/ags_graph_ast.dot` (1791 arestas)
- `tools/pyreverse3.log`

### Observações de fase 2
- `pydeps` falhou por falta do executável `dot` do Graphviz no sistema.
- `pyreverse` funcionou como fallback e produziu os artefatos DOT necessários.
- Os DOTs internos suportam comparação de clusters mesmo sem renderização em PNG.

## Observações de implementação
- Corrigido `tools/ags_validation_phases.py` para normalizar corretamente caminhos absolutos ao comparar imports.
- O arquivo `tools/ags_validation_graph.json` está disponível para gerar uma visualização DOT/PNG.

## Próximo passo recomendado
- Executar Fase 2 com a geração de grafo visual (`pydeps`, `pyreverse` ou `.dot` a partir do JSON).
- Validar a correspondência visual entre o grafo AGS e o grafo externo.
- Opcional: usar `requests` como alvo secundário se desejar comparar com um projeto externo.
