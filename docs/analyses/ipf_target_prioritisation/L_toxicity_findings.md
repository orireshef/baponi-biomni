# Phase L — Toxicity / safety analysis

## What it does

Combines three OT 26.03 evidence sources into a unified safety profile for our candidate drugs and top-target classes:

1. **`drug_warning`** — formal regulatory warnings (FDA black-box, withdrawal/restricted use, etc.)
2. **`openfda_significant_adverse_drug_reactions`** — pharmacovigilance signals from FDA AERS, filtered to events where log-likelihood ratio (LLR) exceeds the disproportionality critical value (i.e. statistically over-represented in this drug's reports vs the AERS background)
3. **`target_prioritisation.hasSafetyEvent`** — target-level safety annotation (=−1 means a known safety event class is associated with this target)

## Why it matters

The Phase G headline conclusion (imetelstat is the wrong drug for IPF; danazol is the right class but tolerability fails) needs empirical safety data to support the "tolerability fails" claim, not just the ANDROTELO 38% / Eppinga 56% AE discontinuation rates from clinical trials. AERS gives us a real-world pharmacovigilance view.

## Drug-level findings

### Black-box warnings (drug_warning)

| Drug | Black-box warnings (count) | Classes |
|------|---------------------------:|---------|
| **DANAZOL** | **5** | hepatotoxicity, neurotoxicity, vascular toxicity, teratogenicity, carcinogenicity |
| MACITENTAN | 1 | teratogenicity (class effect of endothelin receptor antagonists) |
| All others (imetelstat, nintedanib, pirfenidone, pamrevlumab, simtuzumab, ziritaxestat, admilparant, nerandomilast) | 0 | – |

Danazol has by far the heaviest regulatory warning load — five distinct serious-toxicity classes. This is the regulatory foundation for the "androgen drug class is not viable for chronic IPF dosing" thesis. (See figure L2 for AERS categorical breakdown.)

### OpenFDA AERS — significant adverse-event signals

| Drug | # significant AE signals | Total AE reports | Top events (LLR signal × count) |
|------|------------------------:|------------------:|---------------------------------|
| DANAZOL | 63 | 688 | Coombs+ haemolytic anaemia (57.6 × 42); lymphadenitis (46.8 × 42); haemolysis (39.9 × 43); hepatic enzyme increased (24.8 × 46); migraine (23.3 × 43) |
| MACITENTAN | 62 | 56,684 | dyspnoea (22.3 × 4852); fluid retention (15.6 × 1653); hospitalisation (10.7 × 1862) [mostly underlying PAH disease state] |
| PIRFENIDONE | 33 | 9,476 | decreased appetite (18.8 × 774); nausea (10.8 × 1057); photosensitivity reaction (8.9 × 234) |
| NINTEDANIB | 25 | 6,569 | diarrhoea (23.6 × 1586); decreased appetite (6.4 × 464); weight decreased (5.0 × 430) |
| IMETELSTAT | 4 | 4 | infestation; metabolic disorder; malnutrition (all near critval — sample is small as imetelstat was approved 2024) |

**Danazol AERS by toxicity category** (figure L2):

| Category | # signals | # reports | Max LLR signal |
|----------|----------:|----------:|---------------:|
| hematologic | 9 | 193 | 57.6 |
| hepatic | 4 | 56 | 24.8 |
| neurologic | 1 | 43 | 23.3 |
| other | 49 | 396 | 21.9 |

The **hematologic toxicity (Coombs+ hemolytic anemia, lymphadenitis, hemolysis)** dominates the danazol AE profile — directly relevant for IPF, where elderly, often anemic patients on additional therapy can ill afford this risk. Hepatic toxicity (LFT elevation in 6.7% of reports) compounds the issue. **This explains the 38–56% discontinuation seen in ANDROTELO 2026 and Eppinga 2023 clinical trials.**

### Imetelstat — caveat on safety

Only 4 AE signals in OpenFDA — **not because it's safe, but because it's young.** Imetelstat was FDA-approved 2024 for low-risk MDS anemia; AERS reporting volume is still nascent. In its MDS Phase 3 (IMerge), the most common AEs were thrombocytopenia, neutropenia, and infusion-related reactions — all hematologic, expected for a TERT inhibitor in oncology. **In a hypothetical IPF trial, telomere-defect patients already at baseline risk for cytopenias from bone-marrow telomeropathy would be especially vulnerable** — another reason we deprioritise imetelstat for IPF beyond the directionality argument.

## Target-level safety (target_prioritisation)

Of our top-20 OT targets, those with `hasSafetyEvent = -1` (target-class safety signal):

| Target | Has safety event | Notes |
|--------|:---------------:|-------|
| FGFR1 | ✓ | FGFR family — known on-target hyperphosphatemia (RTK class) |
| FGFR3 | ✓ | |
| FLT1 | ✓ | VEGFR family — bleeding, hypertension |
| FLT4 | ✓ | |
| KDR | ✓ | |
| NR3C1 | ✓ | Glucocorticoid receptor — well-known steroid AEs |
| PDGFRB | ✓ | |
| FAM13A | ✓ | (mechanism unclear; minor weight in OT) |
| **MUC5B / MUC5AC / TERT / SFTPA2 / DSP / RTEL1 / PARN / SPDL1** | **clean** | None flagged |

Our top-5 novel targets (MUC5B, MUC5AC, TERT, SFTPA2, DSP) are **clean from a target-class safety perspective** in OT — no inherited red flags from drug-class precedents.

### Drug-class concerns by target

For top targets with existing drugs:

- **TERT (imetelstat)**: hematologic suppression is the on-target liability of telomerase inhibition (myelosuppression). Does not transfer to a hypothetical telomerase *activator* program — different mechanism, but androgen-class activators (danazol) carry the warnings tabulated above.
- **MUC5AC (clivatuzumab, ensituximab)**: cancer mAbs; AEs are cytotoxic-payload-class, not MUC5AC-on-target.
- **NR3C1 (corticosteroids)**: chronic steroid burden — diabetes, osteoporosis, infection risk, adrenal suppression. Reason corticosteroid arm of PANTHER-IPF triple therapy was harmful.
- **RTK cluster (nintedanib targets)**: well-characterised diarrhea, weight loss, LFT elevation — manageable but not benign.

## Genetic constraint as a safety proxy

OT's `geneticConstraint` (LOEUF-derived) flags genes intolerant to LoF in human population genetics — high constraint = drugging via inhibition is risky.

| Target | geneticConstraint | Interpretation |
|--------|------------------:|----------------|
| PDGFRA | −0.91 | strongly constrained — RTK class drug carries developmental risk |
| FGFR1 | −0.91 | – |
| FGFR2 | −0.90 | – |
| NR3C1 | −0.89 | – |
| KDR | −0.86 | – |
| **DSP** | **−0.75** | constrained — therapeutic *reduction* of DSP needs careful titration to avoid desmosomal failure (cardiomyopathy phenotype of LoF DSP in humans) |
| **MUC5B** | **−0.80** | constrained, but interventions are likely on the *cell state* not the protein — risk profile depends on strategy |
| FGFR3 | −0.73 | – |
| **TERT** | −0.58 | moderate — activation should not raise constraint concerns |
| **MUC5AC, SFTPA2, SPDL1** | small / positive | low constraint — well-tolerated to perturb |
| **PARN, RTEL1** | −0.49 / −0.09 | activation-class concerns are low |

**DSP's constraint is the largest red flag among our top novel targets** given that the proposed therapeutic direction (after Borie 2022 reversal) is to *reduce* DSP. Loss-of-function in DSP causes arrhythmogenic cardiomyopathy + woolly-hair syndrome — a small-molecule DSP-reducer would need exquisite tissue selectivity for lung epithelium.

## Implications

1. **Imetelstat is doubly disqualified**: wrong direction (Phase G mechanism argument) + telomerase inhibition has known hematologic toxicity (acceptable for MDS oncology but problematic in telomeropathy patients).

2. **Danazol's tolerability ceiling is empirically grounded**: 5 black-box warnings + 63 distinct AERS signals + dominant hematologic + hepatic burden. The 2026 ANDROTELO and 2023 Eppinga discontinuation rates are **predicted** by this regulatory + pharmacovigilance picture, not anomalous. The androgen drug class is not viable for chronic IPF treatment.

3. **Our top-5 novel targets are clean** at the OT target-class safety level (no `hasSafetyEvent` flags). Genetic constraint says DSP is the riskiest to drug — needs a careful selectivity story given the proposed direction.

4. **Patient stratification** is essential for any telomere-axis IPF trial: telomeropathy patients already have hematologic baseline risk, and an activator (much less an inhibitor) needs to be dosed carefully. Companion-diagnostic flow-FISH telomere-length panels exist clinically.

## Outputs

- `figures/L1_toxicity_overview.png` — # significant AE signals + total AE report volume per drug.
- `figures/L2_danazol_categories.png` — danazol AE category breakdown (hematologic dominates).
- `/data/bulk-gene-counts/analysis/ipf/aers_signals.csv` — full AERS table for our drug list.
- `/data/bulk-gene-counts/analysis/ipf/drug_warnings.csv` — drug_warning rows.

## Caveats

- **AERS is reporter-bias-laden**: under-reporting of mild AEs, over-reporting of suspected drug effects in lawsuit clusters, channeling biases (sicker patients on more active drugs). Disproportionality (LLR vs critval) corrects for some baseline frequency but not all bias.
- **Imetelstat AERS is not yet representative** (4 reports total; approval 2024). Should not be over-interpreted as "safe in all populations."
- **Macitentan signals are largely the underlying disease (PAH)**, not drug-induced events — as is partly true for nintedanib/pirfenidone in IPF (the disease is part of the AE event reporting). LLR partially corrects for this via comparison to the AERS background, but residual confounding likely.
- **Target-level `hasSafetyEvent`** is binary in OT — masks gradation of risk.
