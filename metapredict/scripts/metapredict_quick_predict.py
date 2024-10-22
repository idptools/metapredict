#!/usr/bin/env python

# executing script allowing direct input of a sequence in command line and getting disorder values back
# import stuff for making CLI

import argparse
import metapredict as meta

def main():
    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Predict intrinsic disorder of amino acid sequences.')
    parser.add_argument('sequence', help='The amino acid sequence to predict disorder for.')

    parser.add_argument('-l', '--legacy', action='store_true', help='Optional. Use this flag to use the original legacy version of metapredict.')

    args = parser.parse_args()

    if args.legacy:
        use_legacy=True
    else:
        use_legacy=False

    # print the sequence
    print(str(meta.predict_disorder(sequence=args.sequence, normalized=True, legacy=use_legacy))[1:-1])
