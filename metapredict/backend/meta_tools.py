# various tools for checks and formatting

import re
import os
import numpy as np
import protfasta

# local imports
from metapredict.metapredict_exceptions import MetapredictError
from metapredict.backend.network_parameters import metapredict_networks, pplddt_networks


def valid_range(inval, minval, maxval):
    if inval < minval or inval > maxval:
        raise MetapredictError(f'Value {inval:1.3f} is outside of range [{minval:1.3f}, {maxval:1.3f}]')


def write_csv(input_dict, output_file):
    """
    Function that writes the scores in an input dictionary out to a standardized CVS file format.

    Parameters
    -----------
    input_dict : dict
        Dictionary where keys are headers/identifiers and values is a list of per-residue
        disorder score

    output_file : str
        Location and filename for the output file. Assumes .csv is provided.

    Returns
    --------
    None
        No return value, but writes a .csv file to disk


    """

    # try and open the file and throw exception if anything goes wrong
    try:
        fh = open(output_file, 'w')
    except Exception:
        raise MetapredictError(f'Unable to write to file destination {output_file:s}')

    # for each entry
    for idx in input_dict:

        # important otherwise commmas in FASTA headers render the CSV file unreadable!
        no_comma = idx.replace(',', ' ')
        fh.write(f'{no_comma:s}')

        # for each score write
        for score in input_dict[idx]:
            # remove any brackets
            score=str(score)
            score = score.replace('[', '')
            score = score.replace(']', '')
            fh.write(f', {score}')
        fh.write(f'\n')

    fh.close()


def valid_shaded_region(shaded_regions, n_res):
    """
    Function that ensures that the passed shaded region are readable and make sense.

    Parameters
    ------------
    shaded_regions : list of lists
        A list of lists, where sub-elements are of length 2 and contain start and end
        values for regions to be shaded. Assumes that sanity checking on positions has
        already been done. Default is None, but if there were specific regions you wanted
        to highlight this might, for example, look like shaded_regions=[[1,10],[40,50]], 
        which would shade between 1 and 10 and then between 40 and 50. This can be useful
        to either highlight specific IDRs or specific folded domains

    Returns
    ---------
    None 
        No return type but will raise various possible exceptions in a structured way if
        the shaded regions info is not parseable

    Raises
    --------
    MetapredictError

    """

    if shaded_regions is None:
        return

    # check shaded regions make sense:
    try:
        for b in shaded_regions:

            if b[0] < 1 or b[0] > n_res + 1:
                raise MetapredictError(f'Invalid start position in shaded_regions: {b[0]}')

            if b[1] < 1 or b[1] > n_res + 1:
                raise MetapredictError(f'Invalid end position in shaded_regions: {b[0]}')

    except Exception as e:
        raise MetapredictError(f'Error in parsing shaded_regions - full error below\n\n{str(e):s}')


def validate_options(option, valid_list):
    """
    Function that raises an exception if $option is not found in $valid_list.

    Parameters
    ----------
    option : str
        Option that has been passed

    valid_list : str
        List of strings which we expect $option to be one of

    Returns
    ---------
    None 
        No return type by riases MetapredictError if option not found in valid_list


    """
    if option not in valid_list:
        raise MetapredictError(f"Expected one of {str(valid_list):s} but only option passed was {option:s}")


def sanitize_filename(input_filename):
    """
    Function that removes characters from a putative filename which might be problematic
    for filesystems.

    Parameters
    ------------
    input_filename : str
        Proposed filename

    Returns
    ---------
    str
        Returns a string with the nicely formatted filename

    """

    # this regular expression replace every character not equal to a
    # WORD character (i.e. alphanumeric or underscore) with a space
    s = re.sub(r'\W+', '_', input_filename)
    return s


def get_binary_prediction(confidence_value, cutoff_value):
    '''
    function to turn a disorder sore into a binary classification
    where 1 is disordered and 0 is not disordered

    Parameters 
    -----------
    confidence_value : float
        The disorder confidence score as a float

    cutoff_value : float
        The value to use to decide whether to assign a confidence score
        with a 1 (disordered) or a 0 (not disordered). Assigns a 1 when
        the confidence_value > cutoff_value

    Returns
    -------
    binary_prediction : Int
        Returns a binary prediction

    '''
    if confidence_value >= cutoff_value:
        return 1
    else:
        return 0





