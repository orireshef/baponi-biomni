# Custom Baponi Sandbox Image

The default Baponi OCI image (Python 3.14 + Node 25 + bash) ships zero
biomedical libraries. Biomni's curated tools — for example
`biomni.tool.pharmacology.predict_admet_properties` — require the `biomni`
package itself plus rdkit, scanpy, biopython, scvi-tools, and a long list of
other heavy deps. Without those preinstalled, the agent burns its 60s exec
budget on `pip install` calls and frequently times out on first model load.

## Recommended image: `cbioportal/biomni:latest`

Memorial Sloan Kettering / cbioportal publish a maintained biomni image on
Docker Hub:

```
docker.io/cbioportal/biomni:latest
```

- **Size**: ~5.1 GB compressed.
- **Base**: Ubuntu 20.04 + Mambaforge + biomni's `biomni_env/fixed_env.yml`
  (the upstream-documented reduced env that drops conda-only R and CLI
  tools but keeps the full Python stack).
- **Includes**: the `biomni` Python package and its full pip dep set
  (scanpy, biopython, rdkit, scvi-tools, scvelo, gget, faiss-cpu,
  cellxgene-census, biopandas, biotite, lifelines, scikit-bio, pymed,
  arxiv, scholarly, umap-learn, scrublet, harmony-pytorch, pysam, pyfaidx,
  pyranges, pybedtools, openmm, igraph, pyscenic, cooler, trackpy,
  cellpose, ViennaRNA, cobra, hmmlearn, msprime, tskit, plus the gradio
  and bedrock extras), so most biomni tools that don't shell out to R or
  bio-CLIs work out of the box.
- **Architecture**: `linux/amd64` (matches the Baponi sandbox runtime).
- **Maintenance**: actively updated by inodb / cbioportal.

## What it does NOT include

- **R + Bioconductor** — biomni's R-based tools (DESeq2, Seurat, etc.) won't
  run. `BaponiExecutor.r()` continues to raise `RNotSupportedError`.
- **Bio CLIs from apt or conda** — no `blast`, `samtools`, `bwa`, `bedtools`,
  `fastqc`, `mafft`, `bowtie2` available. Tools that shell out to these
  fail.
- **PLINK / IQ-TREE / GCTA** — biomni's `install_cli_tools.sh` items.

If a biomni tool that needs any of these surfaces in real use, we'll layer
them on top via a derived image (`FROM cbioportal/biomni:latest` + targeted
apt installs). Build it on demand rather than carrying the cost upfront.

## Hooking it up to Baponi

Baponi binds one OCI image per API key in the admin console.

1. In the Baponi admin console, create a new API key with the image set to
   `docker.io/cbioportal/biomni:latest`.
2. Drop the new key into `.env` as `BAPONI_API_KEY`.
3. Re-run `examples/admet.py` or the gradio UI. The agent should now do
   `from biomni.tool.pharmacology import predict_admet_properties` directly
   without the runtime install dance.

The image is public on Docker Hub, so Baponi can pull it without auth.

## Verifying

After hooking it up, two quick checks:

```bash
# 1. biomni is preinstalled
uv run python -c "
from baponi_biomni import BaponiExecutor
ex = BaponiExecutor(thread_id='img-check', timeout=30)
print(ex.python('import biomni; print(biomni.__version__)'))
"

# 2. rdkit works without install
uv run python -c "
from baponi_biomni import BaponiExecutor
ex = BaponiExecutor(thread_id='rdkit-check', timeout=30)
print(ex.python('from rdkit import Chem; print(Chem.MolFromSmiles(\"CCO\"))'))
"
```

## Out of scope (next iterations)

When the need surfaces:

- **R + Bioconductor layer**: a small derived Dockerfile
  (`FROM cbioportal/biomni:latest`) that adds `r-base`, `r-recommended`, and
  Bioconductor essentials (DESeq2, Seurat, edgeR, limma...). Then rewire
  `BaponiExecutor.r()` to route through `client.execute(language="bash")`
  with `Rscript`.
- **Bio CLI layer**: derived image adding ncbi-blast+, samtools, bwa,
  bedtools, fastqc, mafft from apt.
- **PLINK / IQ-TREE / GCTA**: only if an exercised tool needs them.
