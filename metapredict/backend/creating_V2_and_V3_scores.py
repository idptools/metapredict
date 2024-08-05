"""
BELOW IS CODE THAT SHOULD BE KEPT GOING FORWARD FOR REPRODUCIBILITY!

The code below was basically used to make the scores used to make
the V2 network and the v3 network

The metapredict V2 network was created by training on what we 
call 'meta-hybrid scores'. These scores used predicted pLDDT scores and
legacy metapredict (V1) disorder scores as the input values for training the final v2 
network. It's important to note that the predictor used for pLDDT predictions was
trained on the original set of AF2 structures available. They are now at 'V4',
I'm not sure if that actually chages pLDDT values but it's important to note.
The V3 predictor used the *actual* v4 values. 

Similar to V2, V3 used a combination of pLDDT scores and legacy metapredict.
However, for V3 we used real pLDDT scores (not predicted) to make the 
final scores that were used for training the V3 network. In addition,
we also used a moving average to smooth the scores as a final data 
processing step. Finally, the actual data was all sequences from swissprot
that were not duplicated in the dataset.
"""

# import local modules
from metapredict.backend.predictor import predict, predict_pLDDT
import alphaPredict as alpha

# import everything else
import sys
import os
import numpy as np
from scipy.signal import savgol_filter
from tqdm import tqdm
from io import StringIO


''' 
Code below was used to make V2 scores.
'''

def meta_predict_hybrid(sequence, cooperative=True):
    """
    This function was used to generate the scores that were used to
    ultimately train the metapredict V2 and V3 networks. 
    Predictions are made by inputting predicted AF2 pLDDT (ppLDDT) and 
    metapredict V1 profiles to construct a novel 'hybrid' profile.
    
    Parameters
    ------------
    sequence : string
        The amino acid sequence for the protein.

    cooperative : bool
        Flag which defines if cooperative or non-cooperative mode
        should be used. Both are provided for now but we may remove
        non-cooperative given the cooperative mode seems to always
        offer better performance.
        Default = True

    Returns
    ----------
    np.ndarray
        Returns an array that matches the length of the two input
        lists and provides the metapredict-hybrid disorder scores

    """
    # get the metapredict scores. 
    metapredict_disorder = predict(sequence, version='V1', round_values=False)
    ppLDDT = predict_pLDDT(sequence, version='V1', return_decimals=True, round_values=False)
    

    # defines functionally the limits that the predicted pLDDT score
    # can be between
    base = 0.35
    top  = 0.95

    # this normalizes so the pLDDT score ends up being renormalized
    # to be between 0 and 1, converted into an effective disorder score
    d = (ppLDDT - base)*(1/(top-base))

    # if not cooperative then flatten here
    if cooperative is False:
        d = np.where(d<0, 0, d)
        d = np.where(d>1, 1, d)
        
    # means value of 1 = disordered and 0 is disordered
    d = 1 - d

    # if we're using cooperative mode...
    if cooperative:

        hybrid_vals = []
        for idx in range(len(d)):
        
            vmax = max([metapredict_disorder[idx], d[idx]]) 
            
            # if the largest disorder score for either is above 0.5 go
            # with that score as the consensus
            if vmax > 0.5:
                hybrid_vals.append(vmax)

            # else go with the smallest disorder score as the consensus
            else:
                hybrid_vals.append(min([metapredict_disorder[idx], d[idx]]) )
            
        # smooth with a window size of 7 to kill discontinuities
        smoothed = savgol_filter(hybrid_vals,7,3)
        
        # flatten so all values in the bounds of 0 to 1
        smoothed = np.where(smoothed<0, 0, smoothed)
        hybrid = np.where(smoothed>1, 1, smoothed)
    else:
        hybrid = np.amax(np.array([metapredict_disorder, d]),0)

    return hybrid


'''
code below used to make v3 scores. 
'''

def parse_plddt_data(path_to_fi):
    '''
    function to read in the plddt data
    formatted as a tab-delimited file.

    Parameters
    ------------
    path_to_fi : str
        The path to the file containing the plddt data.

    Returns
    ----------
    dict
        Returns a dictionary with the sequence as the key and the 
        plddt scores as the values. 
    '''
    with open(path_to_fi, 'r') as fh:
        lines = fh.read().split('\n')
    fh.close()
    seq_to_dat={}
    for line in tqdm(lines):
        if line != '':
            split_vals=line.split()
            seq_id=split_vals[0]
            seq=split_vals[1]
            dat = []
            for val in split_vals[2:]:
                dat.append(float(val))
            seq_to_dat[seq] = dat
    return seq_to_dat

def moving_average(scores, window_size):
    """
    Smooths an array of scores over a user-specified sliding window size.

    Parameters
    ----------
    scores : array
        Array of scores to be smoothed.
    window_size : int
        Size of the sliding window for smoothing.

    Returns
    -------
    smoothed_scores : ndarray 
        Smoothed scores with the same length as the input array.
    """
    if window_size % 2 == 0:
        raise ValueError("Window size must be an odd number.")

    half_window = window_size // 2
    pad_width = ((half_window, half_window),)  # Pad equally on both sides
    padded_scores = np.pad(scores, pad_width, mode='reflect') 
    smoothed_scores = np.convolve(padded_scores, np.ones(window_size) / window_size, mode='valid')
    return smoothed_scores



