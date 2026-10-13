#!/usr/bin/env python

# executing script allowing direct input of a sequence in command line and getting graphed disorder values back
# import stuff for making CLI

import os
import sys
import argparse

import metapredict as meta
from getSequence import getseq
from metapredict.parameters import DEFAULT_NETWORK, DEFAULT_NETWORK_PLDDT
from metapredict.scripts import exit_if_invalid_version

def main():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Predict intrinsic disorder from a UniProt accession number.')

    parser.add_argument('uniprot', help='The uniprot accession.')

    parser.add_argument('-D', '--dpi', default=150, type=int, metavar='DPI',
                        help='Optional. Set DPI to change resolution of output graphs. Default is 150.')

    parser.add_argument('-o', '--output-file', const='USE_DEFAULT', help='Filename for where to save the returned graph. \
    This can include a file extension, which in turn defines the filetype (pdf, png, jpg etc.) Note if no filename is included then \
    the -o acts as a flag and the file will be saved as the Uniprot ID', nargs='?')
    
    parser.add_argument('-p', '--pLDDT', action='store_true', help='Optional. Use this flag to include AlphaFold2 confidence scores in the graph.')                        

    parser.add_argument('-t', '--title', help='Title to put on graph')

    parser.add_argument('-v', '--version', default=DEFAULT_NETWORK, help='Optional. Use this flag to specify the version of metapredict. Options are V1, V2, or V3.')                            

    parser.add_argument('-pv', '--pLDDT_version', default=DEFAULT_NETWORK_PLDDT, help='Optional. Use this flag to specify the version of pLDDT predictor. Options are 1 or 2.')                            

    parser.add_argument('-s', '--silent', action='store_true', help='Optional. Use this flag to suppress any printed output.')

    args = parser.parse_args()

    exit_if_invalid_version(args.version, 'disorder', '--version')
    exit_if_invalid_version(args.pLDDT_version, 'pLDDT', '--pLDDT_version')

    # see if to include confidence scores
    if args.pLDDT == True:
        pLDDT_scores = True
    else:
        pLDDT_scores = False


    # set title
    if args.title:
        graph_title = args.title
    else:
        graph_title = f'Disorder for {args.uniprot:s}'

    # get sequence. getSequence raises an exception if UniProt doesn't return one, which
    # happens for an invalid or unknown accession, or if UniProt can't be reached
    try:
        name_and_seq = getseq(args.uniprot, uniprot_id=True)
    except Exception as e:
        print(f'Error: Could not get a sequence from UniProt for accession [{args.uniprot}] ({e}). Check that the accession is valid and that you are connected to the internet. If you would like to predict disorder using a name, please use metapredict-name.', file=sys.stderr)
        sys.exit(1)

    # older versions of getSequence return the Uniprot API's error messages instead of raising an exception
    if name_and_seq[0]=='Error messages':
        # if the problem was an invalid accession, try pointing person to use metapredict-name command
        if name_and_seq[1]=="The 'accession' value has invalid format. It should be a valid UniProtKB accession":
            error_message='The metapredict-uniprot command requires a Uniprot ID to work. It appears the Uniprot ID you input is not valid. If you would like to predict disorder using a name, please use metapredict-name.'
        else:
            # otherwise return error messages from Uniprot API
            error_message=f'{name_and_seq[0]}: {name_and_seq[1:]}'
        print(f'Error: {error_message}', file=sys.stderr)
        sys.exit(1)

    # if we don't want to save...
    if args.output_file is None:
        try:
            meta.graph_disorder(name_and_seq[1], 
                                title=graph_title, 
                                pLDDT_scores=pLDDT_scores, 
                                DPI=args.dpi, 
                                version=args.version,
                                pLDDT_version=args.pLDDT_version)
        except Exception as e:
            print(f'Error: Could not graph disorder for [{args.uniprot}]: {e}', file=sys.stderr)
            sys.exit(1)

    # else we do want to save
    else:
        
        if args.output_file == 'USE_DEFAULT':
            outname = f'{args.uniprot:s}.png'
        else:
            outname = args.output_file

        try:
            meta.graph_disorder(name_and_seq[1], 
                                    title=graph_title, 
                                    pLDDT_scores=pLDDT_scores, 
                                    DPI=args.dpi, 
                                    output_file=outname, 
                                    version=args.version,
                                    pLDDT_version=args.pLDDT_version)
        except Exception as e:
            print(f'Error: Could not graph disorder for [{args.uniprot}]: {e}', file=sys.stderr)
            sys.exit(1)
        if not args.silent:
            print('Saving predictions to: %s'%(os.path.abspath(outname)))



if __name__ == "__main__":
    main()
