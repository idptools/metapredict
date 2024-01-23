#!/usr/bin/env python
"""
Functionality previously scattered across various different modules. 
This holds all of the functionality for disorder prediction. 
This includes batch and single sequence. 
"""
# local imports
from metapredict.backend.data_structures import DisorderObject as _DisorderObject
from metapredict.backend import domain_definition as _domain_definition
from metapredict.backend.network_parameters import metapredict_networks
from metapredict.backend import encode_sequence
from metapredict.backend import architectures
from metapredict.metapredict_exceptions import MetapredictError

# other imports
import os
import time
import numpy as np
import torch
from torch.utils.data import DataLoader
from torch.nn.utils.rnn import pad_sequence
from packaging import version
from tqdm import tqdm

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

def predict(inputs,
            network='V3',
            gpuid=0,
            normalized=True,
            return_domains=False,
            disorder_threshold=None,
            round_values=True,
            return_numpy=True,
            minimum_IDR_size=12,
            minimum_folded_domain=50,
            gap_closure=10,
            override_folded_domain_minsize=False,
            use_slow = False,
            print_performance=False,
            show_progress_bar = True):
    """
    Batch mode predictor which takes advantage of PyTorch
    parallelization such that whether it's on a GPU or a 
    CPU, predictions for a set of sequences are performed
    rapidly.

    Parameters
    ----------
    inputs : string list or dictionary
        An individual sequence or a collection of sequences 
        that are presented either as a list of sequences or 
        a dictionary of key-value pairs where values are sequences.

    network : string
        The network to use for prediction. Default is V3.
        Options incllude V1, V2, or V3. 

    gpuid : int 
        Identifier for the GPU being requested. Note that if
        this is left unset the code will use the first GPU available
        and if none is available will default back to CPU; in 
        general it is recommended to not try and set this unless
        there's a specific reason why a specific GPU should be
        used.

    normalized : bool
        Whether or not to normalize disorder values to between 0 and 1. 
        Default : True

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
        Default is set to None because there are different threshold
        values depending on the network (V1 = 0.42, V2=0.5). You can
        override this value. 

    round_values : bool
        Whether to round the values to 4 decimal places. 
        Default : True

    return_numpy : bool
        Whether to return a numpy array or a list for single predictions. 
        Default : True

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
    MetapredictError
        An exception is raised if the requested network is not one of the available options.
    """
    # check network chosen
    if network not in metapredict_networks:
        raise MetapredictError(f'Network {network} not available. Available networks are {metapredict_networks.keys()}')
    else:
        net = metapredict_networks[network]

    # figure out some stuff.
    if disorder_threshold is None:
        disorder_threshold = net['parameters']['disorder_threshold']


    # load and setup the network (same code as used by the non-batch version)
    PATH = os.path.dirname(os.path.realpath(__file__))
    predictor_path = f"{PATH}/networks/{net['weights']}"
    # get params
    params=net['parameters']

    # see if we can use a GPU
    if torch.cuda.is_available():
        device_string=f'cuda:{gpuid}'
    else:
        device_string = 'cpu'

    # set device
    device=torch.device(device_string)

    # load network. We do this differently depending on if we used
    # pytorch or pytorch-lightning to make the network. 
    if params['used_lightning']==False:
        model=architectures.BRNN_MtM(input_size=params['input_size'], 
            hidden_size=params['hidden_size'], num_layers=params['num_layers'], 
            num_classes=params['num_classes'], device=device)
        network=torch.load(predictor_path, map_location=device)
        model.load_state_dict(network)
       
    else:
        # if it's a pytorch-lightning, we can just use load_from_checkpoint
        model=architectures.BRNN_MtM_lightning
        model = model.load_from_checkpoint(predictor_path)

    #model.load_state_dict(network)
    # set to eval mode
    model.eval()

    # make sure network is on correct device. 
    model.to(device)

    # if we want to print the performance, start tracking time per prediction. 
    if print_performance:
        start_time = time.time()

    # now we can start up the predictions. 
    # if a single prediction, we can just ignore the batch stuff. 
    if isinstance(inputs, str)==True:
        # encode the sequence
        seq_vector = encode_sequence.one_hot(inputs)
        seq_vector = seq_vector.view(1, len(seq_vector), -1)

        # get output values from the seq_vector based on the network (brnn_network)
        with torch.no_grad():
            outputs = model(seq_vector.float()).detach().numpy()[0]

        # Take care of rounding and normalization
        if normalized == True and round_values==True:
            outputs=np.round(np.clip(outputs, a_min=0, a_max=1),4)
        elif normalized==True and round_values==False:
            outputs=np.clip(outputs, a_min=0, a_max=1)
        elif normalized==False and round_values==True:
            outputs=np.round(outputs, 4)
        # if both ==False, we don't need to do anything. 
        
        # make list if user wants a list instead of a np.array
        if return_numpy==False:
            if round_values==True:
                # need to round again because the np.round doesn't 
                # keep the rounded values when we convert to list. 
                outputs = [round(x, 4) for x in outputs.flatten()]
            else:
                # otherwise just return the flattened array as a list. 
                outputs=outputs.flatten().tolist()
        # if printing performance
        if print_performance:
            end_time = time.time()
            print(f"Time taken for predictions on {device}: {end_time - start_time} seconds") 

        # see if to build disorder_domsins
        if return_domains:
            outputs= build_DisorderObject(inputs, 
                                            outputs,
                                            disorder_threshold=disorder_threshold,
                                            minimum_IDR_size=minimum_IDR_size, 
                                            minimum_folded_domain=minimum_folded_domain,
                                            gap_closure=gap_closure,
                                            use_slow=use_slow)

        # return the output
        return outputs

    else:
        # otherwise we need to do batch predictions. 
        ## Prepare data by generate a list (sequence_list)
        ## which contains non-redundant sequences 
        ##   
        if isinstance(inputs, dict):
            mode = 'dictionary'
            seq2id = {}
            for k in inputs:
                s = inputs[k]
                if s not in seq2id:
                    seq2id[s] = [k]
                else:
                    seq2id[s].append(k)
            sequence_list = list(seq2id.keys())
        elif isinstance(inputs, list):
            mode = 'list'
            sequence_list = list(set(inputs))
        else:
            raise Exception('Invalid data type passed into batch_predict - expect a list or a dictionary of sequences')
        
        # initialize the return dictionary that maps sequence to
        # disorder profile
        pred_dict = {}

        # Here, we systematically subdivide the sequences into groups 
        # where they're all the same length in a given megabatch, meaning we don't
        # need to pad. This works well in earlier version or torch, but is not optimal
        # in that the effective batch size ends up being 'size-collect' for every uniquely-lengthed
        # sequence.

        # build a dictionary where keys are sequence length
        # and values is a list of sequences of that exact length
        size_filtered =  size_filter(sequence_list)

        # set progress bar info
        loop_range = tqdm(size_filtered) if show_progress_bar else size_filtered

        # iterate through local size
        for local_size in loop_range:
            local_seqs = size_filtered[local_size]
            # load the data
            seq_loader = DataLoader(local_seqs, batch_size=params['batch_size'], shuffle=False)

            # iterate through batches in seq_loader
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

                    if normalized==True and round_values==True:
                        prediction=np.squeeze(np.round(np.clip(outputs[j][0:len(seq)], a_min=0, a_max=1),4))
                    elif normalized==True and round_values==False:
                        prediction=np.squeeze(np.clip(outputs[j][0:len(seq)], a_min=0, a_max=1))
                    elif normalized==False and round_values==True:
                        prediction=np.squeeze(np.round(outputs[j][0:len(seq)]))
                    else:
                        prediction=np.squeeze(outputs[j][0:len(seq)])

                    # make list if user wants a list instead of a np.array
                    if return_numpy==False:
                        if round_values==True:
                            # need to round again because the np.round doesn't 
                            # keep the rounded values when we convert to list. 
                            prediction = [round(x, 4) for x in prediction.flatten()]
                        else:
                            # otherwise just return the flattened array as a list. 
                            prediction=prediction.flatten().tolist()

                    # see if we need to make prediction a list
                    pred_dict[seq] = prediction


        # if printing performance
        if print_performance:
            end_time = time.time()
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
                for s in inputs:
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
                for s in inputs:
                    return_list.append([s, pred_dict[s]])

                return return_list

            else:
                raise Exception('How did we get here? What did we do wrong? Is this the darkest timeline? Definitely')




