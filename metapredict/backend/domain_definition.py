import numpy as np
import scipy
from scipy.signal import savgol_filter
from metapredict.metapredict_exceptions import DomainError
"""
Functions for extracting out discrete disordered domains based on the linear disorder score
calculated by metapredict.

"""


# ------------------------------------------------------------------------
##

def __build_domains_from_values(values,
                                disorder_threshold,
                                minimum_IDR_size=12,
                                minimum_folded_domain=50,
                                gap_closure=10,
                                override_folded_domain_minsize=False):
    """
    This function  extracts out disordered and folded domains from the linear
    disorder score. There are a few parameters here that tune the behavior, but
    the upshot is that the function returns a 2-position list where position 1 is a 
    list that defines boundaries for IDRs and position 2 is a list that defines
    boundaries for folded domains. These two sets of boundaries should be fully
    complementary to one another.


    Parameters
    -----------
    values : list
        A list of disorder values. This should be a list where every value has a number
        for each residue.

    disorder_threshold  : float
        The threshold value used to define if a region is truly disordered or not. This 
        threshold is applied by saying if a residue has a disorder score > $disorder_threshold
        it might be in an IDR, although other constrains/analysis are required.

    minimum_IDR_size : int
        Value that defines the shortest possible IDR. Default is 12.

    minimum_folded_domain : int 
        Value used in the final stages where any 'gaps' < $minimum_folded_domain
        are revaluated with a slightly less stringent disorder threshold. Note that,
        in addition, gaps < 35 are evaluated with a threshold of 0.35*disorder_threshold
        and gaps < 20 are evaluated with a threshold of 0.25*disorder_threshold. These
        two lengthscales were decided based on the fact that coiled-coiled regions (which
        are IDRs in isolation) often show up with reduced apparent disorder within IDRs,
        and but can be as short as 20-30 residues. The minimum_folded_domain is used
        based on the idea that it allows a 'shortest reasonable' folded domain to be 
        identified. Default is 50.

    gap_closure : int
        Value that allow short gaps within two disorder or folded domains to be
        folded in. This actually ends up being most important when disorder scores
        are unsmoothed. Default is 10.

    override_folded_domain_minsize : bool
        By default this function includes a fail-safe check that assumes folded domains
        really shouldn't be less than 35 or 20 residues. However, for some approaches we
        may wish to over-ride these thresholds to match the passed minimum_folded_domain
        value. If this flag is set to True this override occurs. This is generally not 
        recommended unless you expect there to be well-defined sharp boundaries which could
        define small (20-30) residue folded domains. Default = False.

    Returns
    -------------
    list of lists

        Returns a list of lists, where the first list has IDR domain boundaries and
        the second list has folded domain boundaries. For example this might look like:

        [0]  = [[0,50]]
        [1]  = [50,100]]

        For a 100-residue protein where residue 1-50 are disordered and 51-100 are folded.
        Note indexing here is done to be simply compiant with Python slicing 

    """

    # these parameters are fixed but in principle could be tuned. They basically give
    # upper bounds for what we might consider to be single folded structures which are then
    # used as a final step in the procedure (see step 5). Defined here just by convention
    # of defining params early on
    if override_folded_domain_minsize is False:
        folded_domain_min_size_1 = 35
        folded_domain_min_size_2 = 20
    else:
        folded_domain_min_size_1 = minimum_folded_domain
        folded_domain_min_size_2 = minimum_folded_domain

    # Defines a local function that converts a continous IDR score into a bindary classification
    # - this function is instantiated with the passed disorder_threshold
    def binerize_function(idr_score):
        return_vals = []
        for i in idr_score:
            if i > disorder_threshold:
                return_vals.append(1)
            else:
                return_vals.append(0)

        return return_vals

    B = binerize_function(values)

    # for small changes class as either folded or disordered
    if len(values) < minimum_IDR_size or len(values) < 3*gap_closure+1:

        if np.mean(B) >= disorder_threshold:
            idr_boundaries = [[0, len(B)]]
            fd_boundaries = [[]]
            return (idr_boundaries, fd_boundaries)

        else:
            idr_boundaries = [[]]
            fd_boundaries = [[0, len(B)]]
            return (idr_boundaries, fd_boundaries)

    # add to help debugging
    if len(B) != len(values):
        raise DomainError('Error with binerize function. This is a bug. Please raise an issue on GitHub')

    # Part 1 - remove gaps
    for g in range(1, gap_closure+1):
        # first fill in

        # for each position
        i = 0
        finished = False
        while not finished:

            p1 = i
            p2 = i + g
            p3 = i + 2*g
            p4 = i + 3*g

            # if the complete set of smaller regions ahead is empty or
            # fully assigned skip ahead because nothing to do here...
            if np.sum(B[p1:p4]) == 0:
                i = p4

            elif np.sum(B[p1:p4]) == 3*g:

                # we jump to the p3 position (and NOT p4) as this allows us to skip along without
                # discarding positions we need for filling. Note if we know everything is empty
                # it doesn't matter and we can jump to p4
                i = p3

            else:
                # if we have gapsize number of hits
                if np.sum(B[p1:p2]) == g:

                    # and if a gap away there is another gapsize
                    if np.sum(B[p3:p4]) == g:
                        B[p2:p3] = [1]*g

                i = i + 1

            if i + 3*g >= len(B):
                finished = True

    # Part 2 - remove domains that are too small - we adde the '-' caps so we can use
    # replace and distinguish c/n terminal values
    B_string = '-'
    for i in B:
        if i == 1:
            B_string = B_string+"1"
        else:
            B_string = B_string+"0"

    B_string = B_string+'-'

    # for sizes of contigous stretches that are up minimum_IDR_size + 1
    # replace with empty ('0') strings
    for i in range(1, minimum_IDR_size + 1):

        # 011110 -> 000000
        B_string = B_string.replace('0' + i*'1' + '0', '0' + i*'0' + '0')

        # -11110 -> -00000
        B_string = B_string.replace('-'+i*'1' + '0', '-'+i*'0' + '0')

        # 01111- -> 00000-
        B_string = B_string.replace('0' + i*'1'+'-', '0' + i*'0'+'-')

        # -1111- -> -0000-
        B_string = B_string.replace('-' + i*'1'+'-', '-' + i*'0'+'-')

    # 1 to -1 to cut off the artifical caps we added
    for i in range(1, len(B_string)-1):
        B[i-1] = int(B_string[i])

    # Part 3 - extract domain boundaires

    local_domains = []
    local_gaps = []

    if B[0] == 1:
        inside = True
        start = 0
        gap_start = None
    else:
        inside = False
        gap_start = 0

    # for each position
    for idx in range(0, len(B)):

        i = B[idx]

        if i == 1:
            if inside:
                continue
            else:
                local_gaps.append([gap_start, idx])
                inside = True
                start = idx

        if i == 0:
            if inside:
                inside = False
                end = idx
                local_domains.append([start, end])
                gap_start = idx

    # if we finished inside
    if inside:
        local_domains.append([start, len(B)])
    else:
        local_gaps.append([gap_start, len(B)])

    # Part 4 - final closure of larger gaps if close to disorder_threshold
    real_gaps = []
    for d in local_gaps:

        if d[1]-d[0] < minimum_folded_domain:
            if np.mean(values[d[0]:d[1]]) > disorder_threshold*0.75:
                local_domains.append(d)
                continue

        if d[1]-d[0] < folded_domain_min_size_1:
            if np.mean(values[d[0]:d[1]]) > disorder_threshold*0.35:
                local_domains.append(d)
                continue

        if d[1]-d[0] < folded_domain_min_size_2:
            if np.mean(values[d[0]:d[1]]) > disorder_threshold*0.25:
                local_domains.append(d)
                continue

        real_gaps.append(d)

    # finally we merge together any adjacent domains that have now been
    # created in step 4
    tmp = [item for sublist in local_domains for item in sublist]
    tmp.sort()

    valid_vals = []
    i = 0
    while i < len(tmp)-1:
        if tmp[i] == tmp[i+1]:
            i = i+2
        else:
            valid_vals.append(tmp[i])
            i = i+1

    if len(tmp) > 0:
        valid_vals.append(tmp[-1])

    local_domains = []
    for i in range(0, len(valid_vals), 2):
        local_domains.append([valid_vals[i], valid_vals[i+1]])

    return (local_domains, real_gaps)