def split_fasta(fasta_list, number_splits):
    '''
    function to split the dict returned from
    a fasta file read in by protfasta to make
    a specific number of dictionaries with
    approximately equal numbers of proteins. 

    Parameters
    -----------
    protfasta_fasta_list : list
        List of amino acid sequences

    number_splits : int
        Number of lists to split this list into 

    Returns
    -----------
    list
        Returns a list where each sublist within
        the list contains either the same number
        number of sequences or +/- 1 number of 
        sequences to all other lists, and there
        are number_splits sublists in the main
        return list.
          
    '''
    
    # Calculate the number of protein sequences per sublist
    seqs_per_sublist = len(fasta_list) // num_sublists

    # also count remainder
    remainder = len(fasta_list) % num_sublists

    # Create the sublists
    sublists = []
    start = 0
    for i in range(num_sublists):

        # note: saying 1 if 1 < remainder else 0 means we distribute
        # the remainder evenly across the sublists
        sublist_size = seqs_per_sublist + (1 if i < remainder else 0)

        # create a sublist between start and sublist_size position
        sublist = strings[start:start+sublist_size]
        sublists.append(sublist)
        start = start + sublist_size

    # sanity check - good to be sure!
    if np.sum([len(s) for s in sublist]) != len(fasta_list):
        raise Exception('splitting of fasta file did not get all proteins')

    return sublists


def append_to_file(outpath, idrs, mode):
    # Open file to append to.
    fh = open(outpath, 'a')
    # depending on mode...
    # dict to hold vals...
    return_dictionary = {}
    if mode == 'fasta':
        # for each sequence
        for s in idrs:
            # d is IDR start and end positions
            for d in idrs[s][2]:
                return_dictionary[f'{s:s} IDR_START={d[0]:d} IDR_END={d[1]:d}'] =  d[2]
        # write out fasta. Use append functionality. Protfasta closes the file for us.
        protfasta.write_fasta(return_dictionary, outpath, append_to_fasta=True)

    elif mode == 'shephard-domains':
        for s in idrs:
            # d is IDR start and end positions
            for d in idrs[s][2]:
                # note need +1 for shephard format
                start = d[0]+1
                end = d[1]
                fh.write(f'{s}\t{start}\t{end}\tIDR\n')
        # close file handle.
        fh.close()

    elif mode == 'shephard-domains-uniprot':
        for s in idrs:
            # d is IDR start and end positions
            for d in idrs[s][2]:
                uid = s.split('|')[1]
                start = d[0]+1
                end = d[1]
                fh.write(f'{uid}\t{start}\t{end}\tIDR\n')
        # close file handle.
        fh.close()

    else:
        raise Exception('no mode specified!')

                

# ..........................................................................................
#
def raise_exception_on_zero_length(s):
    """
    Function that raises an exception if the passed argument is of 
    length 0. Works for anything where len() can be applied.
        
    Parameters
    ------------
    s : iterable
        Variable for which len(x) can be applied.

    Returns
    ----------
    None

    Raises
    ---------
    If this first argument in the decorated function is len() == 0
    then MetapredictError is raised.

    """
    if len(s) == 0:        
        if isinstance(s, str):
            raise MetapredictError('Error: Passed string is length 0')

        elif isinstance(s, list):
            raise MetapredictError('Error: Passed list is length 0')
        else:
            raise MetapredictError('Error: Passed iterable type is length 0')


