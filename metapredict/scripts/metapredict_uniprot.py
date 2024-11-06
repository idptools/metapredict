#!/usr/bin/env python

# executing script allowing direct input of a sequence in command line and getting graphed disorder values back
# import stuff for making CLI

import os
import argparse

from metapredict.metapredict_exceptions import MetapredictError
import metapredict as meta
from getSequence import getseq
from metapredict.parameters import DEFAULT_NETWORK, DEFAULT_NETWORK_PLDDT

def main():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Predict intrinsic disorder from a UniProt accession number.')

    parser.add_argument('uniprot', help='The uniprot accession.')

    parser.add_argument('-D', '--dpi', default=150, type=int, metavar='DPI',
                        help='Optional. Set DPI to change resolution of output graphs. Default is 150.')

    parser.add_argument('-o', '--output-file', const='USE_DEFAULT', help='Filename for where to save the returned graph. \
    The can included file extension, which in turn defines the filetype (pdf, png, jpg etc.) Note if no filename is included then \
    the -o acts as a flag and the file will be saved as the Uniprot ID', nargs='?')
    
    parser.add_argument('-p', '--pLDDT', action='store_true', help='Optional. Use this flag to include AlphaFold2 confidence scores in the graph.')                        

    parser.add_argument('-t', '--title', help='Title to put on graph')

    parser.add_argument('-v', '--version', default=DEFAULT_NETWORK, help='Optional. Use this flag to specify the version of metapredict. Options are V1, V2, or V3.')                            

    parser.add_argument('-pv', '--pLDDT_version', default=DEFAULT_NETWORK_PLDDT, help='Optional. Use this flag to specify the version of pLDDT predictor. Options are 1 or 2.')                            

    parser.add_argument('-s', '--silent', action='store_true', help='Optional. Use this flag to suppress any printed output.')

    args = parser.parse_args()

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

    # get sequence
    name_and_seq = getseq(args.uniprot, uniprot_id=True)
    # if Uniprot API returns Error messages, raise an exception with the error messages.
    if name_and_seq[0]=='Error messages':
        # if the problem was an invalid accession, try pointing person to use metapredict-name command
        if name_and_seq[1]=="The 'accession' value has invalid format. It should be a valid UniProtKB accession":
            error_message=f'\n\nThe metapredict-uniprot command requires a Uniprot ID to work.\nIt appears the Uniprot ID you input is not valud.\nIf you would like to predict disorder using a name, please use metapredict-name.'
        else:
            # otherwise return error messages from Uniprot API
            error_message=f'\n{name_and_seq[0]}\n{name_and_seq[1:]}'
        raise MetapredictError(error_message)

    # if we don't want to save...
    if args.output_file is None:
        try:
            meta.graph_disorder(name_and_seq[1], 
                                title=graph_title, 
                                pLDDT_scores=pLDDT_scores, 
                                DPI=args.dpi, 
                                version=args.version,
                                pLDDT_version=args.pLDDT_version)
        except MetapredictError as e:
            print(e)
            exit(1)

    # else we do want to save
    else:
        
        if args.output_file == 'USE_DEFAULT':
            outname = f'{args.uniprot:s}.png'
        else:
            outname = args.output_file

        meta.graph_disorder(name_and_seq[1], 
                                title=graph_title, 
                                pLDDT_scores=pLDDT_scores, 
                                DPI=args.dpi, 
                                output_file=outname, 
                                version=args.version,
                                pLDDT_version=args.pLDDT_version)
        if not args.silent:
            print('Saving predictions to: %s'%(os.path.abspath(args.output_file)))

