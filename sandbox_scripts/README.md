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

Downloads gene-count / expression data for a GEO Series (GSE) from NCBI's
public FTP. Stdlib-only.

```text
python geo_download.py GSE12345 /home/baponi/data/GSE12345
python geo_download.py GSE12345 /home/baponi/data/GSE12345 --include suppl
python geo_download.py GSE12345 /home/baponi/data/GSE12345 --only matrix
```

Defaults to `matrix` (the gene-by-sample expression matrix in
`series_matrix.txt.gz`) + `soft` (full SOFT metadata). `--include suppl`
opts in to raw supplementary archives, which are usually large and only
needed if you're processing FASTQs / CEL files yourself.

The script's `download_gse(gse_id, target_dir, categories)` function is also
importable if you'd rather call it from agent-generated Python:

```python
import sys; sys.path.insert(0, "/home/baponi")
from geo_download import download_gse
result = download_gse("GSE12345", "/home/baponi/data/GSE12345", ["matrix"])
```
