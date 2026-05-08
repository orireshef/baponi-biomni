# Phase G — Telomere axis & telomerase therapeutics in IPF

**Status**: complete. Findings to be folded into the final notebook (Phase J).

## TL;DR — narrative pivot

Our composite ranking surfaced **TERT, PARN, RTEL1** as 3 of the top 9 IPF targets. The naive repurposing reflex was *imetelstat* (FDA-approved telomerase inhibitor). **This is mechanistically backwards.** Telomere-defect IPF is driven by *too little* telomerase activity (loss-of-function in TERT/PARN/RTEL1); inhibiting residual telomerase makes the disease worse — directly demonstrated in mouse: imetelstat counters the protective effect of a telomerase activator in bleomycin-induced lung fibrosis ([Le Saux 2013, PLoS One](https://doi.org/10.1371/journal.pone.0058423), PMID 23516479).

The **right** drug class is *telomerase activators* — and the most-studied real-world option is **danazol** (synthetic androgen; androgens upregulate TERT via the AR). Danazol elongates telomeres and produces hematological response in telomere biology disorders ([Townsley 2016, NEJM](https://doi.org/10.1056/NEJMoa1515319), PMID 27192671) and *has* been tested specifically in telomere-related-gene-mutation pulmonary fibrosis (the **ANDROTELO** Phase 2 trial, NCT03710356, [Sicre de Fontbrune 2026, ERJ Open Res](https://doi.org/10.1183/23120541.00905-2025), PMID 41953763) — but with high dropout from side effects (58% discontinuation), precluding efficacy assessment. The opportunity is therefore *better-tolerated telomerase activators / TERT-axis modulators*, not imetelstat.

This finding is itself an example of why automated drug-repurposing scoring needs expert curation: OT correctly surfaces the disease axis (telomere maintenance) but the most-prominent drug-target match (imetelstat → TERT) inverts the directionality.

## Telomeropathy gene panel — IPF association

OT release 26.03 indirect associations (`EFO_0000768`):

| Symbol | OT score | Evidence count | Notes |
|--------|----------|----------------|-------|
| PARN | 0.790 | 812 | Top genetic-axis IPF target overall |
| RTEL1 | 0.733 | 38 | Telomere helicase, familial IPF |
| TERT | 0.721 | 2,770 | Catalytic subunit of telomerase |
| STN1 | 0.260 | 3 | CST complex (telomere protection) |
| CTC1 | 0.111 | 1 | CST complex |
| TERC | 0.038 | 32 | RNA component of telomerase (lncRNA, less indexed) |
| ZCCHC8 | 0.028 | 2 | TERC processing |
| TINF2 | 0.005 | 7 | Shelterin component |
| DKC1 | 0.004 | 8 | Dyskerin, X-linked DC |
| NAF1 | 0.001 | 1 | TERC stability |

(NHP2, NOP10, WRAP53, ACD, TEN1 had no IPF association rows.)

## GWAS credible-set fine-mapping (IPF studies)

L2G predictions over IPF/ILD studies in OT (`GCST90018120`, `GCST001968`, `GCST90399719`, `GCST90258669`, `GCST90270267`):

| L2G score | Symbol | Variant | Chr:Pos | β | log10(p) | Study |
|-----------|--------|---------|---------|---|----------|-------|
| 0.94 | **DSP** | 6_7562999_T_G | 6:7562999 | +0.36 | −19 | Fingerlin 2013 |
| 0.93 | **MUC5AC** | 11_1197927_C_A | 11:1197927 | +0.06 | −15 | Duckworth 2020 |
| 0.89 | **MUC5B** | 11_1219991_G_T (rs35705950) | 11:1219991 | +0.034 | **−54** | Duckworth 2020 |
| 0.88 | **FAM13A** | 4_88890044_G_T | 4:88890044 | −0.25 | −11 | Fingerlin 2013 |
| 0.85 | DPP9 | 19_4717660_A_G | 19:4717660 | +0.25 | −12 | Fingerlin 2013 |
| 0.80 | **TERT** | 5_1286401_C_A | 5:1286401 | +0.31 | −19 | Fingerlin 2013 |
| 0.80 | **TERT** | 5_1279675_C_T | 5:1279675 | −0.15 | −9 | Zhou 2022 |
| 0.45 | **LRRC34** / MYNN / ACTRT3 | 3_169800667_T_C | 3:169800667 | +0.26 | −13 | Fingerlin 2013 (TERC locus) |

Telomere axis is fine-mapped at GWAS resolution: **TERT** at 5p15.33 (rs2736100 region) and **TERC** at 3q26 (LRRC34/MYNN tagging). Surfactant axis (SFTPA2) is rare-variant driven and does not appear in common-variant fine-mapping.

## Imetelstat — clinical activity (OT 26.03)

ChEMBL: `CHEMBL2107856` (IMETELSTAT) and `CHEMBL2108702` (IMETELSTAT SODIUM). MoA: telomerase reverse transcriptase inhibitor (TERT, ENSG00000164362).

| Indication | Max stage |
|-----------|-----------|
| Anemia (low-risk MDS) | **APPROVAL** (FDA 2024) |
| Myelodysplastic syndrome | **APPROVAL** |
| Myelofibrosis | Phase 3 |
| Breast cancer, ET, PV, NSCLC, multiple myeloma | Phase 2 |
| Lymphoma, neuroblastoma, lung cancer | Phase 1 |
| **IPF / pulmonary fibrosis** | **never tested** |

OT `drug_warning` for imetelstat: empty (no major historical safety signals on file).

## Danazol — clinical activity (OT 26.03)

ChEMBL: `CHEMBL1479`. MoA: androgen receptor agonist + progesterone receptor agonist (no direct telomerase target listed). Notable indications:

| Indication | Max stage |
|-----------|-----------|
| Endometriosis, menorrhagia, breast fibrocystic disease | APPROVAL |
| Infertility | Phase 3 |
| **Dyskeratosis congenita, aplastic anemia, Fanconi anemia** | Phase 1/2 |
| Telomere shortening, leukocyte telomere length | OT explicitly tags AR/PGR |

So OT already encodes the telomere-axis indication for danazol — but **not for IPF or pulmonary fibrosis**, despite the existing PF-specific trial.

## Key references (PubMed)

- Le Saux 2013, *PLoS One*: telomerase activator GRN510 suppresses bleomycin lung fibrosis; imetelstat counters this. [DOI](https://doi.org/10.1371/journal.pone.0058423) (PMID 23516479)
- Townsley 2016, *NEJM*: danazol elongates telomeres in TBD; mean +386 bp at 24 mo, hematological response 79–83%. [DOI](https://doi.org/10.1056/NEJMoa1515319) (PMID 27192671)
- Chambers 2020, *Respirol Case Rep*: danazol + immunosuppression in telomeropathy ILD case — telomere length normalized after 18 mo. [DOI](https://doi.org/10.1002/rcr2.607) (PMID 32607243)
- **Sicre de Fontbrune 2026, *ERJ Open Res***: ANDROTELO Phase 2 trial (NCT03710356) — danazol in TRG-mutation PF/BMF, n=30. PF arm: 14/24 evaluable at 12 mo; FVC change median −10%; **9/24 (38%) discontinued for side effects**; conclusion: "danazol was poorly tolerated in patients with TRG-related PF in this study, thus precluding efficacy assessment." [DOI](https://doi.org/10.1183/23120541.00905-2025) (PMID 41953763)
- Almansoori 2025, *Front Mol Biosci*: review of telomerase structure & emerging therapeutics. [DOI](https://doi.org/10.3389/fmolb.2025.1681988) (PMID 41427014)

(According to PubMed.)

## Therapeutic implications (for the notebook discussion)

1. **OT signal is correct, drug pairing is wrong**: TERT high score → imetelstat is the wrong drug; mechanistically should worsen disease.
2. **Right drug class has been tried**: danazol elongates telomeres but tolerability is the rate-limiter (ANDROTELO 2026).
3. **Open opportunity**: better-tolerated telomerase activators (or AR-pathway modulators) for the ~10–30% of IPF cases with TRG mutations or short telomeres. Patient stratification by telomere length could enrich responders.
4. **Diagnostic adjacency**: telomere length measurement is already clinically standardised (flow-FISH); a stratification trial is feasible.

## What this means for our composite

The current composite gives TERT a high score (0.561) driven by genetics + druggability. But the *druggability* feature reflects existence of imetelstat, which we now know is the wrong-direction drug. Two fixes for Phase H:

1. Add a **directionality flag** to the per-target rationale text — for LOF-driven targets, agonists/activators are needed, not inhibitors.
2. When the bulk RNA-seq comes in (Phase H), check whether *TERT mRNA is down in IPF lung* — if so, that is concordant with the LOF/activator thesis. (Predicted: yes, modestly.)
