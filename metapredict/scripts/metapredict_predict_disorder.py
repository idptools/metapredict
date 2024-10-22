#!/usr/bin/env python

# executing script for IDR predictor in command line.

# import stuff for making CLI
import os
import argparse


import metapredict as meta


def main():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Generate disorder scores for all sequences in a FASTA file.')

    parser.add_argument('data_file', help='Path to fasta file containing sequences to be predicted.')

    parser.add_argument('-o', '--output-file', help='Filename for where to save the csv disorder scores. Default = disorder.csv ', default='disorder_scores.csv')

    parser.add_argument('-l', '--legacy', action='store_true', help='Optional. Use this flag to use the original legacy version of metapredict.')

    parser.add_argument('--invalid-sequence-action', help="For parsing FASTA file, defines how to deal with non-standard amino acids. See https://protfasta.readthedocs.io/en/latest/read_fasta.html for details. Default='convert' ", default='convert')

    args = parser.parse_args()

    
    if not os.path.isfile(args.data_file):
        print('Error: Could not find passed fasta file [%s]'%(args.data_file))

    if args.legacy:
        use_legacy=True
    else:
        use_legacy=False

    # run predict disorder fasta
    meta.predict_disorder_fasta(filepath=args.data_file, 
                                output_file = args.output_file,
                                invalid_sequence_action=args.invalid_sequence_action,
                                legacy=use_legacy)
