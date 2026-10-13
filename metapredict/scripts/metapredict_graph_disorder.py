#!/usr/bin/env python

# executing script for IDR predictor in command line.

# import stuff for making CLI
import os
import sys
import argparse
import csv

import protfasta

from metapredict import meta
from metapredict.parameters import DEFAULT_NETWORK, DEFAULT_NETWORK_PLDDT
from metapredict.scripts import exit_if_no_sequences, exit_if_invalid_version

# --disorder-threshold is a disorder score, so it must lie in the range disorder scores take
MIN_DISORDER_THRESHOLD = 0.0
MAX_DISORDER_THRESHOLD = 1.0

def main():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Generate disorder figures for all sequences in a FASTA file.')

    parser.add_argument('data_file', help='Path to fasta file containing sequences to be predicted.')

    parser.add_argument('-D', '--dpi', default=150, type=int, help='Optional. Set DPI to change resolution of output graphs. Default is 150.')                        

    parser.add_argument('-p', '--pLDDT', action='store_true', help='Optional. Use this flag to include AlphaFold2 pLDDT scores in the graph.')                        

    parser.add_argument('-v', '--version', default=DEFAULT_NETWORK, help='Optional. Use this flag to specify the version of metapredict. Options are 1, 2, or 3.')                            

    parser.add_argument('-pv', '--pLDDT_version', default=DEFAULT_NETWORK_PLDDT, help='Optional. Use this flag to specify the version of pLDDT predictor. Options are 1 or 2.')                            

    parser.add_argument('--filetype', default='png', help='Define the possible output filetype. Valid options are png, pdf, jpg. Default is png')
                        
    parser.add_argument('-o', '--output-directory', help='Directory for where to save the returned graphs. If not provided the program generates a default output directory called disorder_out and files are written there.')

    parser.add_argument('--indexed-filenames', help='Flag which, if set to true, means files will be indexed with a leading unique integer starting at 1.', action='store_true')

    parser.add_argument('--disorder-threshold', type=float, help='Defines the value plotted as a threshold line on the graph', default=None)
    
    parser.add_argument('--invalid-sequence-action', help="For parsing FASTA file, defines how to deal with non-standard amino acids. See https://protfasta.readthedocs.io/en/latest/read_fasta.html for details. Default='convert'", default='convert')


    args = parser.parse_args()

    # check the threshold here so a bad value gives a clear error before any work is done
    # (written as 'not inside the range' so that nan is rejected too)
    if args.disorder_threshold is not None:
        if not (MIN_DISORDER_THRESHOLD <= args.disorder_threshold <= MAX_DISORDER_THRESHOLD):
            print(f'Error: --disorder-threshold must be between {MIN_DISORDER_THRESHOLD} and {MAX_DISORDER_THRESHOLD} (got {args.disorder_threshold})', file=sys.stderr)
            sys.exit(1)

    exit_if_invalid_version(args.version, 'disorder', '--version')
    exit_if_invalid_version(args.pLDDT_version, 'pLDDT', '--pLDDT_version')

    if not os.path.isfile(args.data_file):
        print(f'Error: Could not find passed fasta file [{args.data_file:s}]', file=sys.stderr)
        sys.exit(1)

    # stop if there is nothing to predict, rather than writing empty output. The whole file
    # is read now so that a bad record anywhere in it stops the tool before any graphs are made
    exit_if_no_sequences(args.data_file, args.invalid_sequence_action, read_whole_file=True)
    
    if args.pLDDT == True:
        pLDDT_scores = True
    else:
        pLDDT_scores = False


    if args.output_directory is None:
        try:
            # make dir
            os.makedirs('disorder_out', exist_ok=True)
        except Exception:
            print('Error: Unable to make default outdirectory (disorder_out)', file=sys.stderr)
            sys.exit(1)

        outdir = 'disorder_out'
    else:
        outdir = args.output_directory


    # run graph_disorder_fasta. For more info, see the graph_disorder_fasta function in meta.py.
    try:
        meta.graph_disorder_fasta(filepath=args.data_file, 
                                  disorder_threshold=args.disorder_threshold,
                                  pLDDT_scores=pLDDT_scores,
                                  DPI=args.dpi,
                                  output_dir=outdir,
                                  output_filetype=args.filetype,
                                  indexed_filenames=args.indexed_filenames,
                                  version = args.version,
                                  pLDDT_version = args.pLDDT_version,
                                  invalid_sequence_action=args.invalid_sequence_action)
    except Exception as e:
        print('Error while making graphs: %s'%(str(e)), file=sys.stderr)
        sys.exit(1)
                              
                              
                              


if __name__ == "__main__":
    main()
