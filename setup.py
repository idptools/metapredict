from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import os
import numpy
import versioneer

cython_file = os.path.join("metapredict", "backend", "cython", "domain_definition.pyx")

extensions = [
    Extension(
        name="metapredict.backend.cython.domain_definition",
        sources=[cython_file],
        include_dirs=[numpy.get_include()],
    )
]

setup(
    ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    include_package_data=True,
)