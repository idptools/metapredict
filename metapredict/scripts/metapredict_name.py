#!/usr/bin/env python

# executing script allowing direct input of a protein name to get a graph back
# import stuff for making CLI

import os
import argparse

from metapredict.metapredict_exceptions import MetapredictError
from metapredict.parameters import DEFAULT_NETWORK, DEFAULT_NETWORK_PLDDT
import metapredict as meta
from getSequence import getseq

def main():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Predict intrinsic disorder from a protein name.')

    parser.add_argument('name', nargs='+', help='Name of the protein.')

    parser.add_argument('-D', '--dpi', default=150, type=int, metavar='DPI',
                        help='Optional. Set DPI to change resolution of output graphs. Default is 150.')
    
    parser.add_argument('-p', '--pLDDT', action='store_true', help='Optional. Use this flag to include AlphaFold2 confidence scores in the graph.')                        

    parser.add_argument('-t', '--title', help='Title to put on graph')

    parser.add_argument('-v', '--version', default=DEFAULT_NETWORK, help='Optional. Use this flag to specify the version of metapredict. Options are V1, V2, or V3.')                            

    parser.add_argument('-pv', '--pLDDT_version', default=DEFAULT_NETWORK_PLDDT, help='Optional. Use this flag to specify the version of pLDDT predictor. Options are 1 or 2.')                            

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
    

    # set the title to contain the input name, the organism that was found (if possible)
    final_title = final_name

    # set title
    if args.title:
        final_title = args.title


    # figure out what to print if anything
    if print_uniprot==True:
        print(f'Graphing disorder for {full_uniprot_id}')

    # graph it
    meta.graph_disorder(sequence, 
                        version=args.version,
                        pLDDT_version=args.pLDDT_version,
                        title=final_title, 
                        pLDDT_scores=pLDDT_scores, 
                        DPI=args.dpi)
    




