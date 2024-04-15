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
    seq=seq.upper()
    
    # ONE HOT encoding per standard amino acid
    ONE_HOT = {'A': 0, 'C': 1, 'D': 2, 'E': 3, 'F': 4, 'G': 5, 'H': 6, 'I': 7, 'K': 8, 'L': 9,
                   'M': 10, 'N': 11, 'P': 12, 'Q': 13, 'R': 14, 'S': 15, 'T': 16, 'V': 17, 'W': 18, 'Y': 19}
    l = len(seq)
    m = np.zeros((l, 20))

    # try to encode, if there's an invalid amino acid, raise an exception. 
    try:
        for i in range(l):
            m[i, ONE_HOT[seq[i]]] = 1
    except:
        error_str = 'Invalid amino acid detected: ' + seq[i]
        raise ValueError(error_str)
    return torch.from_numpy(m)

