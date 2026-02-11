#!/usr/bin/env python3
"""Normalize notebook source fields to list-of-strings format.

Usage:
    scripts/normalize_notebooks.py nb1.ipynb nb2.ipynb ...
"""
import sys, nbformat

notebooks = [f for f in sys.argv[1:] if f.endswith(".ipynb")]
if not notebooks:
    sys.exit(0)

for path in notebooks:
    nb = nbformat.read(path, as_version=4)
    nbformat.write(nb, path)
    print(f"normalized: {path}")
