---
name: open-targets
description: "Query Open Targets Platform data (target-disease associations, drugs, evidence, GWAS, variants, expression, mouse phenotypes, drug warnings, etc.) from the parquet release mounted in the Baponi sandbox. Use when the user asks about Open Targets, target-disease links, druggability, drug mechanisms, clinical indications, GWAS credible sets, ChEMBL drug data, gene2phenotype, ClinGen, EVA, IMPC, or anything in the OT Platform schema."
---

# Open Targets via Baponi sandbox

The Open Targets Platform data release is mounted at `/data/open-targets-public/<release>/output/` inside the Baponi sandbox. Query it with DuckDB over the parquet files instead of using a remote MCP server.

## When to use

- Target-disease association queries (overall or per data source / data type)
- Drug → target → indication lookups (ChEMBL drug molecule, mechanism of action, warnings)
- Evidence pulls (ClinGen, EVA, gene2phenotype, GWAS credible sets, CRISPR, EuropePMC, IMPC, ...)
- Variant / GWAS study / locus-to-gene predictions
- Target prioritisation, mouse phenotype, expression, GO, pathway, interactions
- Clinical indication / clinical target / clinical report data

If the task is *literature search* use the PubMed MCP. For *clinical trial registry* lookups (CT.gov), the local plugin is currently disabled — fall back to the OT clinical_indication / clinical_report tables or scrape via Python.

## Mechanism

All queries run via the **`mcp__baponi__sandbox_execute`** tool. Stateless by default — pass a `thread_id` (e.g. `ot-query-<8 random chars>`) so DuckDB stays installed across calls in the same session.

### Bootstrap pattern

