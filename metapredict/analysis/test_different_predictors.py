# code to carry out the caid analsis for Disorder PDB dataset. 

"""
#  This is commented out because it requires sklearn. Given that none of the stuff
#  in the analysis part of metapredict is necessary for users, I'm leaving
#  stuff back here commenting out to avoid addint sklearn as another dependency.  

import os
import math
import numpy as np

from metapredict.backend.predictor import predict, predict_pLDDT
from metapredict.backend.creating_V2_and_V3_scores import meta_predict_hybrid_v3
from metapredict.backend.network_parameters import metapredict_networks, pplddt_networks
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, precision_recall_curve

def read_caid_seq_disorder(caid_file='caid1_and_2_disorder_pdb.fasta'):
    '''
    function to read in the modified caid 
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
    caid_seqs_scores = {}
    PATH = os.path.dirname(os.path.realpath(__file__))
    with open(f'{PATH}/{caid_file}', 'r') as fh:
        lines=fh.readlines()
    fh.close()

    # get seqs and lines
    seq_ind=0
    for n in range(0, len(lines),3):
        caid_seqs_scores[lines[n].strip()]={'sequence':lines[n+1].strip(), 'scores':lines[n+2].strip()}
    return caid_seqs_scores

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

def read_caid_scores_with_actual_plddt():
    '''
    function that reads in the caid scores that we had plddt information for. 
    
    Returns
    --------
    final_seqs : dict
        dictionary with 'v3_input' as one key and 'caid' as the other. 
        the 'v3_input' has a dictionary as the value that ahs the sequence as the key
        and the plddt scores as the value. The 'caid' key has the sequence as the key
        and the caid scores as the value. 
    '''
    # read in the file that is a tsv with sequence \t caid values \t plddt scores
    PATH = os.path.dirname(os.path.realpath(__file__))
    with open(f'{PATH}/seq_caid_plddt.tsv', 'r') as fh:
        lines=fh.read().split('\n')
    fh.close()

    # format the dict. 
    seqs_to_caid={}
    seqs_to_plddt={}
    for line in lines:
        if line != '':
            seq, caid, plddt = line.split('\t')
            # need to format plddt as a list of floats
            temp=[]
            for v in plddt.split():
                if v != '':
                    temp.append(float(v))
            plddt=temp
            seqs_to_caid[seq]=caid
            seqs_to_plddt[seq]=plddt
    return {'v3_input':seqs_to_plddt, 'caid':seqs_to_caid}


def calculate_stats_testing_actual_plddt():
    '''
    Calculate the AUC, APS, and F1 max

    Parameters
    ----------
    None

    Returns
    -------
    dict:
        dict with AUC, APS, and MCC as keys
    '''

    # set cutoff for binary scores
    cutoff=0.5

    # get dict with sequences as the keys and plddt scores / caid scores as the values
    get_caid_plddt = read_caid_scores_with_actual_plddt()
    seq_to_plddt = get_caid_plddt['v3_input']
    seq_to_caid = get_caid_plddt['caid']
    
    # do metapredict prediction
    metapredict_vals = meta_predict_hybrid_v3(seq_to_plddt)

    # get linear values for metapredict and caid
    metapredict_linear = []
    caid_linear = ''
    metapredict_binarized=[]
    # iterate through the names so we do everything in the correct order. 
    for seq in metapredict_vals:
        caid_linear = caid_linear + str(seq_to_caid[seq])
        metapredict_linear.extend(metapredict_vals[seq])
        temp=[]
        for i in metapredict_vals[seq]:
            if i < 0.5:
                temp.append(0)
            else:
                temp.append(1)
        metapredict_binarized.extend(temp)

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

    return {'AUC':round(auc,5), 'APS':round(aps,5), 'MCC':round(mcc,5)}

def get_me_the_caid_seqs():
    '''
    Function just for Jeff. Returns the sequences that
    have known pLDDT values from our dataset and were
    also in the CAID 1 or CAID 2 dataset. 

    Parameters
    ---------
    None

    Returns
    -------
    list:
        Returns the sequences that you want as a list. 
    '''
    seq_dict=read_caid_scores_with_actual_plddt()['caid']
    return list(seq_dict.keys())

def calculate_stats_custom_disorder(seq_to_disorder_scores_dict, cutoff=0.5):
    '''
    Calculate the AUC, APS, and F1 max

    Parameters
    ----------
    seq_to_disorder_scores_dict : dict
        dict with the sequence as the key and your disorder scores as the values.

    cutoff : float
        Value that if above is considered disordered

    Returns
    -------
    dict:
        dict with AUC, APS, and MCC as keys
    '''

    # get dict with sequences as the keys and plddt scores / caid scores as the values
    get_caid_plddt = read_caid_scores_with_actual_plddt()
    seq_to_caid = get_caid_plddt['caid']

    # get linear values for metapredict and caid
    disorder_linear = []
    caid_linear = ''
    disorder_binarized=[]
    # iterate through the names so we do everything in the correct order. 
    for seq in seq_to_disorder_scores_dict:
        caid_linear = caid_linear + str(seq_to_caid[seq])
        disorder_linear.extend(seq_to_disorder_scores_dict[seq])
        temp=[]
        for i in seq_to_disorder_scores_dict[seq]:
            if i < cutoff:
                temp.append(0)
            else:
                temp.append(1)
        disorder_binarized.extend(temp)

    # now filter out the '-' values in caid, take out those values from metapredict. 
    caid_filtered=[]
    metapredict_filtered=[]
    metapredict_binarized_filtered=[]
    for i, c in enumerate(caid_linear):
        if c != '-':
            caid_filtered.append(int(c))
            metapredict_filtered.append(float(disorder_linear[i]))
            metapredict_binarized_filtered.append(int(disorder_binarized[i]))

    # make sure we have the same lengths
    if len(caid_filtered)!=len(metapredict_filtered):
        raise Exception(f"Length of caid_filtered ({len(caid_filtered)}) does not match length of metapredict_filtered ({len(metapredict_filtered)}).")

    auc = roc_auc_score(caid_filtered, metapredict_filtered)
    aps = average_precision_score(caid_filtered, metapredict_filtered)
    mcc = calc_mcc(metapredict_binarized_filtered, caid_filtered)

    return {'AUC':round(auc,5), 'APS':round(aps,5), 'MCC':round(mcc,5)}


"""