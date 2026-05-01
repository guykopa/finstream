"""Sphinx configuration for finstream documentation."""
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "finstream"
copyright = "2024, finstream contributors"
author = "finstream contributors"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

napoleon_google_docstring = True
napoleon_numpy_docstring = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/docs", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "alabaster"
html_static_path = ["_static"]
html_theme_options = {
    "description": "Industrial ETL pipeline for financial data",
    "github_user": "finstream",
    "github_repo": "finstream",
    "fixed_sidebar": True,
}
