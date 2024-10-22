#!/usr/bin/env python

# executing script allowing direct input of a protein name to get a graph back
# import stuff for making CLI

import os
import argparse

from metapredict.metapredict_exceptions import MetapredictError
import metapredict as meta
from metapredict.backend.uniprot_predictions import seq_from_name
from getSequence import getseq

def main():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Predict intrinsic disorder from a protein name.')

    parser.add_argument('name', nargs='+', help='Name of the protein.')

    parser.add_argument('-D', '--dpi', default=150, type=int, metavar='DPI',
                        help='Optional. Set DPI to change resolution of output graphs. Default is 150.')
    
    parser.add_argument('-p', '--pLDDT', action='store_true', help='Optional. Use this flag to include AlphaFold2 confidence scores in the graph.')                        

    parser.add_argument('-t', '--title', help='Title to put on graph')

    parser.add_argument('-l', '--legacy', action='store_true', help='Optional. Use this flag to use the original legacy version of metapredict.')

    parser.add_argument('-v', '--verbose', action='store_true', help='Optional. Use this flag to print the full uniprot ID to the terminal.')

    parser.add_argument('-s', '--silent', action='store_true', help='Optional. Use this flag to stop any printed text to the terminal.')

    args = parser.parse_args()


    # get protein name 
    if len(args.name) == 1:
        final_name = args.name[0]
        just_protein_name = True
    else:
        final_name = ''
        for i in args.name:
            final_name += i
            final_name += ' '
        final_name = final_name[:len(final_name)-1]
        just_protein_name = False

    # sequence and name
    seq_and_name = getseq(final_name)

    # get the uniprot ID
    full_uniprot_id = seq_and_name[0]

    # get sequence
    sequence = seq_and_name[1]

    # see if you should print the entire uniprot ID to the terminal
    if args.silent:
        print_uniprot=False
    else:
        print_uniprot=True

    # see if to include confidence scores
    if args.pLDDT == True:
        pLDDT_scores = True
    else:
        pLDDT_scores = False
    
    # see if using the new metapredict or metapredict-legacy
    if args.legacy:
        use_legacy=True
    else:
        use_legacy=False

    # set the title to contain the input name, the organism that was found (if possible)
    final_title = final_name


    # set title
    if args.title:
        final_title = args.title


    # figure out what to print if anything
    if print_uniprot==True:
        print(f'Graphing disorder for {full_uniprot_id}')

    # graph it
    meta.graph_disorder(sequence, title=final_title, pLDDT_scores=pLDDT_scores, DPI=args.dpi, legacy=use_legacy)
    




