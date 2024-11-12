#!/usr/bin/env python
"""
Functionality previously scattered across various different modules. 
This holds all of the functionality for disorder and pLDDT prediction. 
This includes batch and single sequence. 
Device selection can be carried out from the predict function. 
Output data type also from the predict function. 
"""

# general imports
import os
import re
from packaging import version as packaging_version
import time
import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
import gc

# local imports
from metapredict.backend.data_structures import DisorderObject as _DisorderObject
from metapredict.backend import domain_definition as _domain_definition
from metapredict.backend.network_parameters import metapredict_networks, pplddt_networks
from metapredict.parameters import DEFAULT_NETWORK, DEFAULT_NETWORK_PLDDT
from metapredict.backend import encode_sequence
from metapredict.backend import architectures
from metapredict.metapredict_exceptions import MetapredictError

# ....................................................................................
#
def build_DisorderObject(s,
                         disorder,
                         disorder_threshold=0.5,
                         minimum_IDR_size=12,
                         minimum_folded_domain=50,
                         gap_closure=10,
                         override_folded_domain_minsize=False,
                         use_slow = False, return_numpy=True):

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

    return_numpy : bool
        whether to reutrn np array or not

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
    return _DisorderObject(s, disorder, IDRs, FDs, return_numpy=return_numpy)


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

def check_device(use_device, default_device='cuda'):
    '''
    Function to check the device was correctly set. 
    
    Parameters
    ---------------
    use_device : int or str 
        Identifier for the device to be used for predictions. 
        Possible inputs: 'cpu', 'mps', 'cuda', 'cuda:int', or an int that corresponds to
        the index of a specific cuda-enabled GPU. If 'cuda' is specified and
        cuda.is_available() returns False, instead of falling back to CPU, 
        metapredict will raise an Exception so you know that you are not
        using CUDA as you were expecting. 
        If 'mps' is specified and mps is not available, an exception will be raised.

    default_device : str
        The default device to use if device=None.
        If device=None and default_device != 'cpu' and default_device is
        not available, device_string will be returned as 'cpu'.
        I'm adding this in case we want to change the default architecture in the future. 
        For example, we could make default device 'gpu' where it will check for 
        cuda or mps and use either if available and then otherwise fall back to CPU. 

    Returns
    ---------------
    device_string : str
        returns the device string as a string. 
    '''
    # if use_device is None, check for cuda. 
    if use_device==None:
        # check if default device is available.
        if default_device=='cpu':
            return 'cpu'
        elif default_device=='mps':
            if torch.backends.mps.is_available():
                return default_device
            else:
                return 'cpu'
        elif default_device=='cuda':
            if torch.cuda.is_available():
                return 'cuda'
            else:
                return 'cpu'
        else:
            raise MetapredictError("Default device can only be set to 'cpu', 'mps', or 'cuda'")


    else:  
        # if input is an int, make it a string and then do checks. 
        if isinstance(use_device, int)==True:
            use_device=f'cuda:{use_device}'
        
        # if input is a string (it should be...)
        if isinstance(use_device, str)==True:
            # make use_device lowercase
            use_device=use_device.lower()
            # if CPU specified, use CPU    
            if use_device=='cpu':
                return use_device
            elif use_device=='mps':
                # check if mps is available. 
                if torch.backends.mps.is_available():
                    return use_device
                else:
                    raise MetapredictError('mps was specified, but mps is not available. Be sure you are running a Mac with mps-supported GPUs and a Pytorch version with mps support (>=2.1)')
            elif 'cuda' in use_device:
                # make sure cuda is available.
                if torch.cuda.is_available()==False:
                    error_message = f'{use_device} was specified as the device, but torch.cuda.is_available() returned False.'
                    raise MetapredictError(error_message) 
                if use_device == 'cuda':
                    return use_device
                elif ':' in use_device:
                    # make sure a positive integer is specified 
                    pattern = r"^cuda(:\d+)?$"
                    # if the pattern doesn't match, raise an exception. 
                    if re.match(pattern, str(use_device))==None:
                        error_message = f'{use_device} was specified as the device, but it does not match the pattern of cuda:int where int is a positive integer.'
                        raise MetapredictError(error_message)
                    else:
                        # make sure there are enough devices such that it is possible that the specified device index works. 
                        device_index = int(use_device.split(":")[1])
                        num_devices = torch.cuda.device_count()
                        if device_index >= num_devices:
                            error_message = f'{use_device} was specified as the device, but there are only {num_devices} cuda-enabled GPUs available.\nRemember, GPU indices are 0-indexed, so cuda:0 is for the first GPU and so on.\nThe max device index you can use based on torch.cuda.device_count() is {num_devices-1}.'
                            raise MetapredictError(error_message)
                        return use_device
        else:
            raise MetapredictError("Device can only be set to: None, a string equal to 'cpu', 'mps', 'cuda', 'cuda:int' where int is some positive integer, or an int that is equal to the index of a specific CUDA-enabled GPU")

    # if we made it here, raise error
    raise MetapredictError("There is a problem with the check_device function in metapredict/backend/predictor.py.\nPlease raise an issue because you shouldn't be able to see this message.")

