"""

Empty init file in case you choose a package besides PyTest such as Nose which may look for such a rfile

"""

import os
import numpy as np

# Scratch directory for files written by the tests. This is anchored to the
# tests directory itself (not the current working directory) so that importing
# the tests can never clear an unrelated 'output/' folder elsewhere on disk.
TEST_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')


VALID_AA = ['A',
            'C',
            'D',
            'E',
            'F',
            'G',
            'H',
            'I',
            'K',
            'L',
            'M',
            'N',
            'P',
            'Q',
            'R',
            'S',
            'T',
            'V',
            'W',
            'Y']

def build_seq(min_count=10,max_count=50):

    # how many residues
    n_res = np.random.randint(4,20)

    s = ''
    for i in range(n_res):
        aa_idx = np.random.randint(0,20)
        s = s + VALID_AA[aa_idx]*np.random.randint(min_count, max_count)
        
    s = list(s)
    np.random.shuffle(s)
    s = "".join(s)
    return s

os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

# clear out files left over from a previous run (sub-directories are left alone)
for filename in os.listdir(TEST_OUTPUT_DIR):
    filepath = os.path.join(TEST_OUTPUT_DIR, filename)
    if os.path.isfile(filepath):
        os.remove(filepath)
