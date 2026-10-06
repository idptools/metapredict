#!/usr/bin/env python

# executing script for IDR predictor in command line.

# import stuff for making CLI
import os
import sys
import argparse
import protfasta

from metapredict.parameters import DEFAULT_NETWORK
from metapredict.scripts import exit_if_no_sequences, exit_if_invalid_version
import metapredict as meta

# --threshold is a disorder score, so it must lie in the range disorder scores take
MIN_DISORDER_THRESHOLD = 0.0
MAX_DISORDER_THRESHOLD = 1.0

def main():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Predict IDRs for all sequences in a FASTA file.')

    parser.add_argument('data_file', help='Path to fasta file containing sequences to be predicted.')

    parser.add_argument('-o', '--output-file', help='Filename for where to save the output file. Defaults = idrs.fasta (if mode=fasta) and shephard_idrs.tsv otherwise')

    parser.add_argument('-v', '--version', default=DEFAULT_NETWORK, help='Optional. Use this flag to specify the version of metapredict. Options are V1, V2, or V3.')                            

    parser.add_argument('--invalid-sequence-action', help="For parsing FASTA file, defines how to deal with non-standard amino acids. See https://protfasta.readthedocs.io/en/latest/read_fasta.html for details. Default='convert' ", default='convert')

    parser.add_argument('--mode', help='Defines the mode in which IDRs are reported. Options are currently: "fasta", "shephard-domains", "shephard-domains-uniprot". By default this generates a FASTA file with header format that matches the input file with an additional set of fields that are "IDR_START=$START  IDR_END=$END" where $START and $END are the start and end positions of each IDR (indexing from 0, as in Python slice notation). If mode is set to shephard-domains then a SHEPHARD-compliant domains file is generated (where indexing starts at 1 to match protein numbering). If shephard-domains-uniprot the uniprot ID is extracted from the header assuming standard uniprot formatting (where indexing starts at 1 to match protein numbering). Default = fasta', default='fasta')

    parser.add_argument('--threshold', type=float, help='Defines the threshold used to define a region as disordered or not. Default=0.42 for v1, 0.5 for v2 and v3.', default=None)
    
    parser.add_argument('--verbose', help='If included then prints out status updates', action='store_true')
    
    parser.add_argument('-s', '--silent', action='store_true', help='Optional. Use this flag to suppress the progress bar.')

    parser.add_argument('-d', '--device', default=None, help='Optional. Use this flag to specify device to use. Options are cpu, mps, cuda, or cuda:int, or an int specifying the index of a CUDA-enabled GPU.')

    args = parser.parse_args()

    if args.mode not in ['fasta', 'shephard-domains','shephard-domains-uniprot', ]:
        print(f"Error: --mode must be set to one of 'fasta', 'shephard-domains', or 'shephard-domains-uniprot' (got '{args.mode}')", file=sys.stderr)
        sys.exit(1)

    # check the threshold here so a bad value gives a clear error before any work is done
    # (written as 'not inside the range' so that nan is rejected too)
    if args.threshold is not None:
        if not (MIN_DISORDER_THRESHOLD <= args.threshold <= MAX_DISORDER_THRESHOLD):
            print(f'Error: --threshold must be between {MIN_DISORDER_THRESHOLD} and {MAX_DISORDER_THRESHOLD} (got {args.threshold})', file=sys.stderr)
            sys.exit(1)

    exit_if_invalid_version(args.version, 'disorder', '--version')

    if args.output_file is None:
        if args.mode == 'fasta':
            outfile_name = 'idrs.fasta'
        else:
            outfile_name = 'shephard_idrs.tsv'

    else:
        outfile_name = args.output_file

    
    if not os.path.isfile(args.data_file):
        print(f'Error: Could not find passed fasta file [{args.data_file:s}]', file=sys.stderr)
        sys.exit(1)

    # stop if there is nothing to predict, rather than writing an empty file
    exit_if_no_sequences(args.data_file, args.invalid_sequence_action)

    # read in sequences
    try:
        sequences = protfasta.read_fasta(args.data_file, 
                                        invalid_sequence_action=args.invalid_sequence_action)
    except Exception as e:
        print('Error reading fasta file: %s'%(str(e)), file=sys.stderr)
        sys.exit(1)

    # shephard-domains-uniprot takes the UniProt ID from between the first two '|' in each
    # header, so check every header has one before predicting or writing anything
    if args.mode == 'shephard-domains-uniprot':
        for header in sequences:
            if '|' not in header:
                print(f'Error parsing header line: {header} (could not split on "|" characters)', file=sys.stderr)
                sys.exit(1)
    
    if args.verbose:
        print('Read in FASTA file')

    if args.silent:
        show_progress_bar=False
    else:
        show_progress_bar=True

    if args.verbose:
        print('Predicting disorder')

    # if using non-legacy then we use batch mode and request return_domains
    try:
        idrs = meta.predict_disorder(sequences, 
                                    version=args.version, 
                                    device=args.device,
                                    return_domains=True, 
                                    disorder_threshold=args.threshold, 
                                    show_progress_bar=show_progress_bar)
    except Exception as e:
        print('Error during prediction: %s'%(str(e)), file=sys.stderr)
        sys.exit(1)

    if not args.silent:
        print('Saving predictions to: %s'%(os.path.abspath(outfile_name)))


    # if the return type is a FASTA file we want to write 
    if args.mode == 'fasta':

        return_dictionary = {}    

        # for each protein
        for s in idrs:

            # calculate number of IDRs
            n_idrs = len(idrs[s].disordered_domains)

            for idx in range(n_idrs):

                idr_start = idrs[s].disordered_domain_boundaries[idx][0]
                idr_end   = idrs[s].disordered_domain_boundaries[idx][1]
                idr_seq   = idrs[s].disordered_domains[idx]
                
                return_dictionary[f'{s} IDR_START={idr_start} IDR_END={idr_end}'] =  idr_seq
                        
        protfasta.write_fasta(return_dictionary, outfile_name)

    # if the return type is a SHEPHARD-compliant Domains file
    elif args.mode == 'shephard-domains':
        # use a context manager so the file is always flushed and closed
        with open(outfile_name, 'w') as fh:

            # for each protein
            for s in idrs:

                # calculate number of IDRs
                n_idrs = len(idrs[s].disordered_domains)

                for idx in range(n_idrs):

                    idr_start = idrs[s].disordered_domain_boundaries[idx][0] + 1
                    idr_end   = idrs[s].disordered_domain_boundaries[idx][1]

                    fh.write(f'{s}\t{idr_start}\t{idr_end}\tIDR\n')

    elif args.mode == 'shephard-domains-uniprot':
        # use a context manager so the file is always flushed and closed
        with open(outfile_name, 'w') as fh:

            # for each protein
            for s in idrs:

                # every header was checked for a '|' before predicting
                uid = s.split('|')[1]

                # calculate number of IDRs
                n_idrs = len(idrs[s].disordered_domains)

                for idx in range(n_idrs):
                    idr_start = idrs[s].disordered_domain_boundaries[idx][0] + 1
                    idr_end   = idrs[s].disordered_domain_boundaries[idx][1]

                    fh.write(f'{uid}\t{idr_start}\t{idr_end}\tIDR\n')

        



if __name__ == "__main__":
    main()
