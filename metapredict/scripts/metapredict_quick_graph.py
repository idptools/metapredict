#!/usr/bin/env python

# executing script allowing direct input of a sequence in command line and getting graphed disorder values back
# import stuff for making CLI

import argparse
import metapredict as meta

VALID_AA = ['A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y']

def main():
    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Predict intrinsic disorder of amino acid sequences.')
    parser.add_argument('sequence', help='The amino acid sequence to predict disorder for.')
    parser.add_argument('-l', '--legacy', action='store_true', help='Optional. Use this flag to use the original legacy version of metapredict.')
    parser.add_argument('-D', '--dpi', default=150, type=int, metavar='DPI',
                        help='Optional. Set DPI to change resolution of output graphs. Default is 150.')
    parser.add_argument('-p', '--pLDDT', action='store_true', help='Optional. Use this flag to include AlphaFold2 pLDDT scores in the graph.')                        


    args = parser.parse_args()


    if args.legacy:
        use_legacy=True
    else:
        use_legacy=False

    if args.pLDDT == True:
        pLDDT_scores = True
    else:
        pLDDT_scores = False

    # display the disorder of the sequence
    meta.graph_disorder(sequence=args.sequence.upper(), DPI=args.dpi, pLDDT_scores=pLDDT_scores, legacy=use_legacy)
