#!/usr/bin/env python

# executing script for IDR predictor in command line.

# import stuff for making CLI
import os
import sys
import argparse
import metapredict as meta
from metapredict.scripts import exit_if_no_sequences, exit_if_invalid_version

# predict_disorder_caid() always reads the FASTA file with this --invalid-sequence-action
CAID_INVALID_SEQUENCE_ACTION = 'convert'


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

    exit_if_invalid_version(args.version, 'disorder', 'version')

    if not os.path.isfile(args.data_file):
        print(f'Error: Could not find passed fasta file [{args.data_file:s}]', file=sys.stderr)
        sys.exit(1)

    # stop if there is nothing to predict, rather than writing empty output. The whole file
    # is read now so that a bad record anywhere in it gives the same clear error
    exit_if_no_sequences(args.data_file, CAID_INVALID_SEQUENCE_ACTION, read_whole_file=True)

    # carry out predictions
    try:
        meta.predict_disorder_caid(
            input_fasta=args.data_file,
            output_path=args.output_path,
            version=args.version,
            use_fixed_cutoff=args.use_fixed_cutoff,
        )
    except Exception as e:
        print('Error during prediction: %s'%(str(e)), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
