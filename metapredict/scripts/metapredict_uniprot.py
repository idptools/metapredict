#!/usr/bin/env python

# executing script allowing direct input of a sequence in command line and getting graphed disorder values back
# import stuff for making CLI

import os
import argparse

from metapredict.metapredict_exceptions import MetapredictError
import metapredict as meta

def main():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Predict intrinsic disorder from a UniProt accession number.')

    parser.add_argument('uniprot', help='The uniprot accession.')

    parser.add_argument('-D', '--dpi', default=150, type=int, metavar='DPI',
                        help='Optional. Set DPI to change resolution of output graphs. Default is 150.')

    parser.add_argument('-o', '--output-file', const='USE_DEFAULT', help='Filename for where to save the returned graph. \
    The can included file extension, which in turn defines the filetype (pdf, png, jpg etc.) Note if no filename is included then \
    the -o acts as a flag and the file will be saved as the Uniprot ID', nargs='?')
    
    parser.add_argument('-p', '--pLDDT', action='store_true', help='Optional. Use this flag to include AlphaFold2 confidence scores in the graph.')                        

    parser.add_argument('-t', '--title', help='Title to put on graph')

    parser.add_argument('-l', '--legacy', action='store_true', help='Optional. Use this flag to use the original legacy version of metapredict.')

    args = parser.parse_args()

    # see if to include confidence scores
    if args.pLDDT == True:
        pLDDT_scores = True
    else:
        pLDDT_scores = False
    
    if args.legacy:
        use_legacy=True
    else:
        use_legacy=False


    # set title
    if args.title:
        graph_title = args.title
    else:
        graph_title = f'Disorder for {args.uniprot:s}'


    # if we don't want to save...
    if args.output_file is None:
        try:
            meta.graph_disorder_uniprot(args.uniprot, title=graph_title, pLDDT_scores=pLDDT_scores, DPI=args.dpi, legacy=use_legacy)
        except MetapredictError as e:
            print(e)
            exit(1)

    # else we do want to save
    else:
        
        if args.output_file == 'USE_DEFAULT':
            outname = f'{args.uniprot:s}.png'
        else:
            outname = args.output_file

        meta.graph_disorder_uniprot(args.uniprot, title=graph_title, pLDDT_scores=pLDDT_scores, DPI=args.dpi, output_file=outname, legacy=use_legacy)
