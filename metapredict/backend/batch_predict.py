
import torch
import numpy as np

from torch.utils.data import DataLoader
from torch.nn.utils.rnn import pad_sequence

from tqdm import tqdm

from parrot import brnn_architecture
from parrot import encode_sequence

import os
import time
from .metameta_hybrid_predict import predictor_string

from metapredict.backend.data_structures import DisorderObject as _DisorderObject
from metapredict.backend import domain_definition as _domain_definition

# import settings for network
from .py_predictor_v2 import Predictor


# ....................................................................................
#
def build_DisorderObject(s,
                         disorder,
                         disorder_threshold=0.5,
                         minimum_IDR_size=12,
                         minimum_folded_domain=50,
                         gap_closure=10,
                         override_folded_domain_minsize=False,
                         use_slow = False):

    """
    Function which takes a sequence, a disorder profile, and some
    settings and then builds out a DisorderObject from.

    Parameters
    ----------------
    s : str
        Amino acid string

    disorder : np.array
        Array of disordered scores from the prediction

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

    disorder_threshold : float
        Threshold value used for deliniating between disordered and
        and ordered regions

    use_slow : bool
        Flag which, if selected, means we use the older Python-based implementation of
        the domain decomposition algorithm used to excise IDRs from the linear
        disorder profile.

    """

    # extract out disordered domains                 
    return_tuple = _domain_definition.get_domains(s, 
                                                  disorder, 
                                                  disorder_threshold=disorder_threshold,
                                                  minimum_IDR_size=minimum_IDR_size, 
                                                  minimum_folded_domain=minimum_folded_domain,
                                                  gap_closure=gap_closure,
                                                  use_python=use_slow)

    ## assemble the IDRs and FD boundaries
    IDRs = []                    
    for local_idr in return_tuple[1]:
        IDRs.append([local_idr[0], local_idr[1]])

    FDs = []
    for local_fd in return_tuple[2]:
        FDs.append([local_fd[0], local_fd[1]])

    # build an DisorderObject and return it!
    return _DisorderObject(s, disorder, IDRs, FDs, return_numpy=True)


# ....................................................................................
#
def size_filter(inseqs):
    """
    Helper function that breaks down sequences into groups
    where all sequences are the same size.

    Parameters
    ---------------
    inseqs : list
        List of amino acid sequencs

    Returns
    ---------------
    dict
        Returns a dictionary where keys are sequence length and
        values are a list of sequences where all seqs are same length    
    """

    retdict = {}

    for s in inseqs:
        if len(s) not in retdict:
            retdict[len(s)] = []

        retdict[len(s)].append(s)

    return retdict
                               

# old implementation - left for ... reasons ... but should not use
# due to the sequence packing problem
"""
def __batch_predict(sequences, gpuid=00) -> dict:


    # load and setup the network (same code as used by the non-batch version)
    PATH = os.path.dirname(os.path.realpath(__file__))
    predictor_path = f'{PATH}/networks/{predictor_string}'
    brnn_predictor = Predictor(predictor_path, dtype="residues", gpuid=gpuid)

    device = brnn_predictor.device
    model  = brnn_predictor.network

    # hardcoded because this is where metapredict was trained
    batch_size = 32
   
    pred_dict = {}
    
    seq_loader = DataLoader(sequences, batch_size=batch_size, shuffle=False)

    for batch in tqdm(seq_loader):
        # Pad the sequence vector to have the same length as the longest sequence in the batch
        seqs_padded = pad_sequence([encode_sequence.one_hot(seq).float() for seq in batch], batch_first=True)

        # Move padded sequences to device
        seqs_padded = seqs_padded.to(device)

        # Forward pass
        outputs = model.forward(seqs_padded).detach().cpu().numpy()

        # Save predictions
        for j, seq in enumerate(batch):
            pred_dict[seq] = np.squeeze(np.round(np.clip(outputs[j][0:len(seq)], a_min=0, a_max=1),4))
    
    return pred_dict
"""


