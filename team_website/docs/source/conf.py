# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
import django

project = 'AlgEdu Team'
copyright = '2025, Gleb Karasev'
author = 'Gleb Karasev'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

extensions = [
    'sphinx.ext.autodoc', 
    'sphinx.ext.viewcode', 
]
html_theme = 'sphinx_rtd_theme'

sys.path.insert(0, os.path.abspath('../../..'))

sys.path.insert(0, os.path.abspath('../..'))

# Настраиваем Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'AlgEdu_Team.settings'
django.setup()