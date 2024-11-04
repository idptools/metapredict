#!/usr/bin/env python

# executing script allowing direct input of a sequence in command line and getting graphed disorder values back
# import stuff for making CLI

import argparse
import metapredict as meta
from metapredict.parameters import DEFAULT_NETWORK

VALID_AA = ['A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y']

def main():
    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Predict intrinsic disorder of amino acid sequences.')
    parser.add_argument('sequence', help='The amino acid sequence to predict disorder for.')
    parser.add_argument('-v', '--version', default=DEFAULT_NETWORK, help='Optional. Use this flag to specify the version of metapredict. Options are V1, V2, or V3.')                            
    parser.add_argument('-D', '--dpi', default=150, type=int, metavar='DPI',
                        help='Optional. Set DPI to change resolution of output graphs. Default is 150.')
    parser.add_argument('-p', '--pLDDT', action='store_true', help='Optional. Use this flag to include AlphaFold2 pLDDT scores in the graph.')                        

    args = parser.parse_args()

    if args.pLDDT == True:
        pLDDT_scores = True
    else:
        pLDDT_scores = False

    # display the disorder of the sequence
    meta.graph_disorder(sequence=args.sequence.upper(), DPI=args.dpi, pLDDT_scores=pLDDT_scores, version=args.version)