def valid_version(version_specified, prediction_type):
    '''
    Function to handle version specified by the user. 
    To make things less annoying, you can input the version
    as v1, v2, v3, or just 1, 2, 3. This function will
    return the version as a string.

    Parameters
    ----------
    version_specified : str or int
        Version specified by the user

    prediction_type : str
        The type of prediction being made
        options are 'disorder' or 'pLDDT'    

    Returns
    -------
    str
        Returns the version as a string

    '''
    # make sure we are checking a valid network. Make lowercase because pLDDT is annoying. 
    if prediction_type.lower() == 'disorder':
        valid_networks = list(metapredict_networks.keys())
    elif prediction_type.lower() == 'plddt':
        valid_networks = list(pplddt_networks.keys())
    else:
        raise MetapredictError('Invalid prediction type specified. Options are disorder or pLDDT.')

    # make sure that you only get an int or a string as the input for version_specified.
    if isinstance(version_specified, int):
        # if is an int, convert to string
        version = str(version_specified)
    elif isinstance(version_specified, str):
        # if is a string, leave it as is
        version = version_specified
    else:
        # if not either, raise exception
        raise MetapredictError('Version must be an integer or a string')

    # now we can take care of formatting. We have a string that could be 'v1', 'V1', or '1' (for example)
    if len(version)==1:
        # if the length is 1, then we need to add a 'v' to the start
        version = 'V'+version

    # now make sure is uppercase.
    version = version.upper()

    # now see if it's in the valid networks. 
    if version not in valid_networks:
        raise MetapredictError(f'Invalid network specified. Options are {valid_networks}')
    else:
        return version



def write_caid_format(input_dict, output_path, version):
    '''
    Function that takes in a dictionary and outputs a file in the format as 
    specified by IDPcentrail Critical Assessment of Intrinsic protein Disorder
    (CAID). Format is as follows - 
        ouptut is a plain text output where the
        prediction has an entry header >entry_id header, similar to the beginning
        of a .fasta file
        Every line following the entry_id contains tab separated columns with columns
        ordered as follows - 1) residue number, 2) residue name, 3) confidence score,
        4) binary classification where 1 = disordered and 0 = not disordered.

    Example (from idpcentral.org/caid):
        >P04637
        1    M    0.892    1
        2    E    0.813    1

    Parameters
    ----------
    input_dict : dict
        input dictionary of disorder scores. The Key should be the
        entry_id as as string and the associated value should be a list where the
        first element of the list is the corresponding sequence as a string and the
        second item of the list is the corresponding predictions as float values.

    output_path : str
        the path where to save each generated file. The function will save a file
        for each entry in the input_dict. The file will be saved in the format
        entry_id.caid

    version : str
        The version of the network used to make the predictions. Options are 'v1', 'v2', 'v3'

    Returns
    -------
    None
        Does not return anything to the user. Writes a file saved to either
        the current directory or to a specified file path.

    '''

    # first make a list of all of the keys in the dict
    entry_ids = []

    for entry_id in input_dict.keys():
        entry_ids.append(entry_id)

    # make sure output_path is a dir
    if os.path.isdir(output_path)==False:
        raise MetapredictError(f'Please specify output_path as a directory to save generated files. {output_path} is not a valid directory.')

    version=valid_version(version, prediction_type='disorder')

    if version.upper()=='V3':
        cutoff_value=0.5
    elif version.upper()=='V2':
        cutoff_value=0.5
    elif version.upper()=='V1':
        cutoff_value=0.42
    else:
        raise Exception('invalid version detected!')

    # now iterate through the dict and write one file per sequence. 
    for ids in entry_ids:
        cur_id = ids
        if cur_id[0] != '>':
            write_cur_id_header = '>'+cur_id
        else:
            write_cur_id_header = cur_id
        cur_sequence = input_dict[cur_id][0]
        cur_scores = input_dict[cur_id][1]
        
        # open the file to write to
        with open(f'{output_path}/{cur_id}.caid', 'w') as current_output:

            # write entry id
            current_output.write(f'{write_cur_id_header}\n')

            # for each residue write the position, residue, score, and classification
            for res_and_score_index in range(0, len(cur_sequence)):
                cur_residue = cur_sequence[res_and_score_index]
                cur_score = cur_scores[res_and_score_index]
                cur_binary = get_binary_prediction(cur_score, cutoff_value=cutoff_value)
                write_score=str(round(float(cur_score),3))
                if len(write_score) < 5:
                    for i in range(0, 5-len(write_score)):
                        write_score=write_score+'0'

                # write as tsv the caid formatted info
                current_output.write(f'{res_and_score_index+1}\t{cur_residue}\t{write_score}\t{cur_binary}\n')
        
        current_output.close()
