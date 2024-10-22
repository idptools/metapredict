#!/usr/bin/env python

# executing script for AF2 confidence predictor in command line.

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
    parser = argparse.ArgumentParser(description='Generate Alphafold2 pLDDT score figures for all sequences in a FASTA file.')

    parser.add_argument('data_file', help='Path to fasta file containing sequences to be predicted.')

    parser.add_argument('-D', '--dpi', default=150, type=int, help='Optional. Set DPI to change resolution of output graphs. Default is 150.')                        

    parser.add_argument('--filetype', default='png', help='Define the possible output filetype. Valid options are png, pdf, jpg. Default is png')
                        
    parser.add_argument('-o', '--output-directory', help='Directory for where to save the returned graphs. If not provided the program generates a default output directory called disorder_out and files are writte there.')

    parser.add_argument('--indexed-filenames', help='Flag which, if set to true, means files will be indexed with a leading unique integer start at 1.', action='store_true')

    parser.add_argument('--invalid-sequence-action', help="For parsing FASTA file, defines how to deal with non-standard amino acids. See https://protfasta.readthedocs.io/en/latest/read_fasta.html for details. Default='convert'", default='convert')



    args = parser.parse_args()

    DPI = args.dpi

    if args.output_directory is None:
        try:
            # make dir
            os.makedirs('pLDDT_out', exist_ok=True)
        except Exception:
            print('Error: Unable to make default outdirectory (pLDDT_out)')
            exit(1)

        outdir = 'pLDDT_out'
    else:
        outdir = args.output_directory

    # run graph_disorder_fasta. For more info, see the graph_disorder_fasta function in meta.py.
    meta.graph_pLDDT_fasta(filepath=args.data_file, 
                              DPI=args.dpi,
                              output_dir=outdir,
                              output_filetype=args.filetype,
                              indexed_filenames=args.indexed_filenames)
                              
                              
                              
