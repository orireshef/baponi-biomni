class RNotSupportedError(NotImplementedError):
    """R execution requires a custom OCI image on Baponi (Python 3.14 default has no Rscript)."""

    def __init__(self) -> None:
        super().__init__(
            "R execution is not supported in v1. Baponi's default image lacks "
            "Rscript. To enable, push a custom OCI image with r-base via the Baponi "
            "admin console, then route run_r_code through bash."
        )
