"""
Code from Dan Griffith's IDP-Parrot tool from the Holehouse Lab.
All credit for this code should go to Dan.
See https://idptools-parrot.readthedocs.io/en/latest/api.html#module-parrot.encode_sequence
for more information.
"""

"""
File containing functions for encoding a string of amino acids into a numeric vector.
.............................................................................
parrot was developed by the Holehouse lab
     Original release ---- 2020

Question/comments/concerns? Raise an issue on github:
https://github.com/idptools/parrot

Licensed under the MIT license. 
"""

import numpy as np
import torch

# ONE HOT encoding per standard amino acid
ONE_HOT = {'A': 0, 'C': 1, 'D': 2, 'E': 3, 'F': 4, 'G': 5, 'H': 6, 'I': 7, 'K': 8, 'L': 9,
               'M': 10, 'N': 11, 'P': 12, 'Q': 13, 'R': 14, 'S': 15, 'T': 16, 'V': 17, 'W': 18, 'Y': 19}

# Lookup table mapping an ASCII byte value to its one-hot column index (-1 for any
# character that is not a canonical amino acid). Built once at import so encoding is a
# vectorized numpy gather rather than a per-residue Python loop.
_AA_TO_IDX = np.full(256, -1, dtype=np.int64)
for _aa, _idx in ONE_HOT.items():
    _AA_TO_IDX[ord(_aa)] = _idx


def one_hot(seq):
    """Convert an amino acid sequence to a PyTorch tensor of one-hot vectors

    Each amino acid is represented by a length 20 vector with a single 1 and
    19 0's Inputing a sequence with a nono-canonical amino acid letter will
    cause the program to exit.

    E.g. Glutamic acid (E) is encoded: [0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]

    Parameters
    ----------
    seq : str
            An uppercase sequence of amino acids (single letter code)

    Returns
    -------
    torch.IntTensor
            a PyTorch tensor representing the encoded sequence
    """
    # make sequence uppercase
    seq = seq.upper()

    # map every character to its column index in a single vectorized gather.
    # non-ASCII characters are coerced to '?' (0x3f) which is not a valid amino
    # acid and therefore maps to -1, triggering the same error path below.
    codes = np.frombuffer(seq.encode('ascii', 'replace'), dtype=np.uint8)
    cols = _AA_TO_IDX[codes]

    # if any character was not a canonical amino acid, raise on the first offender
    invalid = cols < 0
    if invalid.any():
        raise ValueError('Invalid amino acid detected: ' + seq[int(np.argmax(invalid))])

    # float32 (not float64): the networks run in float32 and the MPS backend
    # does not support float64, so encoding directly as float32 keeps every
    # device path (cpu/cuda/mps) working and halves the memory of the encoding.
    m = np.zeros((len(seq), 20), dtype=np.float32)
    m[np.arange(len(seq)), cols] = 1
    return torch.from_numpy(m)