def take_care_of_version(version_input):
    '''
    Function to take care of the version to use when specifying
    the network.

    Parameters
    ---------------
    version_input : int or str
        The version of the network to use.

    Returns
    ---------------
    version : str
        The version of the network to use.
    '''
    # make sure the version is a string
    version_input=str(version_input)

    # now convert over to what we need version to be. 
    if version_input=='legacy':
        version_input='V1'
    
    # if len version is 1, add a 'V' to the front. 
    if len(version_input)==1:
        version_input=f'V{version_input}'

    # make version uppercase
    version_input=version_input.upper()

    return version_input



# function to load model
# A variable to store the loaded model
loaded_models = {}

# gets model. This lets us avoid iteratively loading the model
# because it can check the global dictionary to see if the model
# has already been loaded. 
# if you don't do this, you start getting memory issues
def get_model(model_name, params, predictor_path, device):
    global loaded_models  # Ensure the dictionary is accessible across calls
    
    # Check if the model has already been loaded
    if model_name in loaded_models:
        return loaded_models[model_name]
    
    # If the model hasn't been loaded yet, load it
    if not params['used_lightning']:
        model = architectures.BRNN_MtM(
            input_size=params['input_size'], 
            hidden_size=params['hidden_size'], 
            num_layers=params['num_layers'], 
            num_classes=params['num_classes'], 
            device=device
        )
        network = torch.load(predictor_path, map_location=device, weights_only=True)
        model.load_state_dict(network)
    else:
        model = architectures.BRNN_MtM_lightning.load_from_checkpoint(
            predictor_path, map_location=device
        )

    # Store the loaded model in the dictionary using the model_name as key
    loaded_models[model_name] = model
    return model

# ....................................................................................

