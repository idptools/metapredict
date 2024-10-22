#!/usr/bin/env python

# executing script for IDR predictor in command line.

# import stuff for making CLI
import os
import argparse
import protfasta

from metapredict.meta import predict_disorder_batch
import metapredict as meta

def main():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Predict IDRs for all sequences in a FASTA file.')

    parser.add_argument('data_file', help='Path to fasta file containing sequences to be predicted.')

    parser.add_argument('-o', '--output-file', help='Filename for where to save the outputfile. Defaults = idrs.fasta (if mode=fasta) and shephard_idrs.tsv otherwise')

    parser.add_argument('-l', '--legacy', action='store_true', help='Optional. Use this flag to use the original legacy version of metapredict.')

    parser.add_argument('--invalid-sequence-action', help="For parsing FASTA file, defines how to deal with non-standard amino acids. See https://protfasta.readthedocs.io/en/latest/read_fasta.html for details. Default='convert' ", default='convert')

    parser.add_argument('--mode', help='Defines the mode in which IDRs are reported. Options are currently: "fasta", "shephard-domains", "shephard-domains-uniprot". By default this generates a FASTA file with header format that matches the input file with an additional set of fields that are "IDR_START=$START  IDR_END=$END" where $START and $END are the starting and ending IDRs (indexing from 0, as in Python slice notation). If mode is set to shephard-domains than a SHEPHAD-compliant domains file is generated (where indexing starts at 1 to match protein numbering). If shephard-domains-uniprot the uniprot ID is extracted from the header assuming standard uniprot formatting (where indexing starts at 1 to match protein numbering). Default = fasta', default='fasta')

    parser.add_argument('--threshold', help='Defines the threshold used to define a region as disordered or not. Default=0.42 which is recommended.', default=0.42, type=float)
    parser.add_argument('--verbose', help='If included then prints out status updates', action='store_true')

    args = parser.parse_args()

    if args.mode not in ['fasta', 'shephard-domains','shephard-domains-uniprot', ]:
        raise Exception("--mode must be set to one of 'fasta', 'shephard-domains', or 'shephard-domains-uniprot'")

    if args.output_file is None:
        if args.mode == 'fasta':
            outfile_name = 'idrs.fasta'
        else:
            outfile_name = 'shephard_idrs.tsv'

    else:
        outfile_name = args.output_file
    
    if args.legacy:
        use_legacy = True
        threshold_val = args.threshold


    else:
        use_legacy=False
        
        # if not using legacy and the default legacy value is still being used, adjust it to 0.5.
        if args.threshold == 0.42:
            threshold_val = 0.5

        # if the user sets their own threshold value that isn't 0.42, keep it.
        else:
            threshold_val = args.threshold
    
    if not os.path.isfile(args.data_file):
        print(f'Error: Could not find passed fasta file [{args.data_file:s}]')

    # read in sequences
    sequences = protfasta.read_fasta(args.data_file, invalid_sequence_action=args.invalid_sequence_action)
    if args.verbose:
        print('Read in FASTA file')

    idrs = {}

    if use_legacy is True:
        
        c = 0
        n_seqs = len(sequences)
        for s in sequences:
            c = c + 1
            idrs[s] = meta.predict_disorder_domains(sequences[s], disorder_threshold=threshold_val, legacy=use_legacy)

            if n_seqs > 500:
                if args.verbose:
                    if c % 500 == 0:
                        print(f'On {c:d} of {n_seqs:d}')

    else:
        # if using non-legacy then we use batch mode and request return_domains
        idrs = predict_disorder_batch(sequences, return_domains=True, disorder_threshold=threshold_val)

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
        fh = open(outfile_name, 'w')

        # for each protein
        for s in idrs:

            # calculate number of IDRs
            n_idrs = len(idrs[s].disordered_domains)

            for idx in range(n_idrs):

                idr_start = idrs[s].disordered_domain_boundaries[idx][0] + 1
                idr_end   = idrs[s].disordered_domain_boundaries[idx][1]

                fh.write(f'{s}\t{idr_start}\t{idr_end}\tIDR\n')

    elif args.mode == 'shephard-domains-uniprot':
        fh = open(outfile_name, 'w')

        # for each protein
        for s in idrs:

            try:
                uid = s.split('|')[1]
            except IndexError:
                print(f'Error parsing header line: {s}\nCould not split on "|" characters.')
                exit(1)
            
            # calculate number of IDRs
            n_idrs = len(idrs[s].disordered_domains)

            for idx in range(n_idrs):                
                idr_start = idrs[s].disordered_domain_boundaries[idx][0] + 1
                idr_end   = idrs[s].disordered_domain_boundaries[idx][1]

                fh.write(f'{uid}\t{idr_start}\t{idr_end}\tIDR\n')
                
        

