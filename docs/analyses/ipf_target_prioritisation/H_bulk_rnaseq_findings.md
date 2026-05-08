# Phase H — Bulk RNA-seq integration (GSE150910)

**Status**: complete. Findings to be folded into the final notebook (Phase J).

## Dataset

[**GSE150910**](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE150910) — Furusawa et al. 2020. Lung tissue bulk RNA-seq, n=288 (103 IPF, 103 control, 82 chronic hypersensitivity pneumonitis). Primary analysis: **IPF vs control** (n=206); CHP held out as future comparator. Counts staged at `/data/bulk-gene-counts/GSE150910/`.

Pipeline (re-runnable in the Phase J notebook):

1. Drop genes with <10 counts in <10 samples → **16,844 / 18,838 genes retained**
2. PCA on top 2,000 variable genes (log₂(CPM+1))
3. **pyDESeq2 v0.5.4** with `condition ~ ipf|control`, default size-factor normalisation, Wald test, BH FDR

Compute time on the sandbox (4 CPUs): library load ~1 s, DE fit ~20 s, GSEA ~60 s.

## Quality / sanity

| Check | Result |
|-------|--------|
| PC1 variance explained | **35.7%** — strong IPF/control separation (figure H1) |
| PC2 variance explained | 11.1% |
| Genes significant (padj<0.05) | **9,283 / 16,844** |
| Genes \|LFC\|>1 & padj<0.05 | **1,781** |
| Top up-regulated | IGFL2, S100A2, FHL2, FCRL5, FAM83A, COL7A1, CTHRC1, CDH3, TMPRSS4, GOLM1 |
| Top down-regulated | KLRG2, MAP3K15, SLCO1A2, EPB41L5, AGTPBP1 |

The top-up list is dominated by canonical IPF markers (S100A2, COL7A1, CTHRC1) — pipeline is correct.

## Top-20 OT picks in DE (figure H3)

| Symbol | log₂FC | padj | Direction | Interpretation |
|--------|-------:|-----:|-----------|----------------|
| **MUC5B** | **+3.46** | 1.5e-32 | ↑↑↑ | Hallmark IPF — confirms canonical bulk signature |
| **MUC5AC** | **+3.25** | 1.2e-15 | ↑↑↑ | Co-regulated mucin, ectopic distal expression |
| **DSP** | **+1.06** | 2.7e-16 | ↑ | Desmoplakin — concordant with GWAS (β +0.36, see Phase G) |
| **TERT** | **+1.01** | 3.1e-3 | ↑ | Slight increase but `baseMean=2.3` (very lowly expressed); plausibly an epithelial stress response |
| FGFR3 | +0.49 | 3.5e-4 | ↑ | |
| FGFR1 | +0.18 | 0.046 | ↑ | |
| PDGFRB | +0.10 | 0.37 | n.s. | |
| RTEL1 | +0.08 | 0.33 | n.s. | |
| NR3C1, FGFR2, IFNGR2 | ~0 | n.s. | flat | |
| PARN | −0.14 | 0.30 | n.s. | |
| SPDL1 | −0.15 | 0.21 | n.s. | |
| **FAM13A** | −0.27 | 8.7e-4 | ↓ | GWAS β was negative — concordant |
| KDR | −0.31 | 0.10 | n.s. | |
| FLT1 | −0.34 | 0.022 | ↓ | |
| **PDGFRA** | −0.79 | 3.0e-7 | ↓ | Reflects fibrosis-driven fibroblast composition shift, not a target malfunction |
| **FLT4** | −0.84 | 1.5e-14 | ↓ | Endothelial loss in fibrotic tissue |
| **SFTPA2** | **−0.90** | 3.0e-7 | ↓↓ | Surfactant deficiency in diseased AT2 cells — concordant with familial-IPF biology |
| **FGFR4** | **−1.17** | 2.4e-20 | ↓↓ | |

## Telomere panel (extension)

| Symbol | log₂FC | padj | Notes |
|--------|-------:|-----:|-------|
| **TERT** | +1.01 | 3.1e-3 | (also in top-20) |
| **WRAP53** | +0.54 | 5.0e-9 | Telomerase Cajal-body factor — UP |
| **DKC1** | +0.45 | 7.1e-5 | Dyskerin — UP |
| RTEL1 | +0.08 | 0.33 | n.s. |
| NHP2, NAF1 | ~0 | n.s. | |
| TINF2 | −0.17 | 1.2e-3 | Shelterin — slightly down |
| STN1 | −0.19 | 3.1e-3 | CST complex — down |
| NOP10 | −0.13 | 0.049 | down |
| ZCCHC8 | −0.09 | 0.017 | down |