First call (bash, with progress bar suppressed — pip's progress output is verbose enough to overflow the tool-result token budget):

```bash
pip install duckdb -q --break-system-packages --progress-bar off 2>&1 | tail -1
```

Then Python (reusing the same `thread_id` so the install persists):

```python
import duckdb
RELEASE = "26.03"  # or the latest available release
BASE = f"/data/open-targets-public/{RELEASE}/output"
con = duckdb.connect()
```

To discover the latest release:

```bash
ls /data/open-targets-public/
```

### Querying parquets

Each table is a directory of `part-*.snappy.parquet` files. Glob them:

```python
con.execute(f"SELECT * FROM '{BASE}/target/*.parquet' WHERE approvedSymbol = 'BRCA1'").df()
```

For repeated queries on the same table, register a view:

```python
con.execute(f"CREATE VIEW target AS SELECT * FROM '{BASE}/target/*.parquet'")
```

## Data dictionary (release 26.03)

55 tables. Key ones below — `DESCRIBE SELECT * FROM '<glob>' LIMIT 1` for full schema of any table.

### Core entities

| Table | Rows | Key fields |
|-------|------|-----------|
| `target` | 78k | `id` (Ensembl gene), `approvedSymbol`, `biotype`, `genomicLocation`, `go`, `hallmarks`, `subcellularLocations`, `targetClass` |
| `disease` | 47k | `id` (EFO/MONDO/Orphanet), `name`, `description`, `ancestors`, `descendants`, `therapeuticAreas`, `synonyms` |
| `drug_molecule` | 22k | `id` (ChEMBL), `name`, `drugType`, `canonicalSmiles`, `inchiKey`, `tradeNames`, `crossReferences`, `maximumClinicalStage` |
| `variant` | 7.4M | `variantId`, `chromosome`, `position`, alleles, `mostSevereConsequenceId`, `transcriptConsequences`, `alleleFrequencies`, `rsIds` |

### Associations (target ↔ disease)

| Table | Rows | Notes |
|-------|------|-------|
| `association_overall_direct` | 4.5M | `(diseaseId, targetId, associationScore, evidenceCount, timeseries, currentNovelty)` — direct evidence only |
| `association_overall_indirect` | — | rolled up via disease ontology |
| `association_by_datasource_direct` / `_indirect` | — | per-source breakdown (e.g. ClinGen, EVA, ChEMBL) |
| `association_by_datatype_direct` / `_indirect` | — | per-type breakdown (genetic, drugs, RNA expression, ...) |

### Drugs / clinical

| Table | Rows | Notes |
|-------|------|-------|
| `drug_mechanism_of_action` | 6.5k | `actionType`, `mechanismOfAction`, `chemblIds`, `targets[]` |
| `drug_warning` | 2.3k | FDA-style warnings, `toxicityClass`, `warningType`, `efoTerm` |
| `clinical_indication` | 54k | `(drugId, diseaseId, maxClinicalStage)` |
| `clinical_target` | 13k | `(drugId, targetId, diseases[], maxClinicalStage)` |
| `clinical_report` | — | underlying trial / submission docs |

### Evidence (per source)

`evidence_clingen`, `evidence_eva`, `evidence_eva_somatic`, `evidence_gene2phenotype`, `evidence_gene_burden`, `evidence_genomics_england`, `evidence_gwas_credible_sets`, `evidence_impc`, `evidence_intogen`, `evidence_orphanet`, `evidence_reactome`, `evidence_uniprot_literature`, `evidence_uniprot_variants`, `evidence_cancer_biomarkers`, `evidence_cancer_gene_census`, `evidence_clinical_precedence`, `evidence_crispr`, `evidence_crispr_screen`, `evidence_europepmc`, `evidence_expression_atlas`.

Common columns across evidence tables: `targetId`, `diseaseId`, `datasourceId`, `datatypeId`, `score`. Source-specific columns (e.g. `confidence`, `allelicRequirements`) vary — `DESCRIBE` first.

### Genetics / GWAS

| Table | Rows | Notes |
|-------|------|-------|
| `study` | 2.0M | GWAS / QTL studies, `studyId`, `geneId`, `traitFromSource`, `pubmedId` |
| `credible_set` | 3.5M | `studyLocusId`, `studyId`, `variantId`, `beta`, `pValueMantissa/Exponent` |
| `l2g_prediction` | — | locus-to-gene predictions |
| `colocalisation` | — | study-pair colocalisation results |

### Other

`expression` (per-tissue), `mouse_phenotype`, `pharmacogenomics`, `interaction` (14.6M PPIs), `interaction_evidence`, `target_prioritisation` (78k, druggability scores), `target_essentiality`, `disease_phenotype`, `disease_hpo`, `go`, `so`, `biosample`, `enhancer_to_gene`, `literature`, `literature_vector`, `openfda_significant_adverse_drug_reactions`.

## Example queries

### 1. Top targets for a disease

```python
import duckdb
con = duckdb.connect()
BASE = "/data/open-targets-public/26.03/output"
con.execute(f"""
    SELECT a.targetId, t.approvedSymbol, t.approvedName, a.associationScore, a.evidenceCount
    FROM '{BASE}/association_overall_direct/*.parquet' a
    JOIN '{BASE}/target/*.parquet' t ON t.id = a.targetId
    WHERE a.diseaseId = 'EFO_0000305'  -- breast carcinoma
    ORDER BY a.associationScore DESC
    LIMIT 20
""").df()
```

### 2. Drugs that target a gene

```python
con.execute(f"""
    SELECT d.name, d.drugType, d.maximumClinicalStage,
           moa.actionType, moa.mechanismOfAction
    FROM '{BASE}/drug_mechanism_of_action/*.parquet' moa,
         UNNEST(moa.targets) AS u(target_id),
         UNNEST(moa.chemblIds) AS c(chembl_id)
    JOIN '{BASE}/drug_molecule/*.parquet' d ON d.id = c.chembl_id
    JOIN '{BASE}/target/*.parquet' t ON t.id = u.target_id
    WHERE t.approvedSymbol = 'EGFR'
""").df()
```

### 3. ClinGen evidence for a target

```python
con.execute(f"""
    SELECT diseaseId, diseaseFromSource, confidence, allelicRequirements, score
    FROM '{BASE}/evidence_clingen/*.parquet'
    WHERE targetId = 'ENSG00000012048'  -- BRCA1
    ORDER BY score DESC
""").df()
```

### 4. Disease ontology walk (descendants of a therapeutic area)

```python
con.execute(f"""
    SELECT id, name FROM '{BASE}/disease/*.parquet'
    WHERE list_contains(ancestors, 'EFO_0000319')  -- cardiovascular disease
""").df()
```

### 5. GWAS credible-set hits in a region

```python
con.execute(f"""
    SELECT studyId, variantId, position, beta, pValueMantissa, pValueExponent
    FROM '{BASE}/credible_set/*.parquet'
    WHERE chromosome = '17' AND position BETWEEN 41100000 AND 41400000
    ORDER BY pValueExponent ASC
    LIMIT 50
""").df()
```

## Tips

- **`thread_id`**: reuse the same id across all calls for one task → DuckDB and connection stay live, no reinstall.
- **Filter early**: most tables are partitioned only at the file level; predicate pushdown works on parquet but JOINs over 14M+ rows (e.g. `interaction`) without filters will be slow. Always restrict by id/symbol first.
- **Struct columns**: use dot syntax (`canonicalTranscript.start`) or `UNNEST` for arrays-of-structs.
- **EFO / Mondo IDs**: OT's `disease.id` uses underscore form (`EFO_0000305`), not colon.
- **Releases**: bump `RELEASE` to whatever is newest under `/data/open-targets-public/`.

## Why a skill, not an MCP

The upstream `open-targets@life-sciences` plugin's MCP server (`mcp.platform.opentargets.org`) currently rejects the protocol versions Claude Code negotiates (`2024-11-05`, `2025-06-18`) — it only accepts `2025-03-26`. Even if it worked, the network round-trips are slower than DuckDB scans of the locally-mounted parquet release, and the parquet release is the canonical artefact (everything Open Targets serves is derived from it). The skill therefore replaces the MCP entirely.
