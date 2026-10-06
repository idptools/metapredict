"""
Check that metapredict's compiled Cython extension is installed and working.

If the compiled domain-decomposition extension can't be imported, metapredict
falls back to a slower pure-Python implementation and only emits a warning.
That is the right behaviour for users, but in CI it would let a broken build
pass unnoticed. This script turns it into a hard failure. It is run by
cibuildwheel against every wheel it builds (see [tool.cibuildwheel] in
pyproject.toml) and by the main CI workflow after installing metapredict.

Usage (from any directory, with metapredict installed)::

    python devtools/check_cython_extension.py

Exits with status 0 if the extension loads and gives the same IDR/folded
domain boundaries as the pure-Python implementation, and 1 otherwise.
"""

import sys

import numpy as np

# Synthetic disorder profile: a 60-residue IDR, an 80-residue folded region and
# another 60-residue IDR. At 200 residues it is well above the length (3 *
# gap_closure + 1 = 31 at the defaults) below which the decomposition takes a
# shortcut, so the full algorithm is exercised.
TEST_PROFILE: np.ndarray = np.array([0.9] * 60 + [0.1] * 80 + [0.9] * 60, dtype=np.float64)

# Disorder score threshold used for the comparison (the V2/V3 network default).
DISORDER_THRESHOLD: float = 0.5


def main() -> int:
    """
    Check the compiled extension loads and agrees with the pure-Python code.

    Returns
    -------
    int
        0 if the extension is available and its domain boundaries match the
        pure-Python implementation for TEST_PROFILE, otherwise 1.
    """
    from metapredict.backend import domain_definition

    if not domain_definition._CYTHON_AVAILABLE:
        print('FAIL: metapredict could not import its compiled Cython extension, '
              'so it would fall back to the slower pure-Python implementation.')
        return 1

    from metapredict.backend.cython import domain_definition as compiled_module
    print(f'Compiled extension loaded from {compiled_module.__file__}')

    compiled_result = compiled_module.build_domains_from_values(TEST_PROFILE, DISORDER_THRESHOLD)

    # metapredict's backend has no type annotations, hence the ignore
    python_result = domain_definition.__build_domains_from_values(TEST_PROFILE, DISORDER_THRESHOLD)  # type: ignore[no-untyped-call]

    # both return (IDR boundaries, folded-domain boundaries)
    if [list(part) for part in compiled_result] != [list(part) for part in python_result]:
        print(f'FAIL: compiled and pure-Python domain decomposition disagree.\n'
              f'  compiled:    {compiled_result}\n'
              f'  pure Python: {python_result}')
        return 1

    print(f'OK: compiled extension gives the expected domains {compiled_result}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
