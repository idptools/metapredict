"""
BELOW IS CODE THAT SHOULD BE KEPT GOING FORWARD FOR REPRODUCIBILITY!

The code below was basically used to make the scores used to make
the V2 and V3 networks. 

This code was originally for the V1 metapredict predictor. It was based 
partly on code from Dan Griffith's IDP-Parrot from the Holehouse lab
(specifically the test_unlabeled_data function in train_network.py). However,
the code was modified, so if there's anything that's not great looking code,
you can probably assume it was Ryan's and not Dan's.

The metapredict V2 and V3 networks were created by training on what we 
call 'meta-hybrid scores'. These cores used predicted pLDDT scores and
legacy metapredict (V1) disorder scores as the input values. This 
module should be kept going forward so we can reproduce how the V2 and 
V3 networks were trained.
"""

# import local modules
from metapredict.backend.predictor import predict
import alphaPredict as alpha

# import everything else
import sys
import os
import numpy as np



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
    ppLDDT = alpha.predict(sequence)

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

