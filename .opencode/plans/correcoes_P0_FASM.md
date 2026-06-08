# Plano de Correções P0 — Contaminação FASM-AGS

**Data**: 2026-06-04
**Status**: Pendente de aprovação
**Baseline Impact**: PATCH + MINOR + MAJOR

---

## Problema

O protocolo ADO v1.0 estabelece:
- **FASM** descreve: Ontologia, Teoria, Fenômenos, Vetor de Estado, Métricas, Dinâmica, Falsificabilidade
- **FASM NÃO** descreve: Frameworks, APIs, Bancos, Interfaces, Deploy
- **AGS NÃO** pode criar conceitos. Todo conceito deve existir primeiro em FASM.

Atualmente, 5 documentos FASM contêm código Python, caminhos de arquivo AGS, ou nomes de tecnologias de implementação.

---

## Correções

### P0.1: STATE_VECTOR.md — Remover código Python (PATCH)

**O que**: Substituir `def to_embedding(self)` (Python) por notação matemática. Substituir `assert` statements por tabela de invariantes. Substituir "All AGS metrics" por "All FASM metrics".

**Arquivo**: `docs/STATE_VECTOR.md` (hasheado no baseline)
**Impacto**: PATCH (formatação)

### P0.2: INVARIANTS.md — Remover referências a Pydantic + caminho de teste (PATCH)

**O que**: Substituir "Pydantic validation" por "Model validation". Substituir "Test suite: tests/test_math_invariants.py" por "Automated verification".

**Arquivo**: `docs/INVARIANTS.md` (hasheado no baseline)
**Impacto**: PATCH (formatação)

### P0.3: MEMORY.md — Remover tecnologias + código Python (PATCH)

**O que**: Remover lista "sqlite-vec, FAISS, pgvector", substituir por "vector store". Remover bloco Python `state_vector.to_embedding()`.

**Arquivo**: `docs/MEMORY.md` (hasheado no baseline)
**Impacto**: PATCH (formatação)

### P0.4: MEASUREMENT_THEORY.md — Remover referências AGS + fix CycleDensity (fora do baseline)

**O que**:
- Remover `ags/core/structural/analyzer.py:_calculate_cri()` e `_calculate_entropy()`
- Fix typo "PHENOMENTS.md" → "PHENOMENA.md"
- Fix `S(t).leakage` → `S(t).boundary_leakage` na tabela resumo
- Marcar CycleDensity como "synthetic only" (não está no S(t) canônico)

**Arquivo**: `docs/MEASUREMENT_THEORY.md` (NÃO hasheado no baseline)
**Impacto**: Nenhum (fora do baseline)

### P0.5: CIR_INVARIANTS.md — Remover referências AGS (fora do baseline)

**O que**: Remover caminhos `ags/synthetic/regimes.py`, `perturbation.py`, `coverage_audit.py`, `tests/test_synthetic_c00.py`. Substituir por referência conceitual.

**Arquivo**: `docs/CIR_INVARIANTS.md` (NÃO hasheado no baseline)
**Impacto**: Nenhum (fora do baseline)

### P0.6: PHENOMENA.md — Adicionar fenômenos faltantes (MAJOR)

**O que**: Adicionar dois fenômenos que METRICS.md referencia mas não existem em PHENOMENA.md:
1. **Coupling Intensity** — para Dependency Density
2. **Rate of Change** — para Half-Life, Entropy Velocity

**Arquivo**: `docs/PHENOMENA.md` (hasheado no baseline)
**Impacto**: MAJOR (fenômeno novo)

### P0.7: METRICS.md — Corrigir mapeamentos de fenômeno (MINOR)

**O que**:
- Entropy Velocity: "Rate of Entropy Change" → "Architectural Entropy" (sub-dimensão)
- Entropy Acceleration: "Acceleration of Entropy" → "Architectural Entropy" (sub-dimensão)

**Arquivo**: `docs/METRICS.md` (hasheado no baseline)
**Impacto**: MINOR (métrica reclassificada)

### P0.8: SCIENTIFIC_VALIDATION_PROTOCOL.md — Adicionar Axioma 8 (fora do baseline)

**O que**: Adicionar "8. Architecture has epistemic limits" à lista de axiomas em Q2.

**Arquivo**: `docs/SCIENTIFIC_VALIDATION_PROTOCOL.md` (NÃO hasheado no baseline)
**Impacto**: Nenhum (fora do baseline)

---

## Baseline Impact

| Arquivo | Baseline | Bump | Razão |
|---------|----------|------|-------|
| STATE_VECTOR.md | Section A | PATCH | Formatação (Python → notação) |
| INVARIANTS.md | Section A | PATCH | Formatação (Pydantic → genérico) |
| MEMORY.md | Section A | PATCH | Formatação (tecnologias → conceito) |
| PHENOMENA.md | Section A | **MAJOR** | Novo fenômeno |
| METRICS.md | Section A | **MINOR** | Reclassificação de métrica |
| MEASUREMENT_THEORY.md | — | Nenhum | Fora do baseline |
| CIR_INVARIANTS.md | — | Nenhum | Fora do baseline |
| SCIENTIFIC_VALIDATION_PROTOCOL.md | — | Nenhum | Fora do baseline |

**Versão resultante**: v1.1.0 (MINOR + MAJOR → MAJOR v2.0.0, ou aggregate v2.0.0?)

> Decisão pendente: bump único ou composto? Sugiro MAJOR v2.0.0 porque há adição de fenômeno.

---

## Pós-Correção

1. Executar `python tools/verify_baseline.py --update` para recalcular hashes
2. Executar `python tests/test_baseline.py` para verificar integridade
3. Atualizar `AUDIT.md` com as correções realizadas
4. Confirmar que `python -m pytest tests/` continua passando (216+ testes)

---

## E se não fizermos?

As violações atuais são aceitáveis para operação, mas:
- Comprometem a rastreabilidade FASM (METRICS.md referencia fenômenos que não existem)
- Criam ambiguidade: um documento é FASM puro ou inclui implementação?
- Impedem que o baseline seja usado como contrato formal entre FASM e AGS
