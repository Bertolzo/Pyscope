# Architectural Calibration

**Layer**: 8
**Purpose**: Validate and tune the model

---

## Definition

Calibration validates that the model produces meaningful results.

ACP=90 means nothing without calibration.

---

## Stages

### C0: Verification

**Objective**: "Does the code implement the theory?"

**Method**: Synthetic fixtures with known ground truth.

**Fixtures**:

| Fixture | Expected ACP | Expected DCI | Expected Leakage |
|---------|--------------|--------------|------------------|
| synthetic_perfect | 100 | 100 | 0 |
| synthetic_coupled | 50 | 50 | 0.3 |
| synthetic_leaky | 80 | 70 | 0.8 |
| synthetic_collapsed | 20 | 20 | 0.9 |

**Success criteria**: Pyscope matches expected values.

---

### Pyscope — Observation

**Objective**: "Can the model distinguish different architectures?"

**Method**: Analyze real projects.

**Projects**:

| Project | Label |
|---------|-------|
| Django | mature |
| FastAPI | modern |
| Celery | complex |
| Airflow | large-scale |
| Requests | simple |

**Success criteria**: Model produces different scores for different architectures.

**Expected distribution**:
```
FastAPI   -> 91
Django    -> 84
Celery    -> 72
Airflow   -> 63
```

---

### C2: Correlation

**Objective**: "Does Pyscope correlate with accepted metrics?"

**Method**: Compare against literature.

**Metrics to compare**:
- CBO (Coupling Between Objects)
- LCOM (Lack of Cohesion in Methods)
- RFC (Response For a Class)

**Success criteria**: Positive correlation with accepted metrics.

---

## Threshold Tuning

After calibration, thresholds may need adjustment.

**Process**:
1. Collect results from C0, C1, C2
2. Analyze distribution
3. Adjust thresholds
4. Re-validate

---

## Weight Tuning

CRI weights may need adjustment.

**Process**:
1. Collect results from C0, C1, C2
2. Analyze contribution of each component
3. Adjust weights
4. Re-validate

---

## Rules

1. Calibration must happen before Governance deployment.
2. Thresholds must be traceable to calibration results.
3. Weights must be traceable to calibration results.
4. Calibration cannot be redefined by lower layers.
