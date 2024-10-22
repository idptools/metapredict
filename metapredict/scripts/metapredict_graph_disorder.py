#!/usr/bin/env python

# executing script for IDR predictor in command line.

# import stuff for making CLI
import os
import sys
import argparse

#import csv
import csv
#import protfasta
import protfasta

#from metapredict import meta
from metapredict import meta


def main():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Generate disorder figures for all sequences in a FASTA file.')

    parser.add_argument('data_file', help='Path to fasta file containing sequences to be predicted.')

    parser.add_argument('-D', '--dpi', default=150, type=int, help='Optional. Set DPI to change resolution of output graphs. Default is 150.')                        

    parser.add_argument('-p', '--pLDDT', action='store_true', help='Optional. Use this flag to include AlphaFold2 pLDDT scores in the graph.')                        

    parser.add_argument('-l', '--legacy', action='store_true', help='Optional. Use this flag to use the original legacy version of metapredict.')                            

    parser.add_argument('--filetype', default='png', help='Define the possible output filetype. Valid options are png, pdf, jpg. Default is png')
                        
    parser.add_argument('-o', '--output-directory', help='Directory for where to save the returned graphs. If not provided the program generates a default output directory called disorder_out and files are writte there.')

    parser.add_argument('--indexed-filenames', help='Flag which, if set to true, means files will be indexed with a leading unique integer start at 1.', action='store_true')

    parser.add_argument('--disorder-threshold', help='Defines the value plotted as a theshold line on the graph', default=0.3, type=float)
    parser.add_argument('--invalid-sequence-action', help="For parsing FASTA file, defines how to deal with non-standard amino acids. See https://protfasta.readthedocs.io/en/latest/read_fasta.html for details. Default='convert'", default='convert')


    args = parser.parse_args()

    
    if args.pLDDT == True:
        pLDDT_scores = True
    else:
        pLDDT_scores = False
    

    if args.legacy:
        use_legacy=True
    else:
        use_legacy=False

    if args.output_directory is None:
        try:
            # make dir
            os.makedirs('disorder_out', exist_ok=True)
        except Exception:
            print('Error: Unable to make default outdirectory (disorder_out)')
            exit(1)

        outdir = 'disorder_out'
    else:
        outdir = args.output_directory

    # run graph_disorder_fasta. For more info, see the graph_disorder_fasta function in meta.py.
    meta.graph_disorder_fasta(filepath=args.data_file, 
                              disorder_threshold=args.disorder_threshold,
                              pLDDT_scores=pLDDT_scores,
                              DPI=args.dpi,
                              output_dir=outdir,
                              output_filetype=args.filetype,
                              indexed_filenames=args.indexed_filenames,
                              legacy = use_legacy)
                              
                              
                              
