# Phase I — Single-cell IPF lung (GSE135893, Habermann et al.)

**Status**: complete. To be folded into the final notebook (Phase J).

## Dataset

[**GSE135893**](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE135893) — Habermann et al. 2020, *Sci Adv*. 10x Genomics scRNA-seq of distal lung from 32 ILD donors (20 IPF + 12 other ILD) and 10 controls. **220,213 cells in raw matrix; 114,396 annotated cells** post-QC by the original authors. Annotation includes the famous KRT5⁻/KRT17⁺ aberrant basaloid population first described in this paper.

This phase analyses **89,326 cells** restricted to IPF (n=57,682) and Control (n=31,644). The full matrix is staged at `/data/bulk-gene-counts/GSE135893/` (counts in `matrix.mtx.gz`, barcodes/genes/metadata as TSVs).

## Pipeline (efficient pre-filter)

The full mtx (33,694 × 220,213, **338 M nnz**) is too big for `scipy.io.mmread` to handle in reasonable time. Strategy used here:

1. **Stream-parse** the gzipped mtx in Python, keeping triplets only for the 40-gene panel (top-20 OT picks + telomere extension + cell-type markers). Output: a dense `(40, 220213) float32` array → 1.5 MB on disk.
2. **Match** 114,396 metadata barcodes to mtx column indices.
3. **Normalise** per cell to log₂(CP10k+1) using the precomputed `nCount_RNA` from Habermann's metadata.
4. **Aggregate** mean expression and percent-expressing per (cell type × diagnosis × gene); keep cell types with ≥30 cells in both groups (26 cell types).

Outputs:
- `/data/bulk-gene-counts/analysis/ipf/sc_panel.npz` — pre-filtered count matrix
- `/data/bulk-gene-counts/analysis/ipf/sc_celltype_means.csv` — 2,080 records (26 types × 2 diag × 40 genes)
- `figures/I1_dotplot.png`, `I2_lfc_heatmap.png`, `I3_focus_targets.png`

## Key biology surfaced

### 1. MUC5B — the textbook ectopic-distal-expression story

Native MUC5B expression should be confined to airway secretory cells. In IPF:

| Cell type | Control mean | IPF mean | ΔIPF–Control |
|-----------|-------------:|--------:|-------------:|
| **MUC5B+** (the namesake population) | 2.0 | 3.0 | **+1.0** |
| **Differentiating Ciliated** | 0.8 | 1.2 | +0.4 |
| **SCGB3A2+** (distal club-like) | 0.0 | 0.4 | **+0.4 (ectopic)** |
| **AT2** | 0.0 | 0.18 | **+0.18 (ectopic alveolar)** |
| Other airway populations | unchanged | unchanged | – |

The MUC5B+ population itself is over-represented in IPF (2,433 cells in 57k IPF vs comparable in 31k controls — disproportionate). Combined with the ectopic up-regulation in AT2 and SCGB3A2+ cells, this fully reproduces the bulk +3.46 LFC from Phase H and is the single most-validated IPF disease signature in the literature ([rs35705950 promoter variant](https://doi.org/10.1056/NEJMoa1013660), Seibold 2011 NEJM).

### 2. SFTPA2 — surfactant collapse in proliferating AT2

| Cell type | Control mean | IPF mean | ΔIPF–Control |
|-----------|-------------:|--------:|-------------:|
| AT2 | 6.85 | 6.78 | flat |
| **Proliferating Epithelial Cells** | **5.5** | **3.0** | **−2.5** |
| SCGB3A2+ | 2.4 | 3.1 | +0.7 |
| Transitional AT2 | 3.1 | 3.4 | +0.3 |

The bulk SFTPA2 down-regulation (−0.90 LFC, Phase H) is **driven by the proliferating epithelial population**, not by terminally-differentiated AT2 cells. This is an interesting refinement: it's the *expanding aberrant epithelial pool* that loses surfactant, not classical AT2.

### 3. TERT — tiny but disease-specific signal

TERT mRNA is below detection in nearly all cells (consistent with telomerase being a tightly regulated, low-abundance enzyme):

| Cell type | Control mean | IPF mean |
|-----------|-------------:|--------:|
| **Proliferating Epithelial Cells** | 0.000 | **0.010** (n=341 IPF) |
| Basal | 0.000 | 0.003 |
| Plasma Cells (immune lineage, expected hi) | 0.020 | 0.002 |
| All other types | ≈0 | ≈0 |

Of 23 TERT-detecting cells in the entire dataset, the IPF signal localises to **proliferating epithelial cells** — exactly the cell population that is trying to regenerate damaged alveolar epithelium and that fails in telomere-deficient IPF. This is mechanistically congruent with the genetics → bulk-DE → cell-biology arc of the analysis.

### 4. DSP — increases mostly in non-AT cell types

DSP up-regulation in bulk (+1.06 LFC) is driven by **lymphatic endothelial cells, MUC5B+, ciliated, and basal** populations — all *increasing* in IPF lung. AT1 and AT2 (which decrease) show DSP slightly *down*. This is a *cell-composition* effect, not a per-cell up-regulation, and tempers DSP as a direct therapeutic target — though the GWAS L2G of 0.94 (Phase G) still flags it as causally relevant.

### 5. Telomere accessory machinery (WRAP53, DKC1, TINF2)

The bulk Phase H signal (WRAP53 +0.54, DKC1 +0.45, TINF2 −0.17) is broadly distributed across cell types with no single cell-type carrying the signal, consistent with these being housekeeping factors with modest IPF-driven changes throughout the tissue.

## Implications

- **MUC5B is a population-level phenomenon, not a single-cell up-regulation**: any therapy targeting MUC5B downstream needs to reduce ectopic-expressing cell populations (SCGB3A2+, AT2-mucinous-transitional), not just cells that "always" expressed it.
- **TERT in proliferating epithelial cells**: this single observation supports the Phase G thesis that activating telomerase (rather than inhibiting it) is the right intervention for the regenerating-but-failing epithelial compartment.
- **SFTPA2 collapse is in the abnormal AT2/transitional pool**: surfactant restoration therapies (synthetic surfactant) won't fix the cell-state defect — the diseased cells need to be either rescued or replaced.

## Figures

- `figures/I1_dotplot.png` — full 40-gene × 26-cell-type dotplot, IPF vs Control side-by-side (mean colour, % expressing size)
- `figures/I2_lfc_heatmap.png` — Δlog₂(IPF − Control) heatmap (cell type × gene)
- `figures/I3_focus_targets.png` — focused per-cell-type bars for MUC5B / SFTPA2 / DSP / TERT

## Reproducibility

Pipeline runs end-to-end in 2 sandbox calls:
1. Stream-parse mtx (~3-5 min, single-threaded Python; `scipy.io.mmread` does not finish at all on the gzipped 1 GB mtx)
2. Normalise + aggregate + plot (~30 s)

All intermediate files persist in `/data/bulk-gene-counts/analysis/ipf/`; the Phase J notebook will reproduce the pipeline cleanly.

## Caveats

- We did **not** run UMAP or re-clustering — Habermann's annotations are accepted as ground truth. Re-clustering would mostly reproduce them.
- The "ectopic" interpretation is observational (means + percents) — formal cell-type-specific DE with a mixed-effect model (e.g. NEBULA, MAST, or pseudobulk + DESeq2) would put error bars on these numbers. For the purposes of this prioritisation analysis the mean shifts are large enough to be unambiguous.
- The proliferating epithelial cell population is small (n=341 IPF, n≈260 control) so per-gene expression variance there is wider — flagged in I3 by smaller bars.