def predict(inputs,
            version=DEFAULT_NETWORK,
            use_device=None,
            normalized=True,
            round_values=True,
            return_numpy=True,
            return_domains=False,
            disorder_threshold=None,
            minimum_IDR_size=12,
            minimum_folded_domain=50,
            gap_closure=10,
            override_folded_domain_minsize=False,
            use_slow = False,
            print_performance=False,
            show_progress_bar = False,
            force_disable_batch=False,
            disable_pack_n_pad = False,
            silence_warnings = False,
            default_to_device = 'cuda'):
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

    version : string
        The network to use for prediction. Default is DEFAULT_NETWORK,
        which is defined at the top of /parameters.
        Options currently include V1, V2, or V3. 

    use_device : int or str 
        Identifier for the device to be used for predictions. 
        Possible inputs: 'cpu', 'mps', 'cuda', or an int that corresponds to
        the index of a specific cuda-enabled GPU. If 'cuda' is specified and
        cuda.is_available() returns False, instead of falling back to CPU, 
        metapredict will raise an Exception so you know that you are not
        using CUDA as you were expecting. 
        Default: None
            When set to None, we will check if there is a cuda-enabled
            GPU. If there is, we will try to use that GPU. 
            If you set the value to be an int, we will use cuda:int as the device
            where int is the int you specify. The GPU numbering is 0 indexed, so 0 
            corresponds to the first GPU and so on. Only specify this if you
            know which GPU you want to use. 
            * Note: MPS is only supported in Pytorch 2.1 or later. If I remember
            right it might have been beta supported in 2.0 *.

    normalized : bool
        Whether or not to normalize disorder values to between 0 and 1. 
        Default : True
    
    round_values : bool
        Whether to round the values to 4 decimal places. 
        Default : True

    return_numpy : bool
        Whether to return a numpy array or a list for single predictions. 
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

    force_disable_batch : bool
        Whether to override any use of batch predictions and predict
        sequences individually.
        Default = False

    disable_pack_n_pad : bool
        Whether to disable the use of pack_n_pad in the prediction
        algorithm. This is useful for debugging and profiling. Also gives
        us a way for people to use older versions of torch. 
        Default = False

    silence_warnings : bool
        whether to silence warnings such as the one about compatibility
        to use pack-n-pad due to torch version restrictions. 

    default_to_device : str
        The default device to use if device=None.
        If device=None and default_device != 'cpu' and default_device is
        not available, device_string will be returned as 'cpu'.
        I'm adding this in case we want to change the default architecture in the future. 
        For example, we could make default device 'gpu' where it will check for 
        cuda or mps and use either if available and then otherwise fall back to CPU.

    Returns
    -------------
    DisorderDomain object str dict or list

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
    ##
    ## FIGURE OUT WHAT NETWORK WE ARE USING
    ##
    ## ....................................................................................

    # normalize such that user can input v#, V#, or # to specify the version
    version = take_care_of_version(version)

    # make list of possible network inputs
    possible_networks=['legacy']
    for cur_net in metapredict_networks.keys():
        possible_networks.append(cur_net)
        possible_networks.append(cur_net[-1])  

    # make sure version is in the metapredict networks. 
    if version not in metapredict_networks:
        raise MetapredictError(f'Network {version} not available. Valid inputs to choose a network are {possible_networks}')
    else:
        net = metapredict_networks[version]

    # figure out some stuff.
    if disorder_threshold is None:
        disorder_threshold = net['parameters']['disorder_threshold']

    # load and setup the network (same code as used by the non-batch version)
    PATH = os.path.dirname(os.path.realpath(__file__))
    predictor_path = f"{PATH}/networks/{net['weights']}"
    # get params
    params=net['parameters']

    ##
    ## FIGURE OUT WHERE WE ARE DOING THE PREDICTIONS
    ##
    ## ....................................................................................    

    # if a single sequence, just use cpu. Using GPU for a single sequence would be silly.
    if isinstance(inputs, str)==True:
        device_string='cpu'
    else:
        device_string = check_device(use_device, default_device=default_to_device)

    # set device
    device=torch.device(device_string)

    # see if we need to mess with packing / padding
    if disable_pack_n_pad==False:
        if packaging_version.parse(torch.__version__) < packaging_version.parse("1.11.0"):
            disable_pack_n_pad=True
            # only warn if user hasn't turned off warning. 
            if silence_warnings==False:
                print('Pytorch version is <= 1.11.0. Disabling pack-n-pad functionality. This might slow down predictions.')

    ##
    ## LOAD IN THE NETWORK
    ##
    ## ....................................................................................    

    # load model
    model = get_model(model_name=f'disorder_{version}', 
                        params=params, 
                        predictor_path=predictor_path, 
                        device=device)

    # set to eval mode
    model.eval()

    # make sure network is on correct device. 
    model.to(device)
        
    ##
    ## START PREDICTIONS
    ##
    ## .................................................................................... 

    # now we can start up the predictions. 
    # if a single prediction, we can just ignore the batch stuff. 
    if isinstance(inputs, str)==True:
        # if we want to print the performance, start tracking time per prediction. 
        if print_performance:
            start_time = time.time()        
        
        # encode the sequence
        seq_vector = encode_sequence.one_hot(inputs)    
        seq_vector = seq_vector.to(device)
        seq_vector = seq_vector.view(1, len(seq_vector), -1)

        # get output values from the seq_vector based on the network (brnn_network)
        with torch.no_grad():
            outputs = model(seq_vector.float()).detach().cpu().numpy()[0]

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
                outputs = [round(float(x), 4) for x in outputs.flatten()]
            else:
                # otherwise just return the flattened array as a list. 
                outputs=outputs.flatten().tolist()

        else:
            # if we want a numpy array, we need to make sure it's a 1D array
            outputs=outputs.flatten()

        # print performance
        if print_performance:
            end_time = time.time()
            print(f"Time taken for prediction on {device}: {end_time - start_time} seconds") 


        # see if need to build disorder_domsins
        if return_domains:
            outputs= build_DisorderObject(inputs, outputs, 
                                            disorder_threshold=disorder_threshold,
                                            minimum_IDR_size=minimum_IDR_size, 
                                            minimum_folded_domain=minimum_folded_domain,
                                            gap_closure=gap_closure,use_slow=use_slow,
                                            return_numpy=return_numpy)
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
            raise Exception('Invalid data type passed - expect a single sequence or a list or dictionary of sequences')

        # if we want to print the performance, start tracking time per prediction. 
        if print_performance:
            start_time = time.time()   

        # initialize the return dictionary that maps sequence to
        # disorder profile
        pred_dict = {}

        # check if we are disabling batch predictions. If we are, we need to
        # do all predictions individually
        if force_disable_batch==True:
            tot_num_seqs=len(sequence_list)
            # see if a progress bar is wanted
            if show_progress_bar:
                pbar = tqdm(total=len(sequence_list))
                # set pbar update amount
                pbar_update_amount=int(0.1*tot_num_seqs)
                if pbar_update_amount==0:
                    pbar_update_amount=1
            # iterate through sequence list
            for cur_seq_num, seq in enumerate(sequence_list):
                # encode the sequence
                seq_vector = encode_sequence.one_hot(seq)
                seq_vector = seq_vector.to(device)
                seq_vector = seq_vector.view(1, len(seq_vector), -1)

                # get output values from the seq_vector based on the network (brnn_network)
                with torch.no_grad():
                    outputs = model(seq_vector.float()).detach().cpu().numpy()[0].flatten()

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
                        outputs = [round(float(x), 4) for x in outputs.flatten()]
                    else:
                        # otherwise just return the flattened array as a list. 
                        outputs=outputs.flatten().tolist()

                # add to dict
                pred_dict[seq]=outputs
                # update progress bar
                if show_progress_bar:
                    if cur_seq_num % (pbar_update_amount)==0:
                        pbar.update(pbar_update_amount)

        else:         
            # if we are disabling pack-n-pad functionalitity...
            if disable_pack_n_pad==True:
                # build a dictionary where keys are sequence length
                # and values is a list of sequences of that exact length
                size_filtered =  size_filter(sequence_list)
                
                # set progress bar info
                if show_progress_bar:
                    pbar = tqdm(total=len(size_filtered))

                # iterate through local size
                for local_size in size_filtered:
                    local_seqs = size_filtered[local_size]
                    # load the data
                    seq_loader = DataLoader(local_seqs, batch_size=params['batch_size'], shuffle=False)

                    # iterate through batches in seq_loader
                    for batch in seq_loader:
                        # Pad the sequence vector to have the same length as the longest sequence in the batch
                        seqs_padded = torch.nn.utils.rnn.pad_sequence([encode_sequence.one_hot(seq).float() for seq in batch], batch_first=True)
                        seqs_padded = seqs_padded.to(device)

                        # Forward pass, then send to CPU for numpy rounding / normalization
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
                                    prediction = [round(float(x), 4) for x in prediction.flatten()]
                                else:
                                    # otherwise just return the flattened array as a list. 
                                    prediction=prediction.flatten().tolist()

                            # see if we need to make prediction a list
                            pred_dict[seq] = prediction
                    
                    # update the progress bar
                    if show_progress_bar:
                        pbar.update(1)
            else:
                # sort the seqs by length, makes pack-n-pad stuff more efficient
                sequence_list.sort(key=len, reverse=True)
                # we will be using pack-n-pad.
                # load seqs into DataLoader
                seq_loader = DataLoader(sequence_list, batch_size=params['batch_size'], shuffle=False) 
                num_batches=len(seq_loader)
                
                # set progress bar info if we are going to display it. 
                # have to do this differently because you can't iterate over DataLoader
                # and get tqdm to update. 
                if show_progress_bar:
                    pbar = tqdm(total=num_batches)

                # iterate through each batch
                for batch in seq_loader:
                    # Pad the sequence vector to have the same length as the longest sequence in the batch
                    seqs_padded = torch.nn.utils.rnn.pad_sequence([encode_sequence.one_hot(seq).float() for seq in batch], batch_first=True)
                    lengths = [len(seq) for seq in batch]

                    # pack padded sequences
                    packed_seqs = torch.nn.utils.rnn.pack_padded_sequence(seqs_padded, lengths, batch_first=True, enforce_sorted=True)
                    
                    # move packed seqs to device. 
                    packed_seqs = packed_seqs.to(device)

                    # lstm forward pass.
                    with torch.no_grad():
                        outputs, _ = model.lstm(packed_seqs)

                    # unpack the packed sequence
                    outputs, _ = torch.nn.utils.rnn.pad_packed_sequence(outputs, batch_first=True)

                    # get final outputs by calling fc.
                    if params['used_lightning']==False:
                        outputs = model.fc(outputs)
                    else:
                        outputs = model.layer_norm(outputs)
                        for layer in model.linear_layers:
                            outputs = layer(outputs)
                    
                    # move to cpu
                    outputs = outputs.detach().cpu().numpy()

                    # clean up / normalize
                    if normalized == True and round_values==True:
                        outputs=np.round(np.clip(outputs, a_min=0, a_max=1),4)
                    elif normalized==True and round_values==False:
                        outputs=np.clip(outputs, a_min=0, a_max=1)
                    elif normalized==False and round_values==True:
                        outputs=np.round(outputs, 4)                
                    
                    # get individual seqs ignoring padded parts. 
                    for seq_num, length in enumerate(lengths):
                        curoutput=outputs[seq_num][0:length].flatten()
                        seq = batch[seq_num]
                    
                        # make list if user wants a list instead of a np.array
                        if return_numpy==False:
                            if round_values==True:
                                # need to round again because the np.round doesn't 
                                # keep the rounded values when we convert to list. 
                                curoutput = [round(float(x), 4) for x in curoutput.flatten()]
                            else:
                                # otherwise just return the flattened array as a list. 
                                curoutput=curoutput.flatten().tolist()

                        # add to dict
                        pred_dict[seq]=curoutput

                    # update progress bar
                    if show_progress_bar:
                        pbar.update(1)

        # close pbar
        if show_progress_bar:
            pbar.close()

        # if printing performance
        if print_performance:
            end_time = time.time()
            print(f"\nTime taken for predictions on {device}: {end_time - start_time} seconds") 
        

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
                                                             use_slow=use_slow, return_numpy=return_numpy)

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



