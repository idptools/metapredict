"""
Backend of the ORIGINAL IDR machine learning predictor. Based partly
on code from Dan Griffith's IDP-Parrot from the Holehouse lab
(specifically the test_unlabeled_data function in train_network.py).

This also contains the code for metapredict-hybrid (function is
meta_predict_hybrid()), which was used to generate scores that were used 
to train the newest metapredict network, metameta_2_7_22_nl2_hs20_b32_v3.pt.

Yes, metapredict somehow got a little bit more meta.
"""

# import packages for predictor
import sys
import os

import numpy as np

from scipy.signal import savgol_filter

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader


# import modules that predictor depends on
from metapredict.backend import encode_sequence
from metapredict.backend import brnn_architecture
from metapredict.metapredict_exceptions import MetapredictError


# set path for location of predictor. Using this in case I want to update the predictor or
# eventually make multiple predictors.
PATH = os.path.dirname(os.path.realpath(__file__))

# Setting predictor equal to location of weighted values.

# originl network
predictor = "{}/networks/meta_predict_disorder_100e_v1.pt".format(PATH)

# V2 network holds slight increases in accuracy but is still undergoing testing.
# so far, 0.5% increase in accuracy has been consistently seen. V1 is the published
# network though, so leaving fo the time being.
# predictor = "{}/networks/metapredict_network_v2_200epochs_nl1_hs20.pt".format(PATH)

# v3 network has significant increase in accuracy of predicting the actual consensus
# score values. Actual accuracy from predicting disorder values using the Disprot-PDB
# testing (as in the paper) were negligent. Therefore, we will not use it as the
# main network and will continue using V1. 


##################################################################################################
# hyperparameters used by when metapredict was trained. Manually setting them here for clarity.
##################################################################################################
# This is defined externally so its read in and loaded one time on the initial import
#


'''
meta_predict_disorder_100e_v1 paramters
# original published network!


device = 'cpu'
hidden_size = 5
num_layers = 1
dtype = 'residues'
num_classes = 1
encoding_scheme = 'onehot'
input_size = 20
problem_type = 'regression'


# metapredict_network_v2_200epochs_nl1_hs20 parameters 
# if you want to use V2 network, move this code out of
commented out section and delete similar code below.

device = 'cpu'
hidden_size = 20
num_layers = 1
dtype = 'residues'
num_classes = 1
encoding_scheme = 'onehot'
input_size = 20
problem_type = 'regression'


# metapredict_network_v3_200epochs_nl2_hs20 parameters 
# if you want to use V3 network, move this code out of
commented out section and delete similar code below.

The V3 network was not significantly better at predicting
the disprot-pdb dataset as far as disorder predictions. 
It was better at predicting consensus values from MobiDB by
a substantial margin (V1 R^2 was 0.878, V3 R^2 was 0.966)

device = 'cpu'
hidden_size = 20
num_layers = 2
dtype = 'residues'
num_classes = 1
encoding_scheme = 'onehot'
input_size = 20
problem_type = 'regression'

'''

# hyperparameters for original network

device = 'cpu'
hidden_size = 5
num_layers = 1
dtype = 'residues'
num_classes = 1
encoding_scheme = 'onehot'
input_size = 20
problem_type = 'regression'


# set location of saved_weights for load_state_dict
saved_weights = predictor

###############################################################################
# Initialize network architecture using previously defined hyperparameters
###############################################################################

brnn_network = brnn_architecture.BRNN_MtM(input_size, hidden_size, num_layers, num_classes, device).to(device)
# if you want to use the V3 network, uncomment line below and comment out line above.
#brnn_network = nn.DataParallel(brnn_architecture.BRNN_MtM(input_size, hidden_size, num_layers, num_classes, device).to(device))
brnn_network.load_state_dict(torch.load(saved_weights, map_location=torch.device(device)))
###############################################################################