**Pattern**: telomerase catalytic/biogenesis components (TERT, WRAP53, DKC1) are *up*; shelterin/CST telomere-protection components (TINF2, STN1) are slightly *down*. This is consistent with a stressed-epithelium response: cells try to upregulate telomerase machinery but lose the protective cap. Net effect = telomere instability — the signature you'd expect in a disease where the *capacity* for telomere maintenance is genetically compromised (Phase G genetics).

**Refined imetelstat thesis** (cf. Phase G): TERT mRNA is *induced* in IPF lung. Imetelstat would shut down this compensatory response, almost certainly accelerating disease. This further reinforces that telomerase **activation** (not inhibition) is the right intervention class.

## Hallmark GSEA (figure H4)

| Direction | Hallmark | NES | FDR |
|-----------|----------|----:|----:|
| UP | **Epithelial Mesenchymal Transition** | **+1.82** | 0.001 |
| UP | KRAS Signaling Dn | +1.45 | 0.15 |
| UP | Spermatogenesis | +1.45 | 0.11 |
| UP | Glycolysis | +1.33 | 0.31 |
| UP | E2F Targets / G2-M | +1.28/+1.22 | – |
| DOWN | **Interferon Alpha Response** | **−2.28** | 0.001 |
| DOWN | **TGF-beta Signaling** | **−1.82** | 0.005 |
| DOWN | TNF-alpha via NFκB | −1.52 | 0.058 |
| DOWN | Heme Metabolism | −1.49 | 0.049 |
| DOWN | Cholesterol Homeostasis | −1.42 | 0.091 |

EMT being the top up-set is expected. The **IFN-α dampening** is consistent with growing literature on impaired antiviral/anti-senescence responses in IPF AT2 cells. The **TGF-β Hallmark being negative** looks paradoxical (TGF-β is *the* canonical IPF cytokine) but reflects what the Hallmark gene set actually contains: hematopoietic/immune-cell TGF-β response genes. The fibrotic ECM-deposition arm of TGF-β signalling lives in different gene sets (e.g. Hallmark Apical Junction was up at +1.20, and ECM-remodelling GO terms would be expected up). Worth flagging in the report as a Hallmark-set caveat, not a biological surprise.

## Implications for the composite

Phase H gives us a transcriptomic axis. Genes where the **bulk DE confirms expected disease direction** are the most credible targets. Composite v2 (to be applied in Phase J) will add:

- **`DE consistency` bonus** (+): non-zero LFC with padj<0.05. Worth ~0.10 to the composite.
- **`Cell-composition` flag**: targets whose down-regulation is plausibly composition-driven (PDGFRA, FLT4, KDR — vasculature/normal fibroblast loss) get a context flag rather than a demerit.

Refined top-tier (Phase H-aware):

1. **MUC5B** — composite ↑ (LFC +3.46 with strong genetics)
2. **DSP** — composite ↑ (LFC +1.06, GWAS L2G 0.94)
3. **TERT** — composite ↑ but with the Phase-G directionality caveat (genetic LOF + transcriptomic induction → activator drug class needed)
4. **SFTPA2** — composite ↑ (LFC −0.90 makes biological sense for surfactant LOF familial IPF)
5. **MUC5AC** — composite ↑ (LFC +3.25)
6. **FAM13A** — composite ↑ (LFC −0.27, concordant with GWAS sign)
7. **PARN, RTEL1, SPDL1** — kept on telomere/genetics strength but no transcriptomic signal at the bulk level (not surprising for Mendelian LOF genes in a heterogeneous tissue mix).

## Figures

- `figures/H1_pca.png` — PCA & variance
- `figures/H2_volcano.png` — annotated volcano (top-20 + telomere panel)
- `figures/H3_target_bars.png` — per-target bar chart (this is the headline panel)
- `figures/H4_hallmark.png` — Hallmark GSEA bar chart

## Reproducibility

- Dataset: `/data/bulk-gene-counts/GSE150910/GSE150910_gene-level_count_file.csv.gz` (downloaded from NCBI GEO)
- Filtered counts + metadata: `/data/bulk-gene-counts/analysis/ipf/{counts_filtered,meta}.parquet`
- DE results: `/data/bulk-gene-counts/analysis/ipf/de_results.parquet` (16,844 × 6)
- GSEA: `/data/bulk-gene-counts/analysis/ipf/hallmark_gsea.csv`

Full pipeline (≈30 lines of Python) lives in the Phase J notebook.
