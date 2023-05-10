"""

Empty init file in case you choose a package besides PyTest such as Nose which may look for such a rfile

"""

import os
import numpy as np


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



dir = 'output/'
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))

    
