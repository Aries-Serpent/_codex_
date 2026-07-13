# Sphinx configuration file for Cognitive Brain API Documentation

import os
import sys

# Add source to path
sys.path.insert(0, os.path.abspath('../../.github/agents'))

# Project information
project = 'Cognitive Brain Core'
copyright = '2026, Aries-Serpent'
author = 'GitHub Copilot Agents'
version = '2.0.0'
release = '2.0.0 (Phase 8.7 Complete)'

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.githubpages',
    'myst_parser',
]

# Napoleon settings for Google/NumPy docstring style
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# AutoDoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Source suffix
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# Master document
master_doc = 'index'

# Language
language = 'en'

# Exclude patterns
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML theme
html_theme = 'sphinx_rtd_theme'

# HTML theme options
html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
}

# HTML static path
html_static_path = ['_static']

# HTML title
html_title = f'{project} {version} Documentation'

# HTML logo
# html_logo = '_static/logo.png'

# HTML favicon
# html_favicon = '_static/favicon.ico'

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
}

# Todo extension
todo_include_todos = True

# MyST parser settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "substitution",
    "tasklist",
]
