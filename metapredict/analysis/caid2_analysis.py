# code to carry out the caid2 analsis for Disorder PDB dataset. 

'''
Some code to test accuracy of new networks. Only the PDB disorder
dataset from CAID. Can do CAID1, CAID2, or CAID 1 and 2. This isn't the
best code because it's really for testing purposes and isn't supposed to be user
facing.
'''


"""
#  This is commented out because it requires sklearn. Given that none of the stuff
#  in the analysis part of metapredict is necessary for users, I'm leaving
#  stuff back here commenting out to avoid addint sklearn as another dependency. 

import os
import numpy as np
from metapredict.backend.predictor import predict, predict_pLDDT
from metapredict.backend.network_parameters import metapredict_networks, pplddt_networks
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, precision_recall_curve
import math
import matplotlib.pyplot as plt

def read_caid2_seq_disorder(caid_file='caid2_disorder_pdb.fasta'):
    '''
    
    # caid1_and_2_disorder_pdb

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
    

def moving_average(scores, window_size):
    '''
    Smooths an array of scores over a user-specified sliding window size.

    Parameters:
        scores (array-like): Array of scores to be smoothed.
        window_size (int): Size of the sliding window for smoothing.

    Returns:
        smoothed_scores (ndarray): Smoothed scores with the same length as the input array.
    '''
    if window_size % 2 == 0:
        raise ValueError("Window size must be an odd number.")

    half_window = window_size // 2
    pad_width = ((half_window, half_window),)  # Pad equally on both sides
    padded_scores = np.pad(scores, pad_width, mode='reflect') 
    smoothed_scores = np.convolve(padded_scores, np.ones(window_size) / window_size, mode='valid')
    return smoothed_scores


def stretch(scores, base=0.1, top=0.95): 
    scores= (scores - base)*(1/(top-base))
    scores=np.where(scores<0, 0, scores)
    scores=np.where(scores>1, 1, scores)
    return scores



def get_metapredict_scores(caid2_seqs_scores, version, cutoff=None, plddt=False, smoothing=None, stretch_scores=False):
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
    smoothing : int
        whether to smooth scores over some window. Default=None (no smoothing)
    stretch_scores : bool
        whether to stretch the scores

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

    if stretch_scores==True:
        for prot_name in metapredict_scores:
            scores=metapredict_scores[prot_name][1]
            stretched_scores = stretch(scores)
            metapredict_scores[prot_name][1] = stretched_scores

    # smooth
    if smoothing!=None:
        allscores=[]
        for prot_name in metapredict_scores:
            scores=metapredict_scores[prot_name][1]
            smoothed_scores = moving_average(scores, smoothing)
            metapredict_scores[prot_name][1] = smoothed_scores
            allscores.extend(smoothed_scores)

        
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

def calculate_stats(version='V2', cutoff=None, smoothing=None, stretch_scores=False,
    evaluation_fasta='caid2_disorder_pdb.fasta'):
    '''
    Calculate the AUC, APS, and F1 max

    Parameters
    ----------
    version : str
        the version of metapredict to use as a string

    cutoff : float
        the cutoff value if you want to hardcode it.
        Otherwise uses default

    smoothing : int
        window over which to smoooth scores.
        default is to not smooth

    stretch_scores : bool
        Whether to stretch the scores to increase the dynamic range closer to 0 to 1

    evaluation_fasta : str
        the fasta file to use for evaluation. 
        Default is the caid2_disorder_pdb.fasta

    whether to stretch the scores

    Returns
    -------
    auc:  float
        Area Under the ROC Curve
    '''
    # set version to version.upper()
    version=version.upper()
    # get cutoff
    if cutoff==None:
        cutoff = metapredict_networks[version]['parameters']['disorder_threshold']

    # get caid dict. 
    caid_vals = read_caid2_seq_disorder(caid_file=evaluation_fasta)
    # do metapredict prediction
    metapredict_vals = get_metapredict_scores(caid_vals, version, cutoff=cutoff, smoothing=smoothing, stretch_scores=stretch_scores)
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




def print_current_network_accuracy(evaluation='all', additional_networks=None):
    '''
    Function to print out the current network accuracies. Just a nice
    one-liner to have sitting around. 

    Parameters
    -----------
    evaluation : str
        the evaluation set to use. Default is 'caid2'
        Options included 'caid1', 'caid2', and 'all'

    additional_networks : list
        additional networks to test. Must be in the 
        metapredict_networks dictionary in network_parameters.py
    '''
    # list of current networks
    nets=['V1', 'V2', 'V3']

    # if we want to test additional networks in the future, do that here. 
    if additional_networks!=None:
        nets.extend(additional_networks)

    # set string for what analysis we are doing
    if evaluation.lower() == 'all':
        evaluation_str='CAID1 and CAID2'
        fasta_used = 'caid1_and_2_disorder_pdb.fasta'
    elif evaluation.lower() == 'caid1':
        evaluation_str='CAID1'
        fasta_used = 'caid1_disorder_pdb.fasta'
    elif evaluation.lower() == 'caid2':
        evaluation_str='CAID2'
        fasta_used = 'caid2_disorder_pdb.fasta'
    else:
        raise Exception(f"evaluation must be 'all', 'caid1', or 'caid2'. You entered {evaluation}")

    # start building string to print
    eval_string = f'{evaluation_str}\n'
    for i in range(0, len(evaluation_str)):
        eval_string = eval_string + '='
    eval_string = eval_string + '\n'

    # add the results for each network 
    for net in nets:
        results = calculate_stats(version=net)
        temp=''
        for result in results:
            temp = temp + f'{result} = {results[result]}, '
        eval_string = eval_string + (f'{net}: {temp[:len(temp)-2]}\n')    

    # print the results
    print(eval_string)

"""