# ....................................................................................
#
def batch_predict(input_sequences,
                  gpuid=00,
                  return_domains=False,
                  disorder_threshold=0.5,
                  minimum_IDR_size=12,
                  minimum_folded_domain=50,
                  gap_closure=10,
                  override_folded_domain_minsize=False,
                  use_slow = False,
                  print_performance=False):
                  
    """
    Batch prediction for metapredict. IN DEVELOPMENT. DO NOT USE.


    Parameters
    ----------
    sequences : list
        A list of one or more sequences

    gpuid : int, optional
        GPU ID to use for predictions, by default 0. Note if a GPU
        is not available will just use a CPU.

    Returns
    -------
    dict
        sequence, value(s) mapping for the requested predictor.

    Raises
    ------
    SparrowException
        An exception is raised if the requested network is not one of the available options.
    """

    ##
    ## Prepare data by generate a list (sequence_list)
    ## which contains non-redundant sequences 
    ##
    
    if type(input_sequences) is dict:
        mode = 'dictionary'
        seq2id = {}
        for k in input_sequences:
            s = input_sequences[k]
            if s not in seq2id:
                seq2id[s] = [k]
            else:
                seq2id[s].append(k)
        sequence_list = list(seq2id.keys())
        
    elif type(input_sequences) is list:
        mode = 'list'
        sequence_list = list(set(input_sequences))

    else:
        raise Exception('Invalid data type passed into batch_predict - expect a list or a dictionary of sequences')
        

    # code block below is where the per-residue disorder prediction is actually done
    
    ## ....................................................................................
    ##
    ## DO THE PREDICTION
    ##
                

    # load and setup the network (same code as used by the non-batch version)
    PATH = os.path.dirname(os.path.realpath(__file__))
    predictor_path = f'{PATH}/networks/{predictor_string}'
    brnn_predictor = Predictor(predictor_path, dtype="residues", gpuid=gpuid)

    device = brnn_predictor.device
    model  = brnn_predictor.network

    # hardcoded because this is where metapredict was trained
    batch_size = 32
                
    # initialize the return dictionary that maps sequence to
    # disorder profile
    pred_dict = {}

    # build a dictionary where keys are sequence length
    # and values is a list of sequences of that exact length
    size_filtered =  size_filter(sequence_list)

    # for each size of sequence
    start_time = time.time()
    for local_size in size_filtered:

        local_seqs = size_filtered[local_size]
    
        seq_loader = DataLoader(local_seqs, batch_size=batch_size, shuffle=False)

        for batch in seq_loader:
            # Pad the sequence vector to have the same length as the longest sequence in the batch
            seqs_padded = pad_sequence([encode_sequence.one_hot(seq).float() for seq in batch], batch_first=True)

            # Move padded sequences to device
            seqs_padded = seqs_padded.to(device)

            # Forward pass
            outputs = model.forward(seqs_padded).detach().cpu().numpy()

            
            # Save predictions
            for j, seq in enumerate(batch):
                pred_dict[seq] = np.squeeze(np.round(np.clip(outputs[j][0:len(seq)], a_min=0, a_max=1),4))

    end_time = time.time()
    if print_performance:
        print(f"Time taken for predictions on {device}: {end_time - start_time} seconds")


                
    ##
    ## PREDICTION DONE
    ##
    ## ....................................................................................


    # if we've requested IDR domains
    if return_domains:


        # we're going to first build a dictionary to map sequence to DisorderObject - this ensures
        # we only build one DO per sequence, even if we have multiple repetitve sequences
        seq2DisorderObject = {}

        # for each sequence in the prediction dictionary. Note this loop may take a second...
        start_time = time.time()
        for s in pred_dict:
            seq2DisorderObject[s] = build_DisorderObject(s,
                                                         pred_dict[s],
                                                         disorder_threshold=disorder_threshold,
                                                         minimum_IDR_size=minimum_IDR_size, 
                                                         minimum_folded_domain=minimum_folded_domain,
                                                         gap_closure=gap_closure,
                                                         use_slow=use_slow)

        end_time = time.time()
        if print_performance:
            print(f"Time taken for domain decomposition: {end_time - start_time} seconds")

            
        # finally, if we passed in a dictionary then return a dictionary with the same
        # ID mapping (even if two IDs map to the same sequence)
        if mode == 'dictionary':
            return_dict = {}
            
            for s in seq2id:

                # for each ID associated with that sequence, assign the disorder object
                for seq_id in seq2id[s]:
                    return_dict[seq_id] = seq2DisorderObject[s]

            return return_dict

        # and if we passed a list return a list in the same order it came in, even if
        # there are duplicates
        elif mode == 'list':
            return_list = []
            for s in input_sequences:
                return_list.append(seq2DisorderObject[s])

            return return_list

        else:
            raise Exception('How did we get here? What did we do wrong? Is this the darkest timeline? Probably')

    # just return scores with no domains
    else:
    
        if mode == 'dictionary':
            return_dict = {}
            for s in seq2id:
                for seq_id in seq2id[s]:
                    return_dict[seq_id] = [s, pred_dict[s]]                

            return return_dict
        elif mode == 'list':
            return_list = []
            for s in input_sequences:
                return_list.append([s, pred_dict[s]])

            return return_list

        else:
            raise Exception('How did we get here? What did we do wrong? Is this the darkest timeline? Definitely')
            
    

