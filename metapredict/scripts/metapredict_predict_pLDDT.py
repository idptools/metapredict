#!/usr/bin/env python

# executing script for AF2 pLDDT predictor in command line.

# import stuff for making CLI
import os
import argparse

import metapredict as meta


def main():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Generate AlphaFold2 pLDDT scores for all sequences in a FASTA file.')

    parser.add_argument('data_file', help='Path to fasta file containing sequences to be predicted.')

    parser.add_argument('-o', '--output-file', help='Filename for where to save the csv pLDDT scores. Default = pLDDT_scores.csv ', default='pLDDT_scores.csv')

    parser.add_argument('--invalid-sequence-action', help="For parsing FASTA file, defines how to deal with non-standard amino acids. See https://protfasta.readthedocs.io/en/latest/read_fasta.html for details. Default='convert' ", default='convert')

    args = parser.parse_args()

    
    if not os.path.isfile(args.data_file):
        print(f'Error: Could not find passed fasta file [{args.data_file:s}]')


    # run predict disorder fasta
    meta.predict_pLDDT_fasta(filepath=args.data_file, 
                                output_file = args.output_file,
                                invalid_sequence_action=args.invalid_sequence_action)
