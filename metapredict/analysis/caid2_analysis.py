# code to carry out the caid2 analsis for Disorder PDB dataset. 

import os
import numpy as np
from metapredict.backend.predictor import predict
from metapredict.backend.predictor import metapredict_networks
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, precision_recall_curve

def read_caid2_seq_disorder():
    '''
    function to read in the modified Caid2 
    fasta file that includes a header, the
    ID, the sequence, and then the scores as
    1 = disorder, 0 = not disordered, and 
    - = not assessed.

    Returns
    --------
    seqs : dict
        dictionary of sequences and scores,
        keyed by ID
    '''
    caid2_seqs_scores = {}
    PATH = os.path.dirname(os.path.realpath(__file__))
    with open(f'{PATH}/caid2_disorder_pdb.fasta', 'r') as fh:
        lines=fh.readlines()
    fh.close()

    # get seqs and lines
    seq_ind=0
    for n in range(0, len(lines),3):
        caid2_seqs_scores[lines[n].strip()]={'sequence':lines[n+1].strip(), 'scores':lines[n+2].strip()}
    return caid2_seqs_scores
    
def get_metapredict_scores(caid2_seqs_scores, version, cutoff=None):
    '''
    function to get the metapredict scores that match
    to each sequence in the caid2 dataset.

    Parameters
    -----------
    caid2_seqs_scores : dict
        dictionary of sequences and scores,
        keyed by ID
    version : str
        version of metapredict to use
    cutoff : float
        cutoff to use for the metapredict version

    Returns
    --------
    seqs : dict
        dictionary of sequences raw scores, and binary scores
        keyed by ID.
    '''
    # Make sure testing compatible version
    version=version.upper()
    if version not in list(metapredict_networks.keys()):
        raise Exception(f"Version {version} not found in metapredict_networks. Please choose from {list(metapredict_networks.keys())}")
   
    # get cutoff
    if cutoff==None:
        cutoff = metapredict_networks[version]['parameters']['disorder_threshold']
    
    # first parse out the scores from caid2_seqs_scores
    caid2_seqs = {}
    for k in caid2_seqs_scores:
        caid2_seqs[k] = caid2_seqs_scores[k]['sequence']
    
    # now get metapredict predictions.
    metapredict_scores = predict(caid2_seqs, network=version)
    
    # now make metapredict scores dict
    results={}
    for s in metapredict_scores:
        name=s
        sequence=metapredict_scores[s][0]
        scores=metapredict_scores[s][1]
        binary_scores=np.array(scores)
        binary_scores[binary_scores<cutoff] = 0
        binary_scores[binary_scores>=cutoff] = 1
        results[name] = {'sequence':sequence, 'scores':scores, 'binary':binary_scores.astype(int).tolist()}
    return results

def calculate_stats(version='V2', cutoff=None):
    """
    Calculate the AUC, APS, and F1 max

    Parameters
    ----------
    version : str
        the version of metapredict to use as a string

    Returns
    -------
    auc:  float
        Area Under the ROC Curve
    """
    # set version to version.upper()
    version=version.upper()
    # get cutoff
    if cutoff==None:
        cutoff = metapredict_networks[version]['parameters']['disorder_threshold']

    # get caid dict. 
    caid_vals = read_caid2_seq_disorder()
    # do metapredict prediction
    metapredict_vals = get_metapredict_scores(caid_vals, version, cutoff=cutoff)
    # get linear values for metapredict and caid
    metapredict_linear = []
    caid_linear = ''
    # iterate through the names so we do everything in the correct order. 
    for name in caid_vals:
        caid_linear = caid_linear + str(caid_vals[name]['scores'])
        metapredict_linear.extend(metapredict_vals[name]['scores'])
    
    # now filter out the '-' values in caid, take out those values from metapredict. 
    caid_filtered=[]
    metapredict_filtered=[]
    for i, c in enumerate(caid_linear):
        if c != '-':
            caid_filtered.append(int(c))
            metapredict_filtered.append(float(metapredict_linear[i]))

    # make sure we have the same lengths
    if len(caid_filtered)!=len(metapredict_filtered):
        raise Exception(f"Length of caid_filtered ({len(caid_filtered)}) does not match length of metapredict_filtered ({len(metapredict_filtered)}).")

    auc = roc_auc_score(caid_filtered, metapredict_filtered)
    aps = average_precision_score(caid_filtered, metapredict_filtered)

    return {'AUC':auc, 'APS':aps}

