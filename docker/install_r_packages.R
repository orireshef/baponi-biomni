# Bioconductor essentials commonly used by biomni's R-based tools.
# Mirrors biomni's biomni_env/install_r_packages.R minus desktop-only deps.

options(repos = c(CRAN = "https://cloud.r-project.org"))
options(Ncpus = parallel::detectCores())

# Bioconductor manager
if (!requireNamespace("BiocManager", quietly = TRUE)) {
    install.packages("BiocManager")
}
BiocManager::install(version = "3.18", ask = FALSE, update = FALSE)

cran_packages <- c(
    "tidyverse",     # readr, dplyr, ggplot2, tibble, etc.
    "data.table",
    "Matrix",
    "Seurat",        # single-cell
    "harmony",       # batch correction
    "WGCNA",         # weighted gene co-expression
    "survival",
    "survminer",
    "pheatmap",
    "ggpubr",
    "viridis"
)

bioc_packages <- c(
    "BiocGenerics",
    "S4Vectors",
    "IRanges",
    "GenomicRanges",
    "Biostrings",
    "DESeq2",
    "edgeR",
    "limma",
    "SingleCellExperiment",
    "SummarizedExperiment",
    "scran",
    "scater",
    "fgsea",
    "clusterProfiler",
    "org.Hs.eg.db",
    "org.Mm.eg.db",
    "rtracklayer",
    "GenomicFeatures",
    "AnnotationDbi"
)

# Install CRAN packages individually so one failure doesn't kill the rest.
for (pkg in cran_packages) {
    tryCatch(
        install.packages(pkg, dependencies = TRUE),
        error = function(e) message(sprintf("[skip] CRAN %s: %s", pkg, e$message))
    )
}

# Install Bioconductor packages individually.
for (pkg in bioc_packages) {
    tryCatch(
        BiocManager::install(pkg, ask = FALSE, update = FALSE, dependencies = TRUE),
        error = function(e) message(sprintf("[skip] Bioc %s: %s", pkg, e$message))
    )
}

# Smoke-check at the end so the Docker layer fails if Seurat / DESeq2 don't load.
suppressPackageStartupMessages({
    library(Seurat)
    library(DESeq2)
    library(BiocManager)
})
cat("R smoke-check passed:",
    " Seurat", as.character(packageVersion("Seurat")),
    " DESeq2", as.character(packageVersion("DESeq2")),
    "\n")
