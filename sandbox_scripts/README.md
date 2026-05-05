# Sandbox scripts

Standalone Python helpers meant to run **inside** the Baponi sandbox alongside
the LLM-generated code. Each one is intentionally stdlib-only or restricted to
packages already in the cbioportal/biomni image so the agent can use them
without an install dance.

## How the agent gets a script into the sandbox

The biomni gradio UI's "upload" button drops files on the *host* machine, not
into the sandbox. To make a script available inside the sandbox, you have
three options — pick whichever fits the moment:

1. **Have the agent fetch it from GitHub.** Easiest when the script lives in
   this repo's `master`. Just tell the agent in chat:

   > Please run `curl -fsSL https://raw.githubusercontent.com/orireshef/baponi-biomni/master/sandbox_scripts/geo_download.py -o /home/baponi/geo_download.py` and then run it for GSE12345 into /home/baponi/data/GSE12345.

   Files written under `/home/baponi/` persist across calls in the same Baponi
   thread, so subsequent prompts can reference the path directly.

2. **Paste the script inline.** Open the file, paste it into the chat with a
   "save this to `/home/baponi/foo.py` then run it" instruction. Useful when
   you've edited locally and don't want to push first.

3. **Push a one-liner that builds the script.** For tiny helpers, just have
   the agent write a heredoc directly: `cat > /home/baponi/foo.py <<'EOF' ... EOF`.

There's deliberately no special "upload to sandbox" plumbing in
`baponi_biomni`: bash already covers it, and adding a custom code path would
just be another thing to maintain.

## Scripts

### `geo_download.py`

Downloads everything GEO hosts for a Series (matrix, soft, suppl) from NCBI's
public FTP. Stdlib-only. Mirrors the canonical workflow from the
[HBC public-genomic-data tutorial](https://hbctraining.github.io/Accessing_public_genomic_data/lessons/accessing_public_experimental_data.html).

By project convention each experiment lands under
**`/data/bulk-gene-counts/<gse_id>/`**, with the three GEO categories nested
inside:

```
/data/bulk-gene-counts/GSE50499/
├── matrix/  GSE50499_series_matrix.txt.gz
├── soft/    GSE50499_family.soft.gz
└── suppl/   GSE50499_GEO_Ceman_counts.txt.gz
```

```text
python geo_download.py GSE50499                   # default target dir
python geo_download.py GSE50499 --only suppl      # just the count matrix
python geo_download.py GSE50499 --skip matrix
python geo_download.py GSE50499 /custom/path      # override target dir
```

Defaults to all three categories. For RNA-seq studies the gene-count matrix
that downstream tools (DESeq2 / edgeR / limma) expect typically lives in
`suppl/`, **not** `matrix/` (the latter is GEO's own normalization, often
empty or uninformative for RNA-seq).

**Note**: GEO's FTP does NOT host raw FASTQs — those are in SRA, referenced
from a GEO record via SRR/SRX accessions. Pulling raw reads needs sra-tools
(`prefetch` + `fasterq-dump`) which is out of this script's scope.

The `download_gse(gse_id, target_dir=None, categories=...)` function is also
importable if you'd rather call it from agent-generated Python:

```python
import sys; sys.path.insert(0, "/home/baponi")
from geo_download import download_gse
result = download_gse("GSE50499")                     # default target dir
result = download_gse("GSE50499", categories=["suppl"])
```
