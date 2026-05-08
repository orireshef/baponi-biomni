# IPF target prioritisation — full analysis plan

**Branch**: `analysis/ipf-target-prioritisation`
**Status**: Phases A–F complete (OT mining → composite ranking → PubMed corroboration). Phases G–J below extend the analysis with clinical landscape, transcriptomics, and a polished report.

## Where we already are

- 20 IPF targets ranked by a transparent composite (genetics 0.40, druggability 0.20, mouse phenotype 0.20, biology 0.10, literature 0.10, safety penalty −0.10). `known_drug` deliberately excluded as circular.
- Top picks: **TERT** (B/repurposing, 0.561), **SFTPA2** (C/novel, 0.511), **DSP** (C, 0.482), **MUC5B** (C, 0.444), **PARN** (C, 0.407), **MUC5AC** (B, 0.378), **SPDL1** (C, 0.371), **RTEL1** (C, 0.350).
- Two clean genetic axes: telomere maintenance (TERT/PARN/RTEL1) and surfactant biology (SFTPA2 + extended).
- Lead repurposing thesis: **imetelstat** (FDA-approved telomerase inhibitor, low-risk MDS) for telomere-defect IPF. Only 2 PubMed papers ever link imetelstat to lung fibrosis (one is a *telomerase activator* paper using imetelstat as a counter-control, [DOI](https://doi.org/10.1371/journal.pone.0058423); the other is a 2025 structural review, [DOI](https://doi.org/10.3389/fmolb.2025.1681988)) — virtually unexplored space.
- Storage scoped: `/data/bulk-gene-counts` is GCS-backed and writable (effectively unlimited); `/tmp` is 4 GB ephemeral. `/data/open-targets-public` is read-only.

## Phase G — Telomere / imetelstat clinical landscape (read-only OT + literature)

**Goal**: nail down whether imetelstat-for-IPF is a credible repurposing thesis and identify the trial / patient-stratification angle.

| Step | What | Source |
|------|------|--------|
| G1 | Pull GWAS credible-set fine-mapping for `TERT`, `PARN`, `RTEL1` in IPF (and proxies: any IPF/ILD-tagged study) | OT `credible_set` + `study` + `l2g_prediction` |
| G2 | Pull all existing imetelstat clinical activity (any indication) and OT's safety/warning signals | OT `clinical_target` + `clinical_indication` + `drug_warning` filtered to `IMETELSTAT` (CHEMBL2103817) |
| G3 | Telomere-pathway target list: pull OT data for the canonical telomeropathy genes (TERT, TERC, TINF2, RTEL1, PARN, NAF1, ZCCHC8, NHP2, NOP10, DKC1, WRAP53, ACD) — see if any others rank for IPF | OT `target` + `association_overall_indirect` |
| G4 | Patient-stratification literature: search PubMed for IPF + short telomere + clinical outcome — quantify the addressable subpopulation | PubMed MCP |
| G5 | Compose the imetelstat-for-IPF case (mechanism, evidence, stratification, watch-outs) | synthesis |

**Output**: section in the Jupyter notebook (Phase J) — text + 1-2 figures (forest plot of telomere-gene OT scores; imetelstat clinical-stage timeline).

## Phase H — Bulk RNA-seq IPF vs control

**Goal**: ground OT's prioritisation in *actual lung transcriptome changes* — do our top targets go up/down in IPF lung? This is the cheapest way to add a transcriptomic axis on top of the OT mining.

**Dataset**: **GSE150910** (Furusawa et al. 2020, *BMC Pulm Med*). 103 IPF + 103 control lung tissue, Illumina paired-end, raw counts available. Largest well-annotated public IPF RNA-seq, widely benchmarked. Counts matrix ~50–100 MB. Alternative if compute is tight: **GSE92592** (Nance 2014, n=20 IPF + 20 control) as a smaller classic.

| Step | What |
|------|------|
| H1 | Download GSE150910 raw counts + metadata to `/data/bulk-gene-counts/GSE150910/` (with the path-traversal hardening that's already in the repo) |
| H2 | Sanity-check: PCA on log-CPM, expect IPF/control separation on PC1 |
| H3 | Differential expression with **pyDESeq2** (Python-native, well-maintained); shrunken LFC; multiple-testing FDR |
| H4 | Per-target panel: log2FC + p_adj for each of our top 20, plus telomere-pathway extension from G3. Plot as a labelled volcano (highlighting top-20 + telomere genes) and a directed bar chart |
| H5 | Pathway enrichment: Hallmark fibrosis, GO telomere maintenance, GO surfactant, KEGG ECM-receptor — using `gseapy` or `fgsea` |
| H6 | **Composite v2**: add a transcriptomic axis (`abs(LFC) × (1 − padj)` or similar) to the existing composite. Re-rank. Compare strata before/after |

**Output**: notebook section with PCA, volcano, per-target bar chart, GSEA dotplot, updated ranking table.

## Phase I — Single-cell IPF lung (cell-type expression of top targets)

**Goal**: determine *which cell types* drive the bulk signal. AT2 cells? Aberrant basaloid? Fibroblasts? This is the single most informative add-on for biological interpretation.

**Dataset choice (small, sandbox-friendly)**: download a curated **CellxGene census IPF subset** (~20–40k cells, ~500 MB h5ad). Alternatives:
- **Habermann 2020** (`GSE135893`, ~115k cells, ~1.5 GB) — the canonical IPF lung atlas
- **Reyfman 2019** (`GSE122960`, ~70k cells)
- **Adams 2020** (`GSE136831`, ~300k cells, ~4 GB) — too big for the sandbox

| Step | What |
|------|------|
| I1 | Pull a CellxGene census slice: `disease in ('idiopathic pulmonary fibrosis','normal')` from a published IPF dataset, save as `/data/bulk-gene-counts/cellxgene_ipf_<slug>.h5ad` |
| I2 | QC with the **`single-cell-rna-qc`** skill (MAD-based filtering) — should be light, dataset is already curated |
| I3 | Cell-type expression matrix: dot plot of top-20 targets across cell types (AT1, AT2, basal, fibroblast, myofibroblast, aberrant basaloid, immune subsets, endothelial) for IPF and control side-by-side |
| I4 | Per-target focus: TERT, MUC5B, SFTPA2, DSP — which cell type expresses each, does expression shift in IPF? (e.g. MUC5B should ectopically appear in distal alveolar epithelium in IPF — well-known) |
| I5 | Optional: integration with `scvi-tools` if batch effects are present (probably not needed for a single-study slice) |

**Output**: notebook section with cell-type composition bar, target × cell-type dotplot, 2-3 UMAPs highlighting key targets.

## Phase J — Final report

**Format**: **Jupyter notebook** (`.ipynb`) committed to the repo, plus a **rendered Markdown summary** (`report.md`) that GitHub displays inline. Notebook is the executable artefact; markdown is the readable artefact.

| File | Role |
|------|------|
| `docs/analyses/ipf_target_prioritisation/PLAN.md` | This document. |
| `docs/analyses/ipf_target_prioritisation/notebook.ipynb` | Reproducible analysis (queries, DE, scRNA, figures). Built via baponi sandbox; figures embedded as base64. |
| `docs/analyses/ipf_target_prioritisation/report.md` | Executive narrative: top picks with rationale, key figures inline, links to notebook sections. |
| `docs/analyses/ipf_target_prioritisation/figures/*.png` | High-DPI figures referenced from report.md. |

**Notebook sections** (mirrors phases): A. Disease scoping → B. Top-20 → C. Per-source enrichment → D. Composite ranking → E. PubMed corroboration → F. Stratification → **G. Telomere/imetelstat case** → **H. Bulk RNA-seq integration** → **I. Single-cell cell-type biology** → J. Discussion / limitations / future.

**Report sections**: TL;DR (top 5 with one-line each) → Methodology → Top-20 ranked table → Per-target deep-dive (top 10) → Imetelstat case → Bulk RNA-seq highlights → Single-cell highlights → Discussion → Reproducibility.

## Open questions for the user

1. **Bulk dataset**: GSE150910 (n=206, modern) [recommended] or GSE92592 (n=40, smaller classic)?
2. **Single-cell**: a CellxGene curated slice (~20–40k cells, fastest) [recommended] or full Habermann GSE135893 (~115k cells, ~1.5 GB)?

Decide these and I execute G → H → I → J straight through.

## Risks / watch-outs

- **Sandbox storage**: 4 GB tmpfs cap on raw bytes inside the container. Habermann full (~1.5 GB) fits but leaves little headroom; CellxGene slice is safer.
- **pyDESeq2 install size**: ~200 MB of deps; first install will be slow but gets cached in the thread.
- **Cross-study integration**: bulk + single-cell are different studies — claims should be that the *direction* of change agrees, not that absolute magnitudes match.
- **Imetelstat for IPF**: there is no imetelstat IPF trial (Geron's pulmonary programme was discontinued years ago, per the 2013 PLoS One paper background). The pitch is "should be reconsidered given new genetic + transcriptomic + cellular evidence" — *not* "this is in trials". Be precise in the report.
- **Composite weights**: the 0.40/0.20/0.20/0.10/0.10 split is defensible but arbitrary. The report must show component contributions and a sensitivity plot (composite ranks under ±0.10 perturbation of each weight).

## Verification plan

- G: imetelstat reachable via OT `clinical_target.drugId='CHEMBL2103817'` returning ≥1 row. TERT credible_set query returns ≥1 fine-mapped variant (rs2736100 expected).
- H: PCA separates IPF vs control; nintedanib targets (FGFR/PDGFR/KDR) significantly DE; MUC5B significantly upregulated in IPF lung (well-established).
- I: MUC5B detected predominantly in airway epithelium (bronchial cells), with ectopic expression in distal/aberrant cell types in IPF — well-known disease hallmark; if absent, dataset is wrong.
- J: notebook renders end-to-end; report.md commits with figures resolving on GitHub.
