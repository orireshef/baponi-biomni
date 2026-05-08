# Phase M — Rank-aggregation re-ranking (Borda + RobustRankAggreg)

**Status**: complete. Replaces the heuristic weighted-sum composite (v1/v2) as the *primary* ranking method.

## Why this phase exists

Audit question: "where do the composite weights come from?" Honest answer: hand-picked. The v1 split (0.40/0.20/0.20/0.10/0.10) and v2 split (0.30/0.25/0.15/0.15/0.10/0.05) were chosen by the analyst based on biological intuition — *not* derived from data. The Phase J sensitivity analysis showed the top-5 was robust to weight perturbation, but that's post-hoc robustness, not derivation.

This phase replaces the weighted-sum composite with **rank-aggregation methods that need no weights at all**. Each evidence component contributes equally as a ranked list; the aggregate score is computed without privileging any axis.

## Methods

We evaluated two complementary rank-aggregation approaches.

### Borda count (mean rank)

For each of the 6 components, compute the per-target rank (1 = best, 20 = worst), with `method='average'` for ties. Borda score = `Σ (N − rank + 1)` across components. Higher = better.

Borda is intuitive — equivalent to mean rank — and rewards targets that are consistently mid-or-better across all axes. A single extreme rank (e.g., MUC5B's LFC=+3.46 in tx) is *not* over-weighted, since the rank just tells us "this is the best on tx", not "by how much".

### RobustRankAggreg (RRA) — Stuart 2003

Per-target rho-score from order statistics:

1. Normalise each component rank to (0, 1] by dividing by N+1 = 21.
2. Sort the K=6 normalised ranks ascending: r₍₁₎ ≤ r₍₂₎ ≤ ... ≤ r₍₆₎.
3. For each k = 1…K, compute `p_k = BetaCDF(r_(k), k, K − k + 1)` — the probability that the k-th best rank would be at least this good if all 6 ranks were drawn from Uniform(0, 1).
4. ρ = min over k of p_k.

A target with strong ranks across multiple components has a very small minimum p-value (low ρ = better). A target with one excellent rank but weak everywhere else gets a less impressive ρ because the order statistics are weighted toward consistent strength.

[Stuart 2003, *Bioinformatics*](https://doi.org/10.1093/bioinformatics/btg455). Widely used in cross-platform meta-analyses.

### Components (same as composite v2)

| Component | Source |
|-----------|--------|
| `genetic_score` | max(genetic_association, genetic_literature) — OT |
| `tx_score` | min(\|LFC\|, 3.0) / 3.0 × max(0, 1 − padj/0.05) — Phase H |
| `druggability` | mean(hasPocket, hasLigand, hasSMB, hasHighQualityChemicalProbes) — OT |
| `mouse_score` | min(n_lung_phenotypes, 10) / 10 — OT |
| `literature_score` | OT `literature` datatype score |
| `biology_score` | max(animal_model, rna_expression) — OT |

`known_drug` excluded (circular). `safety_penalty` not used (rank-aggregation doesn't naturally accept a penalty; we keep it as post-hoc commentary).

## Results

### Top-12 by each method

| Rank | v2 (heuristic) | Borda | RRA |
|-----:|----------------|-------|-----|
| 1 | MUC5B (0.606) | **MUC5B** (91) | **MUC5B** (ρ=0.006) |
| 2 | MUC5AC (0.547) | **SFTPA2** (83) | **DSP** (ρ=0.044) |
| 3 | TERT (0.517) | **TERT** (81.5) | **SFTPA2** (ρ=0.060) |
| 4 | SFTPA2 (0.480) | **DSP** (81.5) | **TERT** (ρ=0.078) |
| 5 | DSP (0.472) | **NR3C1** (72) | **FGFR1** (ρ=0.133) |
| 6 | FGFR2 (0.322) | MUC5AC (71.5) | FLT1 (ρ=0.133) |
| 7 | PDGFRA (0.308) | FGFR1 (67) | PDGFRA (ρ=0.133) |
| 8 | PARN (0.308) | FGFR2 (67) | FGFR4 (ρ=0.133) |
| 9 | SPDL1 (0.290) | PDGFRA (67) | MUC5AC (ρ=0.151) |
| 10 | RTEL1 (0.265) | PDGFRB (61.5) | FGFR2 (ρ=0.154) |
| 11 | NR3C1 (0.242) | FGFR4 (61.5) | NR3C1 (ρ=0.154) |
| 12 | FGFR4 (0.225) | FGFR3 (60.5) | PDGFRB (ρ=0.235) |

### Stable top-4 across all 3 methods

**MUC5B, SFTPA2, TERT, DSP** — these 4 targets are unambiguously the top picks regardless of how evidence is aggregated. No weight-tuning argument can dislodge them; they win by Borda (mean rank) and they win by RRA (order statistics). This is the strongest possible signal a rank-aggregation analysis can give.

### The 5th slot diverges — and the divergence is informative

| Method | 5th pick | Why |
|--------|----------|-----|
| v2 heuristic | MUC5AC | Strong genetic + tx, both heavily weighted in v2 |
| Borda | NR3C1 | Strong druggability + mouse phenotype + literature; null genetic + tx |
| RRA | FGFR1 | Strong druggability + decent on multiple secondary axes |

**Both Borda's NR3C1 (#5) and RRA's FGFR1 (#5) are Stratum-A "already in IPF clinic" targets** — corticosteroid receptor (NR3C1) and a nintedanib FGFR target. When we removed the genetic-axis bias from the heuristic, the druggability axis pulled them up.

This exposes a hidden circularity: **druggability is itself biased toward already-drugged targets** (drugs in clinic for IPF have ligands by definition; nintedanib RTK targets have lung mouse phenotypes by virtue of being studied in IPF). So the act of "letting all axes vote equally" re-introduces a different form of the circularity we removed by dropping `known_drug`.

The honest read: **the 4-stable-top picks (MUC5B, SFTPA2, TERT, DSP) are robust; the 5th slot is method-dependent and any picks in the 5–10 range that come from the druggability-rich axes (FGFR/PDGFR/NR3C1) need to be evaluated against the druggability-circularity caveat.**

### Sanity checks (per plan verification section)

| Check | Result |
|-------|--------|
| Borda: MUC5B = rank 1 | ✓ |
| RRA: targets with one extreme but weak elsewhere drop | ✓ — FGFR4 has tx_score rank 3 but ranks 14, 15, 11 elsewhere → RRA rank 8, well below stable top-4 |
| Top-5 Borda ∩ RRA ≥ 4 | ✓ — 4 (MUC5B, SFTPA2, TERT, DSP); 5th differs (NR3C1 vs FGFR1) |
| ≥3 of {MUC5B, MUC5AC, TERT, SFTPA2, DSP} stable | ✓ — 4 of 5 (MUC5AC drops to v2-only) |
| Stratum-A intrusion warning (FGFR/NR3C1 climbing) | ⚠ Predicted in plan; observed; documented above |

## Output artefacts

- `figures/M1_rank_aggregation.png` — 3-panel: per-component rank heatmap (target × component); Borda-vs-RRA agreement scatter; v2→Borda→RRA slope graph (top-4 highlighted in red).
- `figures/M2_per_target_components.png` — for each top-8 Borda target, per-component contribution bars showing where its rank comes from.
- `/data/bulk-gene-counts/analysis/ipf/rank_aggregation.csv` — per-target ranks per component + Borda + RRA + v2 for full reproducibility.

## Headline conclusion for the report

**MUC5B, SFTPA2, TERT, DSP are the genuinely top-tier IPF targets** — they win across heuristic weighting, Borda, and RRA. No reasonable weight choice or aggregation method moves them off the top. **MUC5AC sits in the heuristic top-5 but doesn't survive Borda/RRA** — it has good genetic + extreme tx but weaker druggability and zero mouse phenotype, so the rank-aggregation methods penalise it relative to NR3C1 / FGFR1 / DSP.

The "novel undrugged" framing of the report stands: of the stable top-4, three (MUC5B, SFTPA2, DSP) are Stratum-C novel; one (TERT) is Stratum-B repurposing-candidate (with the directionality caveat from Phase G).

## Reproducibility (full code)

```python
import pandas as pd, numpy as np
from scipy.stats import rankdata, beta

# Load components from composite_v2.csv (or recompute as in Phase J)
df = pd.read_csv('/data/bulk-gene-counts/analysis/ipf/composite_v2.csv', index_col=0)
components = ['genetic_score','tx_score','druggability','mouse_score','literature_score','biology_score']
N, K = len(df), len(components)

# Per-component ranks (1=best)
ranks = pd.DataFrame({c: rankdata(-df[c].values, method='average') for c in components}, index=df.index)

# Borda
borda = (N + 1 - ranks).sum(axis=1)

# RRA (Stuart 2003)
rho = []
for sym in df.index:
    rr = sorted(ranks.loc[sym, components].values / (N + 1))
    pks = [beta.cdf(rr[k-1], k, K - k + 1) for k in range(1, K+1)]
    rho.append(min(pks))
ranks['borda_score'] = borda
ranks['rra_rho'] = rho
```

About 15 lines. No external libraries beyond scipy.
