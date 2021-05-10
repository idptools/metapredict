# code for pulling down uniprot sequence for predictions
import os
import sys
import argparse
import urllib3

import csv
import protfasta

from metapredict import meta

def fetch_sequence(uniprot_id):
    """
    Function that returns the amino acid sequence by polling UniProt.com
    
    Parameters
    --------------
    uniprot_id : str
        Uniprot accession number

    Returns
    -----------
    
    """

    http = urllib3.PoolManager()
    r = http.request('GET', 'https://www.uniprot.org/uniprot/%s.fasta'%(uniprot_id))
    
    s = "".join(str(r.data).split('\\n')[1:]).replace("'","")


    if s.find('Sorry') > -1:
        return None

    return s


