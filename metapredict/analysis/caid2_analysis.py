# code to carry out the caid2 analsis for Disorder PDB dataset. 

import os
import numpy as np
from metapredict.backend.predictor import predict, predict_pLDDT
from metapredict.backend.network_parameters import metapredict_networks, pplddt_networks
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, precision_recall_curve
import math
import matplotlib.pyplot as plt

def read_caid2_seq_disorder(caid_file='caid1_and_2_disorder_pdb.fasta'):
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
    with open(f'{PATH}/{caid_file}', 'r') as fh:
        lines=fh.readlines()
    fh.close()

    # get seqs and lines
    seq_ind=0
    for n in range(0, len(lines),3):
        caid2_seqs_scores[lines[n].strip()]={'sequence':lines[n+1].strip(), 'scores':lines[n+2].strip()}
    return caid2_seqs_scores
    
def get_metapredict_scores(caid2_seqs_scores, version, cutoff=None, plddt=False):
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
    if plddt==False:
        if version not in list(metapredict_networks.keys()):
            raise Exception(f"Version {version} not found in metapredict_networks. Please choose from {list(metapredict_networks.keys())}")
    else:
        if version not in list(pplddt_networks.keys()):
            raise Exception(f"Version {version} not found in metapredict_networks. Please choose from {list(pplddt_networks.keys())}")
    # get cutoff
    if cutoff==None:
        if plddt==False:
            cutoff = metapredict_networks[version]['parameters']['disorder_threshold']
        else:
            cutoff=0.5
    
    # first parse out the scores from caid2_seqs_scores
    caid2_seqs = {}
    for k in caid2_seqs_scores:
        caid2_seqs[k] = caid2_seqs_scores[k]['sequence']
    
    # now get metapredict predictions.
    if plddt==False:
        metapredict_scores = predict(caid2_seqs, version=version)
    else:
        metapredict_scores = predict_pLDDT(caid2_seqs, version=version, return_as_disorder_score=True)
    
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



def calc_mcc(metapredict_scores, caid_scores):
    '''
    parameters
    -----------
    true_positive : Int
        number of true positives (stuff that was predicted to be disordered
        and was in fact disordered)

    false_positive : Int
        number of false positives (stuff that was predicted to be disordered
        but in fact was annotated as not disordered)

    true_negative : Int
        number of times the predictor predicted something to be ordered and 
        the residue was in fact ordered

    false_negaitve : Int
        number of times the predictor predicted somthing to be ordered
        and the residue was in fact disordered
    
    returns
    -------
    mcc_value : float
        The matthews correlation coefficient value as defined in https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4406047/
    '''
    true_positive=0
    false_positive=0
    true_negative=0
    false_negative=0
    for i in range(0, len(metapredict_scores)):
        predicted=metapredict_scores[i]
        actual=caid_scores[i]
        if predicted==1 and actual==1:
            true_positive=true_positive+1
        elif predicted==1 and actual==0:
            false_positive=false_positive+1
        elif predicted==0 and actual==0:
            true_negative=true_negative+1
        elif predicted==0 and actual==1:
            false_negative=false_negative+1

    numerator = ((true_positive * true_negative) - (false_positive * false_negative))
    denomenator_before_square = ((true_positive+false_positive)*(true_negative+false_positive)*(true_positive+false_negative)*(true_negative+false_negative))
    denomenator = math.sqrt(denomenator_before_square)
    mcc_value = numerator / denomenator
    return mcc_value

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
    metapredict_binarized=[]
    # iterate through the names so we do everything in the correct order. 
    for name in caid_vals:
        caid_linear = caid_linear + str(caid_vals[name]['scores'])
        metapredict_linear.extend(metapredict_vals[name]['scores'])
        metapredict_binarized.extend(metapredict_vals[name]['binary'])
        
    
    # now filter out the '-' values in caid, take out those values from metapredict. 
    caid_filtered=[]
    metapredict_filtered=[]
    metapredict_binarized_filtered=[]
    for i, c in enumerate(caid_linear):
        if c != '-':
            caid_filtered.append(int(c))
            metapredict_filtered.append(float(metapredict_linear[i]))
            metapredict_binarized_filtered.append(int(metapredict_binarized[i]))

    # make sure we have the same lengths
    if len(caid_filtered)!=len(metapredict_filtered):
        raise Exception(f"Length of caid_filtered ({len(caid_filtered)}) does not match length of metapredict_filtered ({len(metapredict_filtered)}).")

    auc = roc_auc_score(caid_filtered, metapredict_filtered)
    aps = average_precision_score(caid_filtered, metapredict_filtered)
    mcc = calc_mcc(metapredict_binarized_filtered, caid_filtered)

    return {'AUC':round(auc, 5), 'APS':round(aps, 5), 'MCC':round(mcc,5)}

def get_individual_accuracy(version, cutoff=None, plddt=False):
    # set version to version.upper()
    version=version.upper()
    # get cutoff
    if cutoff==None:
        if plddt==False:
            cutoff = metapredict_networks[version]['parameters']['disorder_threshold']
        else:
            cutoff=0.5

    # get caid dict. 
    caid_vals = read_caid2_seq_disorder()
    # do metapredict prediction
    metapredict_vals = get_metapredict_scores(caid_vals, version, cutoff=cutoff, plddt=plddt)
    # get linear values for metapredict and caid
    metapredict_linear_error={}
    metapredict_binarized_error={}
    # iterate through the names so we do everything in the correct order. 
    for name in caid_vals:
        caid_linear = str(caid_vals[name]['scores'])
        cur_sequence = metapredict_vals[name]['sequence']
        metapredict_scores=metapredict_vals[name]['scores']
        metapredict_binarized=metapredict_vals[name]['binary']
        error=0
        tot_scores=0
        for i in range(0, len(caid_linear)):
            if caid_linear[i] != '-':
                tot_scores+=1
                if caid_linear[i] != str(metapredict_binarized[i]):
                    error+=1
        metapredict_binarized_error[error/tot_scores]=cur_sequence
    return metapredict_binarized_error