def meta_predict_hybrid_v3(inputs, metapredict_version='v1', vmax_cutoff=0.5,
    base=0.35, top=0.95, windowed_averaging=25):
    """
    Code used to generate the scores used to train metapredict V3. 
    All default values in the function are as used to make V3 scores.
    Real pLDDT scores (not predicted) were used to make V3. 

    Parameters
    ------------
    inputs : dict
        Sequences as the keys and the plddt scores as the values. 

    metapredict_version : str
        The version of metapredict to use. 
        Default = 'v1'

    vmax_cutoff : float
        The cutoff value for the maximum value. 
        Default = 0.5

    base : float
        The base value for the plddt scores. 
        Default = 0.35

    top : float
        The top value for the plddt scores. 
        Default = 0.95

    windowed_averaging : Int
        Whether to smooth scores. Default is 25. 
        Value to make V3 scores for training was 25. 

    Returns
    ----------
    dict of nd.nparrays
        Returns a dict of arrays with the sequence as the key and the 
        scores as the values. 
    """
    # make dict to hold sequences and plddt / disorder scores
    seq_plddt_disorder_dict={}

    # make sure a dict is input
    if isinstance(inputs, dict):
        sequences=list(inputs.keys())
        disorder_scores = predict(sequences, version=metapredict_version, round_values=False)
        for n in range(0, len(disorder_scores)):
            seq = disorder_scores[n][0]
            disorder = disorder_scores[n][1]
            plddt=np.array(inputs[seq])
            seq_plddt_disorder_dict[seq] = {'disorder':disorder,'pLDDT': plddt}
    else:
        raise Exception('only a dict is accepted as input for this function.')

    # now we need to iterate over the dictionary and get hybrid scores. 
    hybrid_scores = {}
    for seq in tqdm(seq_plddt_disorder_dict):
        pLDDT = seq_plddt_disorder_dict[seq]['pLDDT']
        disorder = seq_plddt_disorder_dict[seq]['disorder']

        # defines functionally the limits that the predicted pLDDT score
        # can be between
        base = base
        top  = top

        # this normalizes so the pLDDT score ends up being renormalized
        # to be between 0 and 1, converted into an effective disorder score
        d = (pLDDT - base)*(1/(top-base))
            
        # means value of 1 = disordered and 0 is disordered
        d = 1 - d

        hybrid_vals = []
        for idx in range(len(d)):

            vmax = max([disorder[idx], d[idx]]) 
            
            # if the largest disorder score for either is above 0.5 go
            # with that score as the consensus
            if vmax > vmax_cutoff:
                hybrid_vals.append(vmax)

            # else go with the smallest disorder score as the consensus
            else:
                hybrid_vals.append(min([disorder[idx], d[idx]]))
            
        # smooth with a window size of 7 to kill discontinuities
        smoothed = savgol_filter(hybrid_vals,7,3)
        
        # flatten so all values in the bounds of 0 to 1
        smoothed = np.where(smoothed<0, 0, smoothed)
        smoothed = np.where(smoothed>1, 1, smoothed)

        # moving averaging
        if windowed_averaging != None:
            smoothed=moving_average(smoothed, windowed_averaging)

        hybrid_scores[seq]=np.round(smoothed,4).tolist()
    return hybrid_scores



def generate_parrot_file(path_to_plddt_data, path_to_save_file, windowed_averaging=25):
    '''
    function taht will read in a TSV of plddt data and sequences 
    and save out a file that will be PARROT formatted with a sequence
    identifier, sequence, and hybrid V3 scores. 
    
    Parameters
    ----------
    path_to_plddt_data : str
        The path to the plddt data file

    path_to_save_file : str
        where to save the final file. 

    windowed_averaging : Int
        Whether to smooth scores. Default is 25. 
        Value to make V3 scores for training was 25. 

    Returns
    -------
    None
    '''
    # read in the data
    print('Reading in data.')
    seq_to_dat = parse_plddt_data(path_to_plddt_data)
    print('Predicting hybrid scores.')
    hybrid_scores = meta_predict_hybrid_v3(seq_to_dat, windowed_averaging=windowed_averaging)
    print('Saving output data.')
    num=0
    with open(path_to_save_file, 'w') as fh:
        for seq in tqdm(hybrid_scores):
            num+=1
            if len(seq)!= len(hybrid_scores[seq]):
                raise Exception('ERROR: sequence length does not equal hybrid score length!')
            temp=''
            for val in hybrid_scores[seq]:
                temp+=str(val)+' '
            fh.write(f'seq_{num}\t{seq}\t{temp}\n')
    fh.close()
    print('Done!')

