"""Logging configuration for the Boltzmann CLI."""

import logging
import sys


logger = logging.getLogger("boltzmann")


def setup_logging(verbose: bool = False, debug: bool = False) -> logging.Logger:
    """Configure the boltzmann logger based on verbosity flags.

    All log output goes to stderr so stdout stays clean for piped/structured output.
    """
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    logger.setLevel(level)
    # Avoid duplicate handlers if setup_logging is called more than once.
    if not logger.handlers:
        logger.addHandler(handler)
    logger.propagate = False

    return logger
