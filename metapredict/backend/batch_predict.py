import torch
import numpy as np

from packaging import version
from tqdm import tqdm


from torch.utils.data import DataLoader
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence, pad_packed_sequence

#from tqdm import tqdm

from metapredict.backend import encode_sequence
from metapredict.backend import brnn_architecture

import os
import time
from metapredict.backend.metameta_hybrid_predict import predictor_string

from metapredict.backend.data_structures import DisorderObject as _DisorderObject
from metapredict.backend import domain_definition as _domain_definition

# import settings for network
from metapredict.backend.py_predictor_v2 import Predictor


## Import advanced batch dispatching available in torch 1.11 or higher
##
##
if version.parse(torch.__version__) >= version.parse("1.11.0"):
    from torch.nn.utils.rnn import unpad_sequence
    


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
                               

# ....................................................................................
#
def batch_predict(input_sequences,
                  gpuid=0,
                  return_domains=False,
                  disorder_threshold=0.5,
                  minimum_IDR_size=12,
                  minimum_folded_domain=50,
                  gap_closure=10,
                  override_folded_domain_minsize=False,
                  use_slow = False,
                  print_performance=False,
                  force_mode = None,
                  show_progress_bar = True):
                 
                  
    """
    Batch mode predictor which takes advantage of PyTorch
    parallelization such that whether it's on a GPU or a 
    CPU, predictions for a set of sequences are performed
    rapidly.

    Batch mode was implemented in metapredict V2-FF, as is 
    optimized for the hybrid network first released in V2.
    As such a few options are not available for batch mode

    which include:

    * legacy - you cannot predict legacy metapredict scores with batch_mode
             
    * normalize - all predictions are automatically normalized to fall between 0 and 1
            
    * return_numpy - all disorder scores are returned as numpy arrays.
                   
    Note also that batch mode uses 32-bit float vectors
    whereas non-batch uses 64-bit float vectors, so the
    precise values in batch vs. non-batch may differ 
    slighly, however this is a numerical precision difference,
    such that values by both methods are always within
    1e-3 of one another.

    Note the reason to use this function instead of 
    meta.predict_disorder_batch is here there are a few 
    additional arguments one can pass in which may be useful.

    Parameters
    ----------
    input_sequences : list or dictionary
        A collection of sequences that are presented either
        as a list of sequences or a dictionary of key-value
        pairs where values are sequences.

    gpuid : int 
        Identifier for the GPU being requested. Note that if
        this is left unset the code will use the first GPU available
        and if none is available will default back to CPU; in 
        general it is recommended to not try and set this unless
        there's a specific reason why a specific GPU should be
        used

    return_domains : bool
        Flag which, if set to true, means we return DisorderDomain
        objects instead of simply the disorder scores. These
        domain objects include the boundaries between IDRs and 
        folded domains, the disorder scores, and the individual
        sequences for IDRs and folded domains. This adds a small
        amount of overhead to the prediction, but typically only
        increase prediction time by 10-15%.
    
    disorder_threshold : float
        Used only if return_domains = True.

        Threshold used to deliniate between folded and disordered
        regions. We use a value of 0.5 because predict_disorder_batch
        does not support legacy. 

    minimum_IDR_size : int
        Used only if return_domains = True.

        Defines the smallest possible IDR. This is a hard limit - 
        i.e. we CANNOT get IDRs smaller than this. Default = 12.

    minimum_folded_domain : int
        Used only if return_domains = True.

        Defines where we expect the limit of small folded domains 
        to be. This is NOT a hard limit and functions to modulate
        the removal of large gaps (i.e. gaps less than this size 
        are treated less strictly). Note that, in addition, 
        gaps < 35 are evaluated with a threshold of 
        0.35*disorder_threshold and gaps < 20 are evaluated with 
        a threshold of 0.25*disorder_threshold. These two 
        lengthscales were decided based on the fact that 
        coiled-coiled regions (which are IDRs in isolation) 
        often show up with reduced apparent disorder within IDRs, 
        and but can be as short as 20-30 residues. 
        The folded_domain_threshold is used based on the 
        idea that it allows a 'shortest reasonable' folded domain 
        to be identified. Default=50.

    gap_closure : int
        Used only if return_domains = True.

        Defines the largest gap that would be 'closed'. Gaps here 
        refer to a scenario in which you have two groups of 
        disordered residues seprated by a 'gap' of un-disordered 
        residues. In general large gap sizes will favour larger 
        contigous IDRs. It's worth noting that gap_closure becomes 
        relevant only when minimum_region_size becomes very small 
        (i.e. < 5) because really gaps emerge when the smoothed 
        disorder fit is "noisy", but when smoothed gaps
        are increasingly rare. Default=10.

    override_folded_domain_minsize : bool
        By default this function includes a fail-safe check that
        assumes folded domains really shouldn't be less than 
        35 or 20 residues. However, for some approaches we may 
        wish to over-ride these thresholds to match the passed 
        minimum_folded_domain value. If this flag is set to 
        True this override occurs. This is generally not 
        recommended unless you expect there to be well-defined 
        sharp boundaries which could define small (20-30) 
        residue folded domains. This is not provided as an option 
        in the normal predict_disorder_domains for metapredict. 
        Default = False. 

    use_slow : bool
        Flag which, if passed, means we force a Python 
        implementation of our domain decomposition algorithm 
        instead of the MUCH faster Cython/C implementation. 
        Useful for debugging. Default = False
                
    print_performance : bool
        Flag which means the function prints the time taken 
        for the two stages in the prediction algorithm. Again 
        useful for profiling and debugging. Default = False
    
    force_mode : string
        Default is None. When set as None, chooses the size-collect
        approach.

        Chooses how the sequnces are input for
        batch prediction. In our testing, size-collect is faster
        so it uses that by default. You can also use pack-n-pad
        by specifying 'pack-n-pad' here. 

        size-collect - means we pre-filter sequences into groups where 
        they're all the same length.

        pack-n-pad - involves padding/packing the sequences so that 
        all sequences can be passed in a batchsize of 32. This 
        is only available if pytorch 1.11 or higher is available. 
        In testing, we found that pack-n-pad is about 2x faster than
        size-collect if running on CPU with variable length sequence
        if fewer 5000 sequences. On GPU, size-collect was consistently faster.

    show_progress_bar : bool
        Flag which, if set to True, means a progress bar is printed as 
        predictions are made, while if False no progress bar is printed.
        Default  =  True


    Returns
    -------------
    dict or list

        IF RETURN DOMAINS == FALSE: this function returns either
        a list or a dictionary.
    
        If a list was provided as input, the function returns a list
        of the same length as the input list, where each element is 
        itself a sublist where element 0 = sequence and element 1 is
        a numpy array of disorder scores. The order of the return list
        matches the order of the input list.

        If a dictionary was provided as input, the function returns
        a dictionary, where the same input keys map to values which are
        lists of 2 elements, where element 0 = sequence and element 1 is
        a numpy array of disorder scores.

        IF RETURN DOMAINS == TRUE: this function returns either a list
        or a dictionary.

        If a list was provided as input, the function returns a list
        of the same length as the input list, where each element is 
        a DisorderDomain object. The order of the return list matches 
        the order of the input list.

        If a dictionary was provided as input, the function returns
        a dictionary, where the same input keys map to a DisorderDomain
        object that corresponds to the input dictionary sequence.

    Raises
    ------
    SparrowException
        An exception is raised if the requested network is not one of the available options.
    """

    # define the mode based on torch version or a manual
    # over-ride (for performance testing)
    if force_mode is not None:
        if force_mode not in ['pack-n-pad', 'size-collect']:
            raise Exception("force_mode must be set to 'pack-n-pad', 'size-collect'")
        
        batch_mode = force_mode

        # updated to 2.0.1 in July 2023 due to small numerical instabilities in earlier versions of pack-n-pad
        if version.parse(torch.__version__) < version.parse("2.0.1") and batch_mode == 'pack-n-pad':
            print(f'Warning; batch mode pack-n-pad not supported in PyTorch {torch.__version__}. Requires 2.0.1 or higher. Over-riding and switching to mode=size-collect')
            batch_mode = 'size-collect'
        
    else:
        batch_mode='size-collect'


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

    # make sure we are in eval mode because we are only doing inference.
    model.eval()

    # move model to device. If you don't do this and it goes to GPU, 
    # the input will go to GPU but the model will remain on CPU leading to problems.
    model.to(device)

    # hardcoded because this is where metapredict was trained
    batch_size = 32

    # initialize the return dictionary that maps sequence to
    # disorder profile
    pred_dict = {}

    # if we're in a a version of torch that does not supported unpadding
    if batch_mode == 'size-collect':

        # Mode 'size-collect' means we systematically subdivide the sequences into groups 
        # where they're all the same length in a given megabatch, meaning we don't
        # need to pad. This works well in earlier version or torch, but is not optimal
        # in that the effective batch size ends up being 'size-collect' for every uniquely-lengthed
        # sequence.
        #

        # build a dictionary where keys are sequence length
        # and values is a list of sequences of that exact length
        size_filtered =  size_filter(sequence_list)

        # set progress bar info
        loop_range = tqdm(size_filtered) if show_progress_bar else size_filtered

        # for each size of sequence
        start_time = time.time()
        for local_size in loop_range:

            local_seqs = size_filtered[local_size]
    
            seq_loader = DataLoader(local_seqs, batch_size=batch_size, shuffle=False)

            for batch in seq_loader:
                # Pad the sequence vector to have the same length as the longest sequence in the batch
                seqs_padded = pad_sequence([encode_sequence.one_hot(seq).float() for seq in batch], batch_first=True)

                # Move padded sequences to device
                seqs_padded = seqs_padded.to(device)

                # Forward pass
                with torch.no_grad():
                    outputs = model.forward(seqs_padded).detach().cpu().numpy()
            
                # Save predictions
                for j, seq in enumerate(batch):
                    pred_dict[seq] = np.squeeze(np.round(np.clip(outputs[j][0:len(seq)], a_min=0, a_max=1),4))

    elif batch_mode == 'pack-n-pad':

        # Mode 'pack-n-pad' involves packing/padding and unpacking/unpadding to avoid packing causing
        # errors in prediction, but is only available in pytorch 1.11 or higher. This is definitley
        # the better approach, but we want to avoid a hard-dependency on pytorch 1.11 in metapredict
        # so offer both modes for backwards compatibility.
        
        start_time = time.time()
        seq_loader = DataLoader(sequence_list, batch_size=batch_size, shuffle=False)

        # set progress bar info
        loop_range = tqdm(seq_loader) if show_progress_bar else seq_loader
        
        # iterate through batch
        for batch in loop_range:
            
            # Pad the sequence vector to have the same length as the longest sequence in the batch
            seqs_padded = pad_sequence([encode_sequence.one_hot(seq).float() for seq in batch], batch_first=True)
            
            # get lengths for input into pack_padded_sequence
            lengths = [len(seq) for seq in batch]
            
            # pack up for vacation
            packed_and_padded = pack_padded_sequence(seqs_padded, lengths, batch_first=True, enforce_sorted=False)
            
            # move to device
            packed_and_padded = packed_and_padded.to(device)

            # input packed_and_padded into loaded lstm
            with torch.no_grad():
                packed_output, (ht, ct) = model.lstm.forward(packed_and_padded)
            
            # inverse of pack_padded_sequence
            output, input_sizes = pad_packed_sequence(packed_output, batch_first=True)
            
            # get the outputs by calling fc
            outputs = model.fc(output).cpu()
            
            # get the unpacked, finalized values into the dict.
            for cur_ind, score in enumerate(outputs):
                # first detach, flatten, etc
                cur_score = score.detach().numpy().flatten()
                
                # get the sequence from batch from seq_loader
                cur_seq = batch[cur_ind]
                
                # add to dict
                pred_dict[cur_seq]=np.squeeze(np.round(np.clip(cur_score[0:len(cur_seq)], a_min=0, a_max=1),4))


    # either way we can print performance
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
            
        
