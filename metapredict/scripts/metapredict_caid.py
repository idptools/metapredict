#!/usr/bin/env python

# executing script for IDR predictor in command line.

# import stuff for making CLI
import os
import argparse
import metapredict as meta


def _fixed_cutoff_type(value):
    """argparse type that validates --use-fixed-cutoff is a float in [0, 1]."""
    try:
        fval = float(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError(
            f"--use-fixed-cutoff must be a float between 0 and 1 (got {value!r})")
    if fval < 0.0 or fval > 1.0:
        raise argparse.ArgumentTypeError(
            f"--use-fixed-cutoff must be between 0 and 1 (got {fval})")
    return fval


def main():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Generate disorder scores for all sequences in a FASTA file.')

    parser.add_argument('data_file', help='Path to fasta file containing sequences to be predicted.')

    parser.add_argument('output_path', help='Path of where to save each generated .caid file.')

    parser.add_argument('version', help='The version of metapredict to use. Options are v1, v2, and v3.')

    parser.add_argument(
        '--use-fixed-cutoff',
        nargs='?',
        const=0.5,
        default=None,
        type=_fixed_cutoff_type,
        metavar='CUTOFF',
        help=('If provided, use a simple per-residue disorder-score cutoff to '
              'assign the binary IDR vs. folded classification in the CAID '
              'output instead of the default domain-based approach. Optionally '
              'pass a float between 0 and 1 to set the cutoff value '
              '(default 0.5 if the flag is given with no value).'),
    )

    args = parser.parse_args()

    # carry out predictions
    meta.predict_disorder_caid(
        input_fasta=args.data_file,
        output_path=args.output_path,
        version=args.version,
        use_fixed_cutoff=args.use_fixed_cutoff,
    )