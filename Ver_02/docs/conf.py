# Sphinx configuration for Ver_02 documentation
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'Nikon NEF Batch Editor - Ver_02'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel',
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
html_theme = 'alabaster'
html_static_path = ['_static']

# Make sure autodoc shows members in source order when possible
autodoc_member_order = 'bysource'
# Enable referencing sections by their titles
autosectionlabel_prefix_document = True