def get_domains(sequence,
                disorder,
                disorder_threshold=0.42,
                minimum_IDR_size=12,
                minimum_folded_domain=50,
                gap_closure=10,
                override_folded_domain_minsize=False):
    """

    Parameters
    -------------
    sequence : str
        Amino acid sequence

    disorder : list of floats
        List of per-residue disorder values. Must be same length and sequence

    disorder_threshold : float
        Value that defines what 'disordered' is based on the metapredict disorder score. The higher the value the more
        stringent the cutoff. Default = 0.42.

    minimum_IDR_size : int
        Defines the smallest possible IDR. This is a hard limit - i.e. we CANNOT get IDRs smaller than this. Default = 12.

    minimum_folded_domain : int
        Defines where we expect the limit of small folded domains to be. This is NOT a hard limit and functions to modulate
        the removal of large gaps (i.e. gaps less than this size are treated less strictly). Note that, in addition, 
        gaps < 35 are evaluated with a threshold of 0.35*disorder_threshold and gaps < 20 are evaluated with a threshold 
        of 0.25*disorder_threshold. These two lengthscales were decided based on the fact that coiled-coiled regions (which
        are IDRs in isolation) often show up with reduced apparent disorder within IDRs, and but can be as short as 20-30 
        residues. The minimum_folded_domain is used based on the idea that it allows a 'shortest reasonable' folded domain 
        to be identified. Default = 50.

    gap_closure : int
        Defines the largest gap that would be 'closed'. Gaps here refer to a scenario in which you have two groups
        of disordered residues seprated by a 'gap' of un-disordered residues. In general large gap sizes will favour 
        larger contigous IDRs. It's worth noting that gap_closure becomes relevant only when minimum_region_size becomes
        very small (i.e. < 5) because really gaps emerge when the smoothed disorder fit is "noisy", but when smoothed gaps
        are increasingly rare. Default = 10.

    override_folded_domain_minsize : bool
        By default this function includes a fail-safe check that assumes folded domains
        really shouldn't be less than 35 or 20 residues. However, for some approaches we
        may wish to over-ride these thresholds to match the passed minimum_folded_domain
        value. If this flag is set to True this override occurs. This is generally not 
        recommended unless you expect there to be well-defined sharp boundaries which could
        define small (20-30) residue folded domains. Default = False.

    Returns
    ------------

    list 

        This function takes an amino acid sequence, a disorder score, and returns a 4-position tiple with
        the following information:

        [0] - Smoothed disorder score used to aid in domain boundary identification

        [1] - a list of elements, where each element is itself a list where position 0 and 1 define the IDR location 
              and position 2 gives the actual IDR sequence

        [2] - a list of elements, where each element is itself a list where position 0 and 1 define the folded domain 
              location and position 2 gives the actual folded domain sequence
    """

    # First set up for disorder smoothing function
    polynomial_order = 3  # larger means tight fit. 3 works well...

    # define window size for smoothing function. Note must be an odd number,
    # hence the if statement
    window_size = 2*minimum_IDR_size

    if window_size <= polynomial_order:
        window_size = polynomial_order+2

    if len(disorder) <= window_size:
        print('Warning: length of disorder [%i] is <= window_size [%i]. This happens when you have a small IDR relative to the minimum IDR size. Updating windowsize to match sequence length.' % (
            len(disorder), window_size))
        window_size = len(disorder)

    if window_size % 2 == 0:
        window_size = window_size - 1

    if polynomial_order >= window_size:
        polynomial_order = window_size - 1

    # smoothe!!!!
    smoothed_disorder = savgol_filter(disorder, window_size, polynomial_order)

    # Using smoothed disorder extract out domains
    disordered_domain_info = __build_domains_from_values(smoothed_disorder,
                                                         disorder_threshold,
                                                         minimum_IDR_size=minimum_IDR_size,
                                                         minimum_folded_domain=minimum_folded_domain,
                                                         gap_closure=gap_closure,
                                                         override_folded_domain_minsize=override_folded_domain_minsize)
                                                         

    # finally cycle through and get the actual IDR and FD sequences. Note the if len(d) ==2 means we
    # skip over cases where no FDs or no IDRs were found
    idrs = []
    for d in disordered_domain_info[0]:
        if len(d) == 2:
            idrs.append([d[0], d[1], sequence[d[0]:d[1]]])

    fds = []
    for d in disordered_domain_info[1]:
        if len(d) == 2:
            fds.append([d[0], d[1], sequence[d[0]:d[1]]])

    return [smoothed_disorder, idrs, fds]
