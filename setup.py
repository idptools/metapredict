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

# Compile against the NumPy 1.7+ C API only. Without this every build prints a
# "Using deprecated NumPy API" warning; the extension doesn't use any of the
# deprecated API, so this is purely to keep build logs clean on every platform.
NUMPY_API_MACROS = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]

# The extension is required, not optional: if it cannot be compiled the install
# fails rather than silently falling back to the slower pure-Python domain
# decomposition. Prebuilt wheels (see .github/workflows/wheels.yml) mean most
# users never need a compiler at all.
extensions = [
    Extension(
        name="metapredict.backend.cython.domain_definition",
        sources=[cython_file],
        include_dirs=[numpy.get_include()],
        define_macros=NUMPY_API_MACROS,
    )
]

setup(
    ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),
)