def get_metapredict_legacy_network_version():
    """
    Function that returns a string with the current predictor version. Note that this requires trained weight
    files to have a format that ends in "<anything>_v<version info>.pt". 
    
    For example, 'meta_predict_disorder_100e_v1.pt', 'meta_predict_disorder_best_v1.4.pt' etc.

    Returns
    ----------
    str 
        Returns a string with the current metapredict trained network being used

    """
    return ".".join(predictor.split('_')[-1].split('.')[:-1])


def meta_predict(sequence, normalized=True, network=brnn_network, device=device, encoding_scheme=encoding_scheme):
    """
    The actual executing function for predicting the disorder of a sequence using metapredict.
    Returns a list containing predicted disorder values for the input sequence. 

    Parameters:
    ------------
    sequence : str
        The amino acid sequence to be predicted

    normalized : bool
        Flag which defines if normalization should occur or not. By default,
        negative values are set to be equal to 0 and values greater than 1 
        are set to be equal to 1. User can set normalized=False to get raw 
        prediction values.
        Default = True

    network : Pytorch network 
        Defines the Pytorch network to be used. Alternative networks can
        provided in principle, but in practice metapredict has been trained
        on a specific network. Default = network loaded by metapredict.
      
    device : str
        String describing where the network is physically stored on the computer. 
        Should be either 'cpu' or 'cuda' (GPU). Default = 'cpu'

    encoding_scheme : str
        String that defines the encoding scheme used when metapredict was 
        trained. The encoding scheme used in the default implementation 
        was 'onehot'. Default='onehot'.

    Returns:
    ----------
    list
        Returns a list with a per-residue disorder score. The list length
        will match the length of the input sequence.
    
    """

    # set seq_vector equal to converted amino acid sequence that is a PyTorch tensor of one-hot vectors
    if encoding_scheme == 'onehot':
        seq_vector = encode_sequence.one_hot(sequence)
    else:
        raise MetapredictError('fCannot understand encoding scheme [{encoding_scheme}]')

    seq_vector = seq_vector.view(1, len(seq_vector), -1)

    # get output values from the seq_vector based on the network (brnn_network)
    outputs = network(seq_vector.float()).detach().numpy()[0]

    # make empty list to add in outputs
    output_values = []
    # for the values 'i' in outputs
    for i in outputs:
        # append each value (which is the predicted disorder value) to output values as a float.
        # round each value to six digits.
        output_values.append(round(float(i), 4))

    # if normalized=True (defualt)
    if normalized == True:
        # initialize empty list to populate normalized values
        normalized_IDR_values = []
        # determine the lowest value in the output_values list
        min_IDR = min(output_values)
        # if the lowset value is less than 0, normalize the list by replacing negative values with 0.
        if min_IDR < 0:
            for j in range(0, len(output_values)):
                cur_value = output_values[j]
                if cur_value < 0:
                    normalized_IDR_values.append(0)
                else:
                    normalized_IDR_values.append(round(cur_value, 4))
            # overwrite output_values with normalized_IDR_values (which are now all non-negative).
            output_values = normalized_IDR_values
        # overwrite normalized_IDR_values with an empty list
        normalized_IDR_values = []
        # determine the greatest value in the ouputValues list
        max_IDR = max(output_values)
        # if the greatest value is greater than 1, replace values greater than 1 with 1.
        if max_IDR > 1:
            for k in range(0, len(output_values)):
                cur_value = output_values[k]
                if cur_value > 1:
                    normalized_IDR_values.append(1)
                else:
                    normalized_IDR_values.append(round(cur_value, 4))
            # overwrite output_values with normalized_IDR_values (which are now all less than or equal to 1).
            output_values = normalized_IDR_values
        # return output_values
        return output_values
    # if normalized=False, just return the output_values.
    else:
        return output_values


def meta_predict_hybrid(metapredict_disorder, ppLDDT, cooperative=True):
    """
    This function will ultimately be replaced with a network-based predictor, but for 
    now we predict by using the ppLDDT and metapredict profiles to construct
    a novel hybrid profile.
    

    Parameters
    ------------
    metapredict_disorder : np.ndarrays
        List of per-residue disorder scores generated by metapredict

    ppLDDT : np.ndarrays
        List of per-residue predicted pLDDT scores

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

