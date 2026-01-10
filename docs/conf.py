"""
Sphinx configuration file for Pykrieg documentation.
"""

import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath('../src'))

project = "Pykrieg"
author = "ssjmarx"
copyright = "2026, ssjmarx"

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}
