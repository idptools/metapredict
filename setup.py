from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import os
import numpy

cython_file = os.path.join("metapredict", "backend", "cython", "domain_definition.pyx")

extensions = [
    Extension(
        name="metapredict.backend.cython.domain_definition",
         sources=[cython_file],
         include_dirs=[numpy.get_include()],
     )
 ]
 
 
setup(
    ext_modules = cythonize(extensions, compiler_directives={'language_level' : "3"}),
    packages=find_packages(),

    # Optional include package data to ship with your package
    # Customize MANIFEST.in if the general case does not suit your needs
    # Comment out this line to prevent the files from being packaged with your software
    include_package_data=True
    )