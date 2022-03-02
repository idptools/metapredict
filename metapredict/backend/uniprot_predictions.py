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


def seq_from_name(name, print_name=True):
    '''
    Function to get the sequence of a protein from the name. 

    Parameters
    ----------
    name: string
        A string that carries the details fo the protein to search for. Can 
        contain the name of the protein as well as the name of the organims.
            ex. ARF19
                Arabidopsis ARF19

                p53
                Human p53
                Homo sapiens p53

    print_name : bool
        Whether to print the name of the recieved protein to the 
        user. By default is seet to True such that the user can see 
        which protein was actually used.


    Returns
    -------
    top_hit : string
        Returns the amino acid sequence of the top hit on uniprot
        website.
    '''



    # first format name into a url
    # uses only reviewed
    name = name.split(' ')
    if len(name) == 1:
        # this url does not filter for the reviewed proteins
        # leaving as a backup
        # use_url = f'https://www.uniprot.org/uniprot/?query={name[0]}&sort=score'

        use_url = f'https://www.uniprot.org/uniprot/?query={name[0]}&fil=reviewed%3Ayes&sort=score'


    else:
        add_str = ''
        for i in name:
            add_str += i
            add_str += '%20'
        add_str = add_str[0:len(add_str)-3]
        # this url does not filter for the reviewed proteins
        # leaving as a backup
        #use_url = f'https://www.uniprot.org/uniprot/?query={add_str}&sort=score'

        # one below filters for the reviewed proteins.
        use_url = f'https://www.uniprot.org/uniprot/?query={add_str}&fil=reviewed%3Ayes&sort=score'

    # set http
    http = urllib3.PoolManager()
    # get r
    r = http.request('GET', use_url)

    if b'Sorry, no results found for your search term.' in r.data:
        if len(name) == 1:
            # this url does not filter for the reviewed proteins
            use_url = f'https://www.uniprot.org/uniprot/?query={name[0]}&sort=score'

        else:
            add_str = ''
            for i in name:
                add_str += i
                add_str += '%20'
            add_str = add_str[0:len(add_str)-3]
            # this url does not filter for the reviewed proteins
            use_url = f'https://www.uniprot.org/uniprot/?query={add_str}&sort=score'

        # set http
        http = urllib3.PoolManager()
        # get r
        r = http.request('GET', use_url)

        if b'Sorry, no results found for your search term.' in r.data:
            raise MetapredictError('Sorry! We were not able to find the protein corresponding to that name.')

    # now that the url is figured out and the data fetched, parse it to get the uniprot ids.
    parsed_data=r.data.split(b'checkbox_')
    # take the top uniprot ID from the page
    first_hit = str(parsed_data[1])[2:]
    # now format the top hit so it is just the uniprot ID
    top_hit = (first_hit.split('"')[0])
    org = first_hit.split('taxonomy')
    organism_name = (org[1].split('>')[1].split('<')[0])
    organism_name = organism_name.split()
    final_name = ''
    for val in organism_name:
        final_name += val
        final_name += '_'
    final_name = final_name[:len(final_name)-1]

    # by default, print the actual protein name to the terminal / console
    # so the user knows which one they ended up getting. Then can verify
    # that the search was correct
    if print_name == True:
        print(f'>{top_hit}_{final_name}')
    return fetch_sequence(top_hit)



