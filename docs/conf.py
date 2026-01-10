"""
Sphinx configuration file for Pykrieg documentation.

Minimal configuration for Read the Docs setup.
"""

project = "Pykrieg"
author = "ssjmarx"
copyright = "2026, ssjmarx"

extensions = []

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
