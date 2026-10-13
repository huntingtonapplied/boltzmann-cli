"""Boltzmann CLI — multiphysics simulation platform from your terminal."""
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("boltzmann-cli")
except PackageNotFoundError:
    __version__ = "1.0.2"
