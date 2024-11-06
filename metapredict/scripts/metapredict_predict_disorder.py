#!/usr/bin/env python

# executing script for IDR predictor in command line.

# import stuff for making CLI
import os
import argparse
import sys
import metapredict as meta
from metapredict.parameters import DEFAULT_NETWORK

def main():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Generate disorder scores for all sequences in a FASTA file.')

    parser.add_argument('data_file', help='Path to fasta file containing sequences to be predicted.')

    parser.add_argument('-o', '--output-file', help='Filename for where to save the csv disorder scores. Default = disorder.csv ', default='disorder_scores.csv')

    parser.add_argument('-v', '--version', default=DEFAULT_NETWORK, help='Optional. Use this flag to specify the version of metapredict. Options are V1, V2, or V3.')                            

    parser.add_argument('--invalid-sequence-action', help="For parsing FASTA file, defines how to deal with non-standard amino acids. See https://protfasta.readthedocs.io/en/latest/read_fasta.html for details. Default='convert' ", default='convert')

    parser.add_argument('-s', '--silent', action='store_true', help='Optional. Use this flag to suppress the progress bar.')

    parser.add_argument('-d', '--device', default=None, help='Optional. Use this flag to specify device to use. Options are cpu, mps, cuda, or cuda:int, or an int specifying the index of a CUDA-enabled GPU.')

    args = parser.parse_args()

    
    if not os.path.isfile(args.data_file):
        print('Error: Could not find passed fasta file [%s]'%(args.data_file))
        sys.exit(1)

    if args.silent:
        show_progress_bar=False
    else:
        show_progress_bar=True

    # run predict disorder fasta
    try:
        meta.predict_disorder_fasta(filepath=args.data_file, 
                                    output_file = args.output_file,
                                    invalid_sequence_action=args.invalid_sequence_action,
                                    version=args.version,
                                    device=args.device,
                                    show_progress_bar=show_progress_bar)
    except Exception as e:
        print('Error durring prediction: %s'%(str(e)))
        sys.exit(1)

    if not args.silent:
        print('Predictions saved to: %s'%(os.path.abspath(args.output_file)))




