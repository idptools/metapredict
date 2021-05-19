
import re
from metapredict.metapredict_exceptions import MetapredictError


def valid_range(inval, minval, maxval):
    if inval < minval or inval > maxval:
        raise MetapredictError('Value %1.3f is outside of range [%1.3f, %1.3f]' % (inval, minval, maxval))


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
        raise MetapredictError('Unable to write to file destination %s' % (output_file))

    # for each entry
    for idx in input_dict:

        # important otherwise commmas in FASTA headers render the CSV file unreadable!
        no_comma = idx.replace(',', ' ')
        fh.write('%s' % (no_comma))

        # for each score write
        for score in input_dict[idx]:
            fh.write(', %1.3f' % (score))
        fh.write('\n')


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
        raise MetapredictError('Error in parsing shaded_regions - full error below\n\n%s' % (str(e)))


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
        raise MetapredictError('Expected one of %s but only option passed was %s' % (str(valid_list), option))


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
