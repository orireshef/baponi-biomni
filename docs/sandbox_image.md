# Custom Baponi Sandbox Image

The default Baponi OCI image (Python 3.14 + Node 25 + bash) ships a stdlib
Python and zero biomedical libraries. Biomni's curated tools (e.g.
`biomni.tool.pharmacology.predict_admet_properties`) require the `biomni`
package plus rdkit, scanpy, biopython, R + Bioconductor, and a long list of
bioinformatics CLIs. This image bundles all of that.

## What's in it

Everything biomni's `biomni_env/setup.sh` installs, except the heaviest
desktop-only tools (PLINK/IQ-TREE/GCTA — added later if needed):

- **Python 3.11** — biomni's expected runtime. `python` and `python3` both
  resolve to it.
- **biomni** (latest from PyPI) and its full pip dep set.
- **Bio Python**: scanpy, biopython, biopandas, biotite, rdkit, scvi-tools,
  scvelo, scrublet, scikit-bio, gget, faiss-cpu, openmm, pysam, pyranges,
  cobra, pyscenic, cellpose, cellxgene-census, plus ~30 more.
- **Bio CLIs from apt**: ncbi-blast+, samtools, bowtie2, bwa, bedtools,
  fastqc, mafft.
- **R 4.x** with `r-recommended` + Bioconductor 3.18: DESeq2, edgeR, limma,
  Seurat, SingleCellExperiment, scran, scater, fgsea, clusterProfiler,
  org.Hs.eg.db, org.Mm.eg.db, GenomicRanges, GenomicFeatures, Biostrings,
  rtracklayer, plus tidyverse, data.table, harmony, WGCNA, survival.
- **agent libs**: langchain, langgraph, openai, anthropic, mcp,
  cloudpickle (lets us upgrade `BaponiExecutor` from stdlib pickle to
  cloudpickle without an in-sandbox install dance — follow-up).

Final compressed image: ~10–12 GB, uncompressed ~25 GB.

## Build & publish

CI builds and pushes on every push to master that touches
`docker/Dockerfile.sandbox` or this workflow. Manual trigger:

```bash
gh workflow run build-sandbox-image.yml \
  -F tag=sandbox-r-bioconductor-2026-05
```

Local build for testing:

```bash
docker buildx build \
  --platform linux/amd64 \
  -f docker/Dockerfile.sandbox \
  -t ghcr.io/orireshef/baponi-biomni:sandbox-local \
  --load \
  .
```

Smoke-check the layer:

```bash
docker run --rm ghcr.io/orireshef/baponi-biomni:sandbox-local \
  python -c "import biomni; from biomni.tool import pharmacology; print('ok')"

docker run --rm ghcr.io/orireshef/baponi-biomni:sandbox-local \
  Rscript -e 'library(DESeq2); cat("DESeq2", as.character(packageVersion("DESeq2")), "\n")'
```

## Hooking it up to Baponi

Baponi binds one OCI image per API key (admin console → API Keys → image).

1. Wait for the GH Action to push the image to
   `ghcr.io/orireshef/baponi-biomni:sandbox-latest` (or your tag).
2. If the registry is private, make sure Baponi's image pull credentials
   include the `read:packages` scope on this org.
3. In the Baponi admin console, create a new API key with this image
   pinned. Copy the key into `.env` as `BAPONI_API_KEY`.
4. Re-run `examples/admet.py`. The agent should be able to
   `from biomni.tool.pharmacology import predict_admet_properties` without
   the runtime install dance.

## Verifying

After hooking it up, two quick checks:

```bash
# 1. biomni is preinstalled
uv run python -c "
from baponi_biomni import BaponiExecutor
ex = BaponiExecutor(thread_id='img-check', timeout=30)
print(ex.python('import biomni; print(biomni.__version__)'))
"

# 2. R works
uv run python -c "
from baponi_biomni import BaponiExecutor
ex = BaponiExecutor(thread_id='r-check', timeout=30)
print(ex.bash('Rscript -e \"library(DESeq2); cat(packageVersion(\\\"DESeq2\\\")); cat(\\\"\\\\n\\\")\"'))
"
```

## Versioning policy

- `sandbox-latest` follows master and is what the live API key should
  reference for normal use.
- `sandbox-<git-sha>` is published per commit; useful for pinning a
  reproducible tag.
- Manual-tagged builds (e.g. `sandbox-r-bioconductor-2026-05`) are for
  rollouts that need a stable handle independent of master movement.

When biomni or the bio_env dependency list changes upstream, regenerate the
image and bump `sandbox-latest`. The GH Action build cache amortizes most of
the rebuild cost.

## Out of scope (next iterations)

- **PLINK / IQ-TREE / GCTA**: biomni's `install_cli_tools.sh` installs these
  to a custom path. Skipped for now to keep the image lean. Add when a tool
  that requires them is exercised.
- **GPU**: image is CPU-only. CUDA variants would be a separate workflow.
- **Custom-tag publish on PRs**: today PRs only build (no push). If we
  start needing per-PR previews, switch the workflow to push `pr-N` tags.
