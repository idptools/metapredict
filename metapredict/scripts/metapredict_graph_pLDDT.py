#!/usr/bin/env python

# executing script for AF2 confidence predictor in command line.

# import stuff for making CLI
import os
import sys
import argparse
import csv

import protfasta

from metapredict import meta
from metapredict.parameters import DEFAULT_NETWORK_PLDDT
from metapredict.scripts import exit_if_no_sequences, exit_if_invalid_version


def main():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Generate Alphafold2 pLDDT score figures for all sequences in a FASTA file.')

    parser.add_argument('data_file', help='Path to fasta file containing sequences to be predicted.')

    parser.add_argument('-D', '--dpi', default=150, type=int, help='Optional. Set DPI to change resolution of output graphs. Default is 150.')                        

    parser.add_argument('--filetype', default='png', help='Define the possible output filetype. Valid options are png, pdf, jpg. Default is png')
                        
    parser.add_argument('-o', '--output-directory', help='Directory for where to save the returned graphs. If not provided the program generates a default output directory called pLDDT_out and files are written there.')

    parser.add_argument('--indexed-filenames', help='Flag which, if set to true, means files will be indexed with a leading unique integer starting at 1.', action='store_true')

    parser.add_argument('--invalid-sequence-action', help="For parsing FASTA file, defines how to deal with non-standard amino acids. See https://protfasta.readthedocs.io/en/latest/read_fasta.html for details. Default='convert'", default='convert')

    parser.add_argument('-v', '--pLDDT-version', default=DEFAULT_NETWORK_PLDDT, help='Optional. Use this flag to specify the version of the pLDDT predictor. Options are V1 or V2.')


    args = parser.parse_args()

    exit_if_invalid_version(args.pLDDT_version, 'pLDDT', '--pLDDT-version')

    if not os.path.isfile(args.data_file):
        print(f'Error: Could not find passed fasta file [{args.data_file:s}]', file=sys.stderr)
        sys.exit(1)

    # stop if there is nothing to predict, rather than writing empty output. The whole file
    # is read now so that a bad record anywhere in it stops the tool before any graphs are made
    exit_if_no_sequences(args.data_file, args.invalid_sequence_action, read_whole_file=True)

    DPI = args.dpi

    if args.output_directory is None:
        try:
            # make dir
            os.makedirs('pLDDT_out', exist_ok=True)
        except Exception:
            print('Error: Unable to make default outdirectory (pLDDT_out)', file=sys.stderr)
            sys.exit(1)

        outdir = 'pLDDT_out'
    else:
        outdir = args.output_directory

    # run graph_pLDDT_fasta. For more info, see the graph_pLDDT_fasta function in meta.py.
    try:
        meta.graph_pLDDT_fasta(filepath=args.data_file, 
                                  DPI=args.dpi,
                                  output_dir=outdir,
                                  output_filetype=args.filetype,
                                  indexed_filenames=args.indexed_filenames,
                                  pLDDT_version=args.pLDDT_version,
                                  invalid_sequence_action=args.invalid_sequence_action)
    except Exception as e:
        print('Error while making graphs: %s'%(str(e)), file=sys.stderr)
        sys.exit(1)
                              
                              
                              


if __name__ == "__main__":
    main()