# ....................................................................................

def predict_pLDDT(inputs,
            version=DEFAULT_NETWORK_PLDDT,
            return_decimals=False,
            use_device=None,
            normalized=True,
            round_values=True,
            return_numpy=True,
            print_performance=False,
            show_progress_bar = False,
            force_disable_batch=False,
            disable_pack_n_pad = False,
            silence_warnings = False,
            return_as_disorder_score=False,
            plddt_base=0.35,
            plddt_top=0.95,
            default_to_device = 'cuda'):
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

    version : string
        The network to use for prediction. Default is DEFAULT_NETWORK,
        which is defined at the top of /parameters.
        Options currently include V1 or V2. V1 is the version used
        to make legacy metapredict and is from 'alphaPredict'. V2 
        is a new network made much more recently. 

    return_decimals : bool
        Originally trained to get values from 0 to 1. If set to True, you will get 
        values in their original form. If True, will multiply by 100 such that you get
        scores representative of actual pLDDT scores. 
        Default is False. 

    use_device : int or str 
        Identifier for the device to be used for predictions. 
        Possible inputs: 'cpu', 'mps', 'cuda', or an int that corresponds to
        the index of a specific cuda-enabled GPU. If 'cuda' is specified and
        cuda.is_available() returns False, instead of falling back to CPU, 
        metapredict will raise an Exception so you know that you are not
        using CUDA as you were expecting. 
        Default: None
            When set to None, we will check if there is a cuda-enabled
            GPU. If there is, we will try to use that GPU. 
            If you set the value to be an int, we will use cuda:int as the device
            where int is the int you specify. The GPU numbering is 0 indexed, so 0 
            corresponds to the first GPU and so on. Only specify this if you
            know which GPU you want to use. 
            * Note: MPS is only supported in Pytorch 2.1 or later. If I remember
            right it might have been beta supported in 2.0 *.

    normalized : bool
        Whether or not to normalize disorder values to between 0 and 1. 
        Default : True
    
    round_values : bool
        Whether to round the values to 4 decimal places. 
        Default : True

    return_numpy : bool
        Whether to return a numpy array or a list for single predictions. 
        Default : True    
                
    print_performance : bool
        Flag which means the function prints the time taken 
        for the two stages in the prediction algorithm. Again 
        useful for profiling and debugging. Default = False

    show_progress_bar : bool
        Flag which, if set to True, means a progress bar is printed as 
        predictions are made, while if False no progress bar is printed.
        Default  =  True

    force_disable_batch : bool
        Whether to override any use of batch predictions and predict
        sequences individually.
        Default = False

    disable_pack_n_pad : bool
        Whether to disable the use of pack_n_pad in the prediction
        algorithm. This is useful for debugging and profiling. Also gives
        us a way for people to use older versions of torch. 
        Default = False

    silence_warnings : bool
        whether to silence warnings such as the one about compatibility
        to use pack-n-pad due to torch version restrictions. 

    return_as_disorder_score : bool
        Whether to return as a disorder score.
        This basically inverts the score as a decimal and normalizes it between 0.35 
        as the lowest value and 0.95 as the highest. 

    plddt_base : float
        the lowest value plddt can be when converting it to a disorder score
        Default=0.35

    plddt_top : float
        the highest value plddt can be when converting it to a disorder score
        Default=0.95

    default_to_device : str
        The default device to use if device=None.
        If device=None and default_device != 'cpu' and default_device is
        not available, device_string will be returned as 'cpu'.
        I'm adding this in case we want to change the default architecture in the future. 
        For example, we could make default device 'gpu' where it will check for 
        cuda or mps and use either if available and then otherwise fall back to CPU.

    Returns
    -------------
    dict or list

        This function returns either a list or a dictionary.
    
        If a list was provided as input, the function returns a list
        of the same length as the input list, where each element is 
        itself a sublist where element 0 = sequence and element 1 is
        a numpy array of disorder scores. The order of the return list
        matches the order of the input list.

        If a dictionary was provided as input, the function returns
        a dictionary, where the same input keys map to values which are
        lists of 2 elements, where element 0 = sequence and element 1 is
        a numpy array of disorder scores.

    Raises
    ------
    MetapredictError
        An exception is raised if the requested network is not one of the available options.
    """
    ##
    ## FIGURE OUT WHAT NETWORK WE ARE USING
    ##
    ## ....................................................................................
    # normalize such that user can input v#, V#, or # to specify the version
    version = take_care_of_version(version)

    # make list of possible network inputs
    possible_networks=[]
    for cur_net in pplddt_networks.keys():
        possible_networks.append(cur_net)
        possible_networks.append(cur_net[-1])

    # make sure version in the known plddt networks
    if version not in pplddt_networks:
        raise MetapredictError(f'Network {version} not available. Valid inputs to choose a network are {possible_networks}')
    else:
        net = pplddt_networks[version]

    # load and setup the network (same code as used by the non-batch version)
    PATH = os.path.dirname(os.path.realpath(__file__))
    predictor_path = f"{PATH}/ppLDDT/networks/{net['weights']}"
    # get params
    params=net['parameters']

    # make sure that we set return_decimals to True if we are doing disorder prediction using plddt scores
    if return_as_disorder_score==True:
        return_decimals=True

    # see if we are return pLDDT values or raw decimal values.
    if return_decimals==True:
        if version=='V1':
            multiplier=0.01
        else:
            multiplier=1
        max_val_clipped=1
    else:
        if version=='V1':
            multiplier=1
        else:
            multiplier=100
        max_val_clipped=100       

    ##
    ## FIGURE OUT WHERE WE ARE DOING THE PREDICTIONS
    ##
    ## ....................................................................................    

    # if a single sequence, just use cpu. Using GPU for a single sequence would be silly.
    if isinstance(inputs, str)==True:
        device_string='cpu'
    else:
        device_string = check_device(use_device, default_device=default_to_device)
    
    # set device
    device=torch.device(device_string)

    # see if we need to mess with packing / padding
    if disable_pack_n_pad==False:
        if packaging_version.parse(torch.__version__) < packaging_version.parse("1.11.0"):
            disable_pack_n_pad=True
            # only warn if user hasn't turned off warning. 
            if silence_warnings==False:
                print('Pytorch version is <= 1.11.0. Disabling pack-n-pad functionality. This might slow down predictions.')


    ##
    ## LOAD IN THE NETWORK
    ##
    ## ....................................................................................    

    # load network. We do this differently depending on if we used
    # pytorch or pytorch-lightning to make the network. 
    model = get_model(model_name=f'pLDDT_{version}', 
                    params=params, 
                    predictor_path=predictor_path, 
                    device=device)

    # set to eval mode
    model.eval()

    # make sure network is on correct device. 
    model.to(device)
        
    ##
    ## START PREDICTIONS
    ##
    ## .................................................................................... 

    # now we can start up the predictions. 
    # if a single prediction, we can just ignore the batch stuff. 
    if isinstance(inputs, str)==True:
        # if we want to print the performance, start tracking time per prediction. 
        if print_performance:
            start_time = time.time()        
        
        # encode the sequence
        seq_vector = encode_sequence.one_hot(inputs)
        seq_vector = seq_vector.to(device)
        seq_vector = seq_vector.view(1, len(seq_vector), -1)

        # get output values from the seq_vector based on the network (brnn_network)
        with torch.no_grad():
            outputs = model(seq_vector.float()).detach().cpu().numpy()[0]*multiplier

        # convert to disorder score if needed. 
        if return_as_disorder_score==True:
            # this normalizes so the pLDDT score ends up being renormalized
            # to be between 0 and 1, converted into an effective disorder score
            outputs = outputs-plddt_base
            outputs = outputs*(1/(plddt_top-plddt_base))
            # means value of 1 = disordered and 0 is disordered
            outputs = 1-outputs 

        # Take care of rounding and normalization
        if normalized == True and round_values==True:
            outputs=np.round(np.clip(outputs, a_min=0, a_max=max_val_clipped),4)
        elif normalized==True and round_values==False:
            outputs=np.clip(outputs, a_min=0, a_max=max_val_clipped)
        elif normalized==False and round_values==True:
            outputs=np.round(outputs, 4)

        # make list if user wants a list instead of a np.array
        if return_numpy==False:
            if round_values==True:
                # need to round again because the np.round doesn't 
                # keep the rounded values when we convert to list. 
                outputs = [round(float(x), 4) for x in outputs.flatten()]
            else:
                # otherwise just return the flattened array as a list. 
                outputs=outputs.flatten().tolist()
        else:
            # if we want a numpy array, we need to make sure it's a 1D array
            outputs=outputs.flatten()

        # print performance
        if print_performance:
            end_time = time.time()
            print(f"Time taken for prediction on {device}: {end_time - start_time} seconds") 

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
            raise Exception('Invalid data type passed - expect a single sequence or a list or dictionary of sequences')

        # if we want to print the performance, start tracking time per prediction. 
        if print_performance:
            start_time = time.time()   

        # initialize the return dictionary that maps sequence to
        # disorder profile
        pred_dict = {}

        # check if we are disabling batch predictions. If we are, we need to
        # do all predictions individually
        if force_disable_batch==True:
            tot_num_seqs=len(sequence_list)
            # see if a progress bar is wanted
            if show_progress_bar:
                pbar = tqdm(total=len(sequence_list))
                # set pbar update amount
                pbar_update_amount=int(0.1*tot_num_seqs)
                if pbar_update_amount==0:
                    pbar_update_amount=1
            # iterate through sequence list
            for cur_seq_num, seq in enumerate(sequence_list):
                # encode the sequence
                seq_vector = encode_sequence.one_hot(seq)
                seq_vector = seq_vector.to(device)
                seq_vector = seq_vector.view(1, len(seq_vector), -1)

                # get output values from the seq_vector based on the network (brnn_network)
                with torch.no_grad():
                    outputs = model(seq_vector.float()).detach().cpu().numpy()[0].flatten()*multiplier

                # convert to disorder score if needed. 
                if return_as_disorder_score==True:
                    # this normalizes so the pLDDT score ends up being renormalized
                    # to be between 0 and 1, converted into an effective disorder score
                    outputs = outputs-plddt_base
                    outputs = outputs*(1/(plddt_top-plddt_base))
                    # means value of 1 = disordered and 0 is disordered
                    outputs = 1-outputs 

                # Take care of rounding and normalization
                if normalized == True and round_values==True:
                    outputs=np.round(np.clip(outputs, a_min=0, a_max=max_val_clipped),4)
                elif normalized==True and round_values==False:
                    outputs=np.clip(outputs, a_min=0, a_max=max_val_clipped)
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

                # add to dict
                pred_dict[seq]=outputs
                # update progress bar
                if show_progress_bar:
                    if cur_seq_num % (pbar_update_amount)==0:
                        pbar.update(pbar_update_amount)

        else:         
            # if we are disabling pack-n-pad functionalitity...
            if disable_pack_n_pad==True:
                # build a dictionary where keys are sequence length
                # and values is a list of sequences of that exact length
                size_filtered =  size_filter(sequence_list)
                
                # set progress bar info
                if show_progress_bar:
                    pbar = tqdm(total=len(size_filtered))

                # iterate through local size
                for local_size in size_filtered:
                    local_seqs = size_filtered[local_size]
                    # load the data
                    seq_loader = DataLoader(local_seqs, batch_size=params['batch_size'], shuffle=False)

                    # iterate through batches in seq_loader
                    for batch in seq_loader:
                        # Pad the sequence vector to have the same length as the longest sequence in the batch
                        seqs_padded = torch.nn.utils.rnn.pad_sequence([encode_sequence.one_hot(seq).float() for seq in batch], batch_first=True)
                        seqs_padded = seqs_padded.to(device)

                        # Forward pass, then send to CPU for numpy rounding / normalization
                        with torch.no_grad():
                            outputs = model.forward(seqs_padded).detach().cpu().numpy()*multiplier

                        # convert to disorder score if needed. 
                        if return_as_disorder_score==True:
                            # this normalizes so the pLDDT score ends up being renormalized
                            # to be between 0 and 1, converted into an effective disorder score
                            outputs = outputs-plddt_base
                            outputs = outputs*(1/(plddt_top-plddt_base))
                            # means value of 1 = disordered and 0 is disordered
                            outputs = 1-outputs                         

                        # Save predictions
                        for j, seq in enumerate(batch):
                            if normalized==True and round_values==True:
                                prediction=np.squeeze(np.round(np.clip(outputs[j][0:len(seq)], a_min=0, a_max=max_val_clipped),4))
                            elif normalized==True and round_values==False:
                                prediction=np.squeeze(np.clip(outputs[j][0:len(seq)], a_min=0, a_max=max_val_clipped))
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
                    
                    # update the progress bar
                    if show_progress_bar:
                        pbar.update(1)
            else:
                # sort the seqs by length, makes pack-n-pad stuff more efficient
                sequence_list.sort(key=len, reverse=True)
                # we will be using pack-n-pad.
                # load seqs into DataLoader
                seq_loader = DataLoader(sequence_list, batch_size=params['batch_size'], shuffle=False) 
                num_batches=len(seq_loader)
                
                # set progress bar info if we are going to display it. 
                # have to do this differently because you can't iterate over DataLoader
                # and get tqdm to update. 
                if show_progress_bar:
                    pbar = tqdm(total=num_batches)

                # iterate through each batch
                for batch in seq_loader:
                    # Pad the sequence vector to have the same length as the longest sequence in the batch
                    seqs_padded = torch.nn.utils.rnn.pad_sequence([encode_sequence.one_hot(seq).float() for seq in batch], batch_first=True)
                    lengths = [len(seq) for seq in batch]

                    # pack padded sequences
                    packed_seqs = torch.nn.utils.rnn.pack_padded_sequence(seqs_padded, lengths, batch_first=True, enforce_sorted=True)
                    
                    # move packed seqs to device. 
                    packed_seqs = packed_seqs.to(device)

                    # lstm forward pass.
                    with torch.no_grad():
                        outputs, _ = model.lstm(packed_seqs)

                    # unpack the packed sequence
                    outputs, _ = torch.nn.utils.rnn.pad_packed_sequence(outputs, batch_first=True)

                    # get final outputs by calling fc.
                    if params['used_lightning']==False:
                        outputs = model.fc(outputs)
                    else:
                        outputs = model.layer_norm(outputs)
                        for layer in model.linear_layers:
                            outputs = layer(outputs)
                    
                    # move to cpu
                    outputs = outputs.detach().cpu().numpy()*multiplier

                    # convert to disorder score if needed. 
                    if return_as_disorder_score==True:
                        # this normalizes so the pLDDT score ends up being renormalized
                        # to be between 0 and 1, converted into an effective disorder score
                        outputs = outputs-plddt_base
                        outputs = outputs*(1/(plddt_top-plddt_base))
                        # means value of 1 = disordered and 0 is disordered
                        outputs = 1-outputs 

                    # clean up / normalize
                    if normalized == True and round_values==True:
                        outputs=np.round(np.clip(outputs, a_min=0, a_max=max_val_clipped),4)
                    elif normalized==True and round_values==False:
                        outputs=np.clip(outputs, a_min=0, a_max=max_val_clipped)
                    elif normalized==False and round_values==True:
                        outputs=np.round(outputs, 4)                
                    
                    # get individual seqs ignoring padded parts. 
                    for seq_num, length in enumerate(lengths):
                        curoutput=outputs[seq_num][0:length].flatten()
                        seq = batch[seq_num]
                    
                        # make list if user wants a list instead of a np.array
                        if return_numpy==False:
                            if round_values==True:
                                # need to round again because the np.round doesn't 
                                # keep the rounded values when we convert to list. 
                                curoutput = [round(x, 4) for x in curoutput.flatten()]
                            else:
                                # otherwise just return the flattened array as a list. 
                                curoutput=curoutput.flatten().tolist()

                        # add to dict
                        
                        pred_dict[seq]=curoutput

                    # update progress bar
                    if show_progress_bar:
                        pbar.update(1)

        # close pbar
        if show_progress_bar:
            pbar.close()

        # if printing performance
        if print_performance:
            end_time = time.time()
            print(f"\nTime taken for predictions on {device}: {end_time - start_time} seconds") 
        
        ##
        ## PREDICTION DONE
        ##
        ## ....................................................................................

        # return scores
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

            
