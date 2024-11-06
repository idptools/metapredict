#!/usr/bin/env python

# executing script allowing direct input of a sequence in command line and getting disorder values back
# import stuff for making CLI

import argparse
import metapredict as meta
from metapredict.parameters import DEFAULT_NETWORK

def main():
    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Predict intrinsic disorder of amino acid sequences.')
    parser.add_argument('sequence', help='The amino acid sequence to predict disorder for.')

    parser.add_argument('-v', '--version', default=DEFAULT_NETWORK, help='Optional. Use this flag to specify the version of metapredict. Options are V1, V2, or V3.')                            

    args = parser.parse_args()

    # print the sequence
    print(str(meta.predict_disorder(inputs=args.sequence, 
                                    normalized=True, 
                                    version=args.version, 
                                    return_numpy=False))[1:-1])
