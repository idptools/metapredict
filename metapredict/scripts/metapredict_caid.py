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

    parser.add_argument('output_path', help='Path of where to save each generated .caid file.')

    parser.add_argument('version', help='The version of metapredict to use. Options are v1, v2, and v3.')

    args = parser.parse_args()

    # carry out predictions
    meta.predict_disorder_caid(input_fasta=args.data_file, output_path=args.output_path, version=args.version)