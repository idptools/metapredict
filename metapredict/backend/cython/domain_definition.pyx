import numpy as np
cimport numpy as np
from libc.math cimport round

import numpy as np
cimport numpy as np
cimport cython 

from cpython cimport array
import array


def public_binerize(np.ndarray[np.float64_t, ndim=1] idr_score, double disorder_threshold):
    return  binerize_function(idr_score, disorder_threshold)

## ................................................................................................
##
#cdef binerize_function(np.ndarray[np.float64_t, ndim=1] idr_score, double disorder_threshold):
cdef binerize_function(double[:]  idr_score, double disorder_threshold):
    """
    Cython function to binerize the disorder scores. This function takes in a numpy array
    of floats and and returns a numpy integer array where if the float > above disorder_
    threshold it gives a 1, otherwise gives a 0.


    disoder_threshold : double 
        NOTE - make sure its a double because in Python numerical values are by default
        a 64-bit (double) and so if say float it gets propagated here as a 32-bit number
        which cases some issues when comparing greater than/less than


    

    """

    
    cdef int i
    cdef np.ndarray[np.int32_t, ndim=1] return_vals = np.empty(idr_score.shape[0], dtype=np.int32)
    
    for i in range(idr_score.shape[0]):

        if idr_score[i] > disorder_threshold:
            return_vals[i] = 1
        else:
            return_vals[i] = 0
            
    return return_vals

## ................................................................................................
##
@cython.boundscheck(False)
@cython.wraparound(False) 
cdef int sum_array(int start, int end, np.ndarray[np.int32_t, ndim=1] B):
    """
    This function is actually where most of the performance boost for cythonizing this whole
    thing comes from. The first loop in the domain decomposition code has a TON of calls
    to np.sum for very small arrays which kills performance. By writing our own implementation
    here which can be compiled down to pure C - all those summations are in native C with zero
    numpy/python overhead.

    Parameters
    -----------------
    start : int
        Note we don't bounds check so NEED to be sure that start >=0 or this will cause a 
        segfault (and the 'kernel will die' from Python's perspective)

    end : int
        Note we don't bounds check so NEED to be sure that end < len(B) or this will cause a 
        segfault (and the 'kernel will die' from Python's perspective)

    B : np.ndarray[np.int32_t, ndim=1]
        Binary array - i.e. a 1D array of integers 

    Returns
    -----------------
    int
        This function returns an integer which is equal to the sum of the values
        in the binary array between 
    """
    
    cdef int i, total_sum = 0
    for i in range(start, end):
        total_sum += B[i]
    return total_sum


## ................................................................................................
##
##
#cpdef build_domains_from_values(np.ndarray[np.float64_t, ndim=1] values,
cpdef build_domains_from_values(double[:]  values,
                                double disorder_threshold,
                                int minimum_IDR_size=12,
                                int minimum_folded_domain=50,
                                int gap_closure=10,
                                bint override_folded_domain_minsize=False):

    """
    
    MAKE SURE disorder_threshold is a double for the love of god

    """
    cdef:    
        int folded_domain_min_size_1, folded_domain_min_size_2
        np.ndarray[np.int32_t, ndim=1] B
        int i, g, p1, p2, p3, p4, idx, start, gap_start, end
        list local_domains = [], local_gaps = [], real_gaps = [], tmp = [], valid_vals = []
        bint inside
        float mean_value

    # 
    if not override_folded_domain_minsize:
        folded_domain_min_size_1 = 35
        folded_domain_min_size_2 = 20
    else:
        folded_domain_min_size_1 = minimum_folded_domain
        folded_domain_min_size_2 = minimum_folded_domain

    # build a binary version
    B = binerize_function(values, disorder_threshold)

    #print(B)
    
    if len(values) < minimum_IDR_size or len(values) < 3*gap_closure+1:
        if np.mean(B) >= disorder_threshold:

            # return (idr_boundaries, fd_boundaries)
            return ([[0, len(B)]], [[]])
        else:

            # return (idr_boundaries, fd_boundaries)
            return ([[]], [[0, len(B)]])
    
    if len(B) != len(values):
        raise ValueError('Error with binerize function. This is a bug.')
    
    for g in range(1, gap_closure+1):
        
        i = 0
        
        while True:
            p1 = i
            p2 = i + g
            p3 = i + 2*g
            p4 = i + 3*g

            # if the complete set of smaller regions ahead is empty or
            # fully assigned skip ahead because nothing to do here...
            #if np.sum(B[p1:p4]) == 0:
            if sum_array(p1,p4,B) == 0:
                i = p4

            # we jump to the p3 position (and NOT p4) as this allows us to skip along without
            # discarding positions we need for filling. Note if we know everything is empty
            # it doesn't matter and we can jump to p4
            #elif np.sum(B[p1:p4]) == 3*g:
            elif sum_array(p1,p4,B) == 3*g:
                i = p3

            # if we have gapsize number of hits and gap away there's another gapsize
            else:
                #if np.sum(B[p1:p2]) == g and np.sum(B[p3:p4]) == g:
                if sum_array(p1,p2,B) == g and sum_array(p3,p4,B) == g:
                
                    B[p2:p3] = [1]*g
                i = i + 1

            if i + 3*g >= len(B):
                break

    # build a binary string
    B_string = '-' + ''.join(map(str, B)) + '-'


    for i in range(1, minimum_IDR_size + 1):

        # 011110 -> 000000
        B_string = B_string.replace('0' + i*'1' + '0', '0' + i*'0' + '0')

        # -11110 -> -00000
        B_string = B_string.replace('-'+i*'1' + '0', '-'+i*'0' + '0')

        # 01111- -> 00000-
        B_string = B_string.replace('0' + i*'1'+'-', '0' + i*'0'+'-')
                   
        # -1111- -> -0000-
        B_string = B_string.replace('-' + i*'1'+'-', '-' + i*'0'+'-')

    # 1 to -1 to cut off the artificial caps we added
    for i in range(1, len(B_string)-1):
        B[i-1] = int(B_string[i])

    # Part 3 - extract domain boundaries
    if B[0] == 1:
        inside = True
        start = 0
        gap_start = -1
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

    # finally we merge together any adjacent domains that have now been created in step 4
    tmp = [item for sublist in local_domains for item in sublist]
    tmp.sort()

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


