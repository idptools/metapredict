# code for pulling down uniprot sequence for predictions
import urllib3
from metapredict.metapredict_exceptions import MetapredictError


def fetch_sequence(uniprot_id):
    """
    Function that returns the amino acid sequence by polling UniProt.com

    Note that right now the test for success is a bit hap-hazard (looks for the
    string "Sorry", which appears if the UniProt call fails. We probably want
    something a bit more robust in the future...

    Parameters
    --------------
    uniprot_id : str
        Uniprot accession number

    Returns
    -----------
    str or None:
        If the call is succesfull, this returns the amino acid string. If not, it returns
        None. 

    """

    http = urllib3.PoolManager()
    r = http.request('GET', 'https://www.uniprot.org/uniprot/%s.fasta' % (uniprot_id))

    s = "".join(str(r.data).split('\\n')[1:]).replace("'", "")

    # make sure that the last character is not a " due to a ' in protein name
    # Thank you to Github user keithchev for pointing out this bug!
    if s[len(s)-1] == '"':
        s = s[:len(s)-1]

    if s.find('Sorry') > -1:
        raise MetapredictError('Error: unable to fetch UniProt sequence with accession %s'%(uniprot_id))


    return s
