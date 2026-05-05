#!/usr/bin/env python3
"""Download a GEO Series (GSE) accession from NCBI FTP into a target directory.

Pulls everything GEO hosts for a series: matrix, soft, and supplementary
files. For RNA-seq studies the gene-count matrices that downstream tools
(DESeq2, edgeR, limma) expect typically live in `suppl/`, not `matrix/`
(which holds GEO's own normalization and is often empty / not-counts for
RNA-seq). See https://hbctraining.github.io/Accessing_public_genomic_data/lessons/accessing_public_experimental_data.html
for the canonical workflow this script automates.

Note on raw reads: GEO's FTP does NOT host FASTQs — those live in SRA
(referenced from a GEO record via SRR/SRX accessions). Pulling raw reads
needs sra-tools (`prefetch` + `fasterq-dump`) and an SRR accession; out
of scope for this script.

Categories:
  - matrix/  (series_matrix.txt.gz: GEO-normalized expression + sample
             metadata; useful for older microarray studies, often
             empty/uninformative for RNA-seq)
  - soft/    (family.soft.gz: full SOFT-format sample annotations)
  - suppl/   (depositor-uploaded files — for RNA-seq this is where the
             gene-count matrix lives, e.g. GSE50499_GEO_Ceman_counts.txt.gz)

Default: all three. Use `--only suppl` if you just want the count matrix and
don't care about GEO's own pre-processing.

NCBI GEO FTP path layout:

    https://ftp.ncbi.nlm.nih.gov/geo/series/<NNN>nnn/<GSE>/{matrix,soft,suppl}/

where <NNN>nnn drops the last 3 digits of the accession, e.g.
  GSE12345  -> GSE12nnn
  GSE234567 -> GSE234nnn

Usage:
    python geo_download.py GSE50499 /home/baponi/data/GSE50499
    python geo_download.py GSE50499 /home/baponi/data/GSE50499 --only suppl
    python geo_download.py GSE50499 /home/baponi/data/GSE50499 --skip matrix

Returns 0 on full success, 1 on any download failure (other categories still
attempted).
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin


_GSE_RE = re.compile(r"^GSE(\d+)$", re.IGNORECASE)
_BASE = "https://ftp.ncbi.nlm.nih.gov/geo/series/"


class _LinkScraper(HTMLParser):
    """NCBI's HTTP listing returns a basic <a href="filename">filename</a>
    table. Pull every href that names a real file relative to this dir.
    Skips parent-dir links and any absolute URLs (sort headers, etc.)."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for name, value in attrs:
            if name != "href" or not value:
                continue
            if value in ("../", "/"):
                continue
            # Skip absolute URLs (e.g. NCBI listings include sort-link
            # absolutes like ?C=N;O=D) and query-only links.
            if value.startswith(("http://", "https://", "ftp://", "?")):
                continue
            # Trailing-slash entries are subdirectories, not files.
            if value.endswith("/"):
                continue
            self.links.append(value)


def _gse_dir(gse_id: str) -> str:
    """GSE12345 -> 'GSE12nnn'. Per NCBI's series prefix scheme: drop the last
    3 digits, replace with 'nnn', minimum prefix 'GSEnnn' for GSE 1-999."""
    m = _GSE_RE.match(gse_id)
    if not m:
        raise SystemExit(f"Not a valid GSE accession: {gse_id!r}")
    digits = m.group(1)
    prefix = digits[:-3] if len(digits) > 3 else ""
    return f"GSE{prefix}nnn"


def _list_remote(url: str) -> list[str]:
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        raise
    parser = _LinkScraper()
    parser.feed(html)
    return parser.links


def _download(url: str, dest: Path) -> int:
    """Streaming download. Returns bytes written."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with urllib.request.urlopen(url, timeout=300) as resp, open(dest, "wb") as f:
        while True:
            chunk = resp.read(1 << 16)
            if not chunk:
                break
            f.write(chunk)
            written += len(chunk)
    return written


def _fmt_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n //= 1024  # type: ignore[assignment]
    return f"{n} TB"


def fetch_category(
    gse_id: str, category: str, target_dir: Path, base: str = _BASE
) -> tuple[int, int]:
    """Download every file under <base>/<dir>/<gse>/<category>/.
    Returns (n_downloaded, n_failed)."""
    listing_url = urljoin(base, f"{_gse_dir(gse_id)}/{gse_id.upper()}/{category}/")
    files = _list_remote(listing_url)
    if not files:
        print(f"  [{category}] no files (or directory missing)")
        return 0, 0

    out_dir = target_dir / category
    print(f"  [{category}] {len(files)} file(s) -> {out_dir}")

    ok = 0
    fail = 0
    for fname in files:
        url = urljoin(listing_url, fname)
        dest = out_dir / fname
        try:
            n = _download(url, dest)
            print(f"    + {fname} ({_fmt_bytes(n)})")
            ok += 1
        except Exception as e:
            print(f"    ! {fname}: {e}")
            fail += 1
    return ok, fail


def download_gse(
    gse_id: str,
    target_dir: str | Path,
    categories: Iterable[str] = ("matrix", "soft", "suppl"),
) -> dict:
    """Download the requested categories for a GSE accession into target_dir.
    Returns a summary dict suitable for printing or programmatic inspection."""
    target = Path(target_dir).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)

    print(f"GEO download: {gse_id} -> {target}")
    summary: dict = {"gse_id": gse_id, "target_dir": str(target), "categories": {}}
    total_fail = 0
    for cat in categories:
        ok, fail = fetch_category(gse_id, cat, target)
        summary["categories"][cat] = {"downloaded": ok, "failed": fail}
        total_fail += fail
    summary["total_failed"] = total_fail
    print(
        f"\nDone. Categories: "
        + ", ".join(
            f"{c}={s['downloaded']}/{s['downloaded']+s['failed']}"
            for c, s in summary["categories"].items()
        )
    )
    return summary


_ALL_CATEGORIES = ("matrix", "soft", "suppl")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Download GEO Series files (matrix, soft, supplementary) "
                    "from NCBI FTP. Raw FASTQs are NOT here — those live in SRA.",
    )
    p.add_argument("gse_id", help="GEO Series accession, e.g. GSE50499")
    p.add_argument("target_dir", help="Local directory to download into")
    p.add_argument(
        "--only",
        action="append",
        choices=_ALL_CATEGORIES,
        help="Restrict to one or more categories (repeatable). "
             "Default: all three (matrix + soft + suppl).",
    )
    p.add_argument(
        "--skip",
        action="append",
        choices=_ALL_CATEGORIES,
        help="Drop a category from the active set (repeatable). "
             "E.g. `--skip matrix` if the GEO-normalized matrix is unhelpful.",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    cats: list[str] = list(args.only) if args.only else list(_ALL_CATEGORIES)
    if args.skip:
        cats = [c for c in cats if c not in args.skip]
    if not cats:
        print("No categories selected.", file=sys.stderr)
        return 2
    summary = download_gse(args.gse_id, args.target_dir, cats)
    return 1 if summary["total_failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
