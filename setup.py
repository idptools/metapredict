"""Build script for metapredict.

All package metadata and configuration live in ``pyproject.toml``. This file
exists only to compile the Cython domain-decomposition extension at build time,
which cannot yet be expressed declaratively in ``pyproject.toml``.
"""

import os

import numpy
from Cython.Build import cythonize
from setuptools import Extension, setup

cython_file = os.path.join("metapredict", "backend", "cython", "domain_definition.pyx")

extensions = [
    Extension(
        name="metapredict.backend.cython.domain_definition",
        sources=[cython_file],
        include_dirs=[numpy.get_include()],
    )
]

setup(
    ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),
)
