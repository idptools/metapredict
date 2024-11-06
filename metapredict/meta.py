##
## meta.py
## 
## meta.py contains all the user-facing function associated with metapredict. If a new function is added it should be included
## here and added to the __all__ list
## 

##Handles the primary functions

# NOTE - any new functions must be added to this list!
__all__ =  ['predict_disorder', 'predict_disorder_domains', 'graph_disorder', 'predict_all', 'percent_disorder', 'predict_disorder_fasta', 'graph_disorder_fasta', 'predict_disorder_uniprot', 'graph_disorder_uniprot', 'predict_disorder_domains_uniprot', 'predict_disorder_domains_from_external_scores', 'graph_pLDDT_uniprot', 'predict_pLDDT_uniprot', 'graph_pLDDT_fasta', 'predict_pLDDT_fasta', 'graph_pLDDT', 'predict_pLDDT', 'predict_disorder_caid', 'predict_disorder_batch']
 
# import packages
import os
import sys
import numpy as np
from tqdm import tqdm

# note - we import packages below with a leading _ which means they are ignored in the import

#import protfasta to read .fasta files
import protfasta as _protfasta
# import getseq to get sequences from uniprot
from getSequence import getseq as _getseq

# import stuff for confidence score predictions
from metapredict.backend.network_parameters import metapredict_networks
from metapredict.parameters import DEFAULT_NETWORK, DEFAULT_NETWORK_PLDDT

# import stuff for IDR predictor from backend. Note the 'as _*' hides the imported
# module from the user
from metapredict.backend.predictor import predict as _predict
from metapredict.backend.predictor import predict_pLDDT as _predict_pLDDT
from metapredict.backend import meta_tools as _meta_tools

#import stuff for graphing from backend
from metapredict.backend.meta_graph import graph as _graph
from metapredict.backend import domain_definition as _domain_definition

# import stuff for exceptions
from metapredict.metapredict_exceptions import MetapredictError

# stuff for data structures
from metapredict.backend.data_structures import DisorderObject as _DisorderObject


# ..........................................................................................
#
def predict_disorder(inputs, version=DEFAULT_NETWORK, device=None,
    normalized=True,  round_values=True, return_numpy=True, return_domains=False,
    disorder_threshold=None, minimum_IDR_size=12, minimum_folded_domain=50,
    gap_closure=10, override_folded_domain_minsize=False, print_performance=False, 
    show_progress_bar=False, force_disable_batch=False, 
    disable_pack_n_pad=False, silence_warnings=False, 
    legacy=False):
    """
    The main function in metapredict. Updated to handle much more advanced
    functionality while maintaining backwards compatibility with previous
    versions of metapredict. 

    With V3, you can now input a single sequence, a list of sequences, or
    a dictionary where key:value pairings are a name for a sequence
    and the values are the actual sequence into this single function
    into this single function.

    We are keeping the 'predict_disorder_batch' function available
    to avoid breaking peoples' code, but that function isn't strictly
    necessary anymore because you can do batch predictions here. 

    You can also choose the specific device to carry out predictions 
    (a specific CUDA enabled GPU, MPS on Mac GPUs, or CPU).
    
    We also made it easy for users to print performance of the predictor
    on their own device to see how fast metapredict is!

    An important new thing is that we now have 3 versions of metapredict.
    Although setting 'legacy=True' will still work to maintain backwards
    compatibilty, the recommended thing to do is set 'version' equal
    to either 'v1', 'v2', or 'v3'.

    Finally, this also adds the ability to return DisorderObjects if 
    return_domains is set to True. The DisorderObject has the following variables:

    DisorderObject

        .sequence : str    
            Amino acid sequence 

        .disorder : list or np.ndaarray
            Hybrid disorder score

        .disordered_domain_boundaries : list
            List of domain boundaries for IDRs using Python indexing

        .folded_domain_boundaries : list
            List of domain boundaries for folded domains using Python indexing

        .disordered_domains : list
            List of the actual sequences for IDRs

        .folded_domains : list
            List of the actual sequences for folded domains    

    Parameters
    ------------

    inputs : str, list, or dict 
        Input amino acid sequence(s) as a string, list, or dictionary.
        If a list, needs to be just a list of amino acid sequences
        If a dictionary, each key needs to be a sequence name and 
        each value needs to be the corresponding sequence.

    version : str
        Which version of metapredict to use. Default is DEFAULT_NETWORK which 
        is the latest version as defined in parameters. Alternatively, 'V1', 'V2',
        or 'V3' can be specified to access a specific version of metapredict

    device : int or str 
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
            right it might have been beta supported in 2.0 *. MPS is still fairly
            new, so use at your own risk. 

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
        values depending on the network (V1 = 0.42, V2=0.5, V3=0.5). You can
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

    legacy : bool
        whether to use the legacy version of metapredict. This is 
        maintained for backwards compatibility, but the recommended
        approach is to use the version parameter to specify which
        version of metapredict you want to use. If you set this to
        True, it will override any version parameter you set. 
        Default: False

    Returns
    --------
     
    DisorderObject or list or np.ndarray
        Depending on your input and specified desired output, can return a 
        np.array, list, or DisorderObject. If you input a string, you will
        get back a single np.array, list, or DisorderObject. If you input a list,
        you will get a list of your specified return value. If you input a dict, 
        if you do not set return_domains=True, you will get back a dictionary 
        where the key is the same as the key for your input dict and the corresponding
        value is a nested list where the first element in that list is the sequence for
        that key and the value is the disorder scores. If you set return_domains=True,
        you will get back a dictionary where the key is the same as the key for your input
        dict and the value is a DisorderObject for that sequence.


    """

    # sanity check
    _meta_tools.raise_exception_on_zero_length(inputs)

    # check version and make sure it is an uppercase string
    version = _meta_tools.valid_version(version, 'disorder')

    # if legacy, make sure version is v1. 
    if legacy==True:
        version='V1'

    # get disorder
    return _predict(inputs, version=version, use_device=device,
        normalized=normalized, round_values=round_values, 
        return_numpy=return_numpy, return_domains=return_domains,
        disorder_threshold=disorder_threshold, minimum_IDR_size=minimum_IDR_size,
        minimum_folded_domain=minimum_folded_domain, gap_closure=gap_closure,
        override_folded_domain_minsize=override_folded_domain_minsize,
        print_performance=print_performance, show_progress_bar=show_progress_bar,
        force_disable_batch=force_disable_batch, disable_pack_n_pad=disable_pack_n_pad,
        silence_warnings=silence_warnings)


# ..........................................................................................
#
def predict_disorder_domains_from_external_scores(disorder, 
                                                  sequence=None,
                                                  disorder_threshold=0.5, 
                                                  minimum_IDR_size=12, 
                                                  minimum_folded_domain=50,
                                                  gap_closure=10,
                                                  override_folded_domain_minsize=False,
                                                  return_numpy=True):
    
    """
    This function takes in disorder scores generated from another predictor 
    and applies the same domain-decomposition algorithm as 
    predict_disorder_domains() does to extract out congigous IDRs. For example, 
    if one were to predict disorder using the (excellent) ODiNPred, download the 
    resulting scores, and read the scores into a list, that list could be passed
    as the $disorder argument to this function.
    
    Note that the settings used here may be inapplicable to another disorder 
    predictor, so you may need to play around with the parameters including 
    disorder_threshold, minimum_IDR_size, minimum_folded_domain and 
    gap_closure.


    Parameters
    -------------
    disorder : list
        A list of per-residue disorder scores.

    sequence : str
        The protein sequence as a string. If no sequence is passed, 
        calling DisorderObject.sequence will return an fake sequence.

    disorder_threshold : float
        Value that defines what 'disordered' is based on the input predictor 
        score. The higher the value the more stringent the cutoff.
        Default = 0.5. 
        
    minimum_IDR_size : int
        Defines the smallest possible IDR. This is a hard limit - i.e. we 
        CANNOT get IDRs smaller than this. 
        Default = 12.

    minimum_folded_domain : int
        Defines where we expect the limit of small folded domains to be. This 
        is NOT a hard limit and functions to modulate the removal of large gaps 
        (i.e. gaps less than this size are treated less strictly). Note that, in 
        addition, gaps < 35 are evaluated with a threshold of 
        0.35*disorder_threshold and gaps < 20 are evaluated with a threshold 
        of 0.25*disorder_threshold. These two lengthscales were decided based on
        the fact that coiled-coiled regions (which are IDRs in isolation) often 
        show up with reduced apparent disorder within IDRs, and but can be as 
        short as 20-30 residues. The folded_domain_threshold is used based on 
        the idea that it allows a 'shortest reasonable' folded domain to be 
        identified. 
        Default = 50.

    gap_closure : int
        Defines the largest gap that would be 'closed'. Gaps here refer to a 
        scenario in which you have two groups of disordered residues seprated 
        by a 'gap' of un-disordered residues. In general large gap sizes will 
        favour larger contigous IDRs. It's worth noting that gap_closure 
        becomes  relevant only when minimum_region_size becomes very small 
        (i.e. < 5)  because  really gaps emerge when the smoothed disorder 
        fit is "noisy", but when smoothed gaps are increasingly rare. 
        Default = 10.
        
    override_folded_domain_minsize : bool
        By default this function includes a fail-safe check that assumes 
        folded domains really shouldn't be less than 35 or 20 residues. 
        However, for some approaches we may wish to over-ride these thresholds 
        to match the passed minimum_folded_domain value. If this flag is set to 
        True this override occurs. This is generally not recommended unless you
        expect there to be well-defined sharp boundaries which could define
        small (20-30) residue folded domains. This is not provided as an option 
        in the normal predict_disorder_domains for metapredict. Default = False. 

    return_numpy : bool
        Flag which if set to true means all numerical types are returned
        as numpy.ndlist. Default is True

    Returns
    ---------
    DisorderObject
        Returns a DisorderObject. DisorderObject has 7 dot variables:

        .sequence : str    
            Amino acid sequence 

        .disorder : list or np.ndaarray
            Hybrid disorder score

        .disordered_domain_boundaries : list
            List of domain boundaries for IDRs using Python indexing

        .folded_domain_boundaries : list
            List of domain boundaries for folded domains using Python indexing

        .disordered_domains : list
            List of the actual sequences for IDRs

        .folded_domains : list
            List of the actual sequences for folded domains

    """

    # sanity check
    _meta_tools.raise_exception_on_zero_length(disorder)

    # if a sequence was provided check it makes sense in terms of type and length...
    if sequence is not None:
        try:
            if len(sequence) != len(disorder):
                raise MetapredictError(f'Disorder and sequence info are not length matched [disorder length = {len(disorder)}, sequence length = {len(sequence)}')
        except Exception:
            raise MetapredictError(f'Could not compare length of disorder and sequence parameters. Make sure sequence is a str and disorder a list')

        return_sequence = True

    # if sequence is None create a fake sequence and set return_sequence to False
    else:
        sequence = 'A'*len(disorder)
        return_sequence = False
        
            
    # run the get_domains function, passing in parameters
    return_tuple = _domain_definition.get_domains(sequence, 
                                                  disorder, 
                                                  disorder_threshold=disorder_threshold,                                           
                                                  minimum_IDR_size=minimum_IDR_size, 
                                                  minimum_folded_domain=minimum_folded_domain,
                                                  gap_closure=gap_closure,
                                                  override_folded_domain_minsize=override_folded_domain_minsize)
                                                 
    

    # extract out the IDR and FD boundaires, discarding the sequence info which is irrelevant
    IDRs = []

    for local_idr in return_tuple[1]:
        IDRs.append([local_idr[0], local_idr[1]])

    FDs = []

    for local_fd in return_tuple[2]:
        FDs.append([local_fd[0], local_fd[1]])

                                         
    # return DisorderObject
    return _DisorderObject(sequence, disorder, IDRs, FDs, return_numpy=return_numpy)


# ..........................................................................................
#
def predict_disorder_domains(sequence, 
                             disorder_threshold=None, 
                             minimum_IDR_size=12, 
                             minimum_folded_domain=50,
                             gap_closure=10, 
                             normalized=True,
                             return_numpy=True,
                             version=DEFAULT_NETWORK,
                             return_list=False):
    """
    This function takes an amino acid sequence and one or more 
    variable options and returns a data structure called a 
    `DisorderObject`. The object parameters associated with this
    object are defined below.

    The previous version of metapredict returned a list of values,
    which can be obtained instead of the DisorderedObject if 
    return_list is set to True.

    Parameters
    -------------

    sequence : str
        Amino acid sequence

    disorder_threshold : float
        Set to None such that it will change to 0.42 for legacy
        and 0.5 for metapredict. Can still manually set value.

    minimum_IDR_size : int
        Defines the smallest possible IDR. This is a hard limit - 
        i.e. we CANNOT get IDRs smaller than this. Default = 12.

    minimum_folded_domain : int
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
        Defines the largest gap that would be 'closed'. Gaps here 
        refer to a scenario in which you have two groups of 
        disordered residues seprated by a 'gap' of un-disordered 
        residues. In general large gap sizes will favour larger 
        contigous IDRs. It's worth noting that gap_closure becomes 
        relevant only when minimum_region_size becomes very small 
        (i.e. < 5) because really gaps emerge when the smoothed 
        disorder fit is "noisy", but when smoothed gaps
        are increasingly rare. Default=10.

    normalized : bool
        whether the disorder scores are normalized between zero and
        one, default is true

    return_numpy : bool
        Flag which if set to true means all numerical types are returned
        as numpy.ndlist. Default is True

    version : str
        Which version of metapredict to use. Default is DEFAULT_NETWORK which 
        is the latest version as defined in parameters. Alternatively, 'V1', 'V2',
        or 'V3' can be specified to access a specific version of metapredict

    return_list : bool
        Flag that determines i to return the old format where a 
        tuple is returned. This is retained for backwards compatibility

    Returns
    ---------
    DisorderObject
        By default, the function returns a DisorderObject. A DisorderObject has 7 dot variables:

        .sequence : str    
            Amino acid sequence 

        .disorder : list or np.ndaarray
            disorder scores

        .disordered_domain_boundaries : list
            List of domain boundaries for IDRs using Python indexing

        .folded_domain_boundaries : list
            List of domain boundaries for folded domains using Python indexing

        .disordered_domains : list
            List of the actual sequences for IDRs

        .folded_domains : list
            List of the actual sequences for folded domains

    Returns
    ---------
    list
        However, if ``return_list`` == True. Then, the function returns a 
        list with three elements, as outlined below.

        * [0] - Smoothed disorder score used to aid in domain boundary identification. This can be useful for understanding how IDRs/folded domains were identified, and will vary depending on the settings provided

        * [1] - a list of elements, where each element defines the start and end position of each IDR. If a sequence was provided the third element in each sub-element is the IDR sequence. If no sequence was provided, then each sub-element is simply len=2.
        
        * [2] - a list of elements, where each element defines the start and end position of each folded region. If a sequence was provided the third element in each sub-element is the folded domain sequence. If no sequence was provided, then each sub-element is simply len=2.    

    """

    # sanity check
    _meta_tools.raise_exception_on_zero_length(sequence)

    # check version and make sure it is an uppercase string
    version = _meta_tools.valid_version(version, 'disorder')

    # get disorder threshold
    if disorder_threshold == None:
        disorder_threshold = metapredict_networks[version]['parameters']['disorder_threshold']

    # check that a valid range was passed for disorder_threshold
    _meta_tools.valid_range(disorder_threshold, 0.0, 1.0)

    # if not returning list, we can do everything using the predict function
    if return_list==False:
        # get the disorder obj and return it. 
        DomObj = _predict(sequence, version=version, normalized=normalized,
            return_numpy=return_numpy, return_domains=True,
            disorder_threshold=disorder_threshold, minimum_IDR_size=minimum_IDR_size, 
            minimum_folded_domain=minimum_folded_domain, gap_closure=gap_closure)
        return DomObj
    else:
        # get disorder
        disorder = _predict(sequence, version=version, normalized=normalized,
            return_numpy=return_numpy)
        
        # extract out disordered 
        return_tuple = _domain_definition.get_domains(sequence, 
                                                     disorder, 
                                                     disorder_threshold=disorder_threshold,                                            
                                                     minimum_IDR_size=minimum_IDR_size, 
                                                     minimum_folded_domain=minimum_folded_domain,
                                                     gap_closure=gap_closure)
        # return the list
        return [disorder, return_tuple[0], return_tuple[1], return_tuple[2]]



# ..........................................................................................
#
def predict_all(sequence):
    """
    Function to return all three disorder predictions (V1, V2, V3 for
    (metapredict), and predicted pLDDT (V1, V2). Returns as a tuple of numpy 
    arrays, with ppLDDT returned as normalized between 0 and 1.

    Parameters
    ------------
    sequence : str 
        Input amino acid sequence (as string) to be predicted.

    Returns
    --------
     
    tuple with five np.ndarrays:

        [0] - normalized ppLDDT scores using V1 pLDDT predictor (previously from AlphaPredict)
        [1] - normalized ppLDDT scores using V2 pLDDT predictor
        [2] - legacy metapredict disorder (original metapredict disorder)
        [3] - meta disorder (updated metapredict disorder) - V2
        [4] - meta disorder (updated metapredict disorder) - V3

    """

    # sanity check
    _meta_tools.raise_exception_on_zero_length(sequence)

    # compute pLDDT and metapredict disorder
    v1 = _predict(sequence, version='V1')
    v2 = _predict(sequence, version='V2')
    v3 = _predict(sequence, version='V3')
    ppLDDT_v1 = _predict_pLDDT(sequence, return_numpy=True, normalized=True, return_decimals=True, version='v1')
    ppLDDT_v2 = _predict_pLDDT(sequence, return_numpy=True, normalized=True, return_decimals=True, version='v2')
    
    return (ppLDDT_v1, ppLDDT_v2, v1, v2, v3)



# ..........................................................................................
#
def predict_disorder_batch(input_sequences,
                                version = DEFAULT_NETWORK,
                                device=None,
                                normalized=True,
                                round_values=True,
                                return_numpy=True,                                
                                return_domains=False,
                                disorder_threshold=None,
                                minimum_IDR_size=12,
                                minimum_folded_domain=50,
                                gap_closure=10,
                                override_folded_domain_minsize=False,
                                show_progress_bar = True,
                                disable_batch = False):

    """
    Batch mode predictor which takes advantage of PyTorch
    parallelization such that whether it's on a GPU or a 
    CPU, predictions for a set of sequences are performed
    rapidly.

    This now works with all versions of metapredict.     

    Note also that batch mode uses 32-bit float vectors
    whereas non-batch uses 64-bit float vectors, so the
    precise values in batch vs. non-batch may differ 
    slighly, however this is a numerical precision difference,
    such that values by both methods are always within
    1e-3 of one another.

    Parameters
    --------------
    input_sequences : list or dictionary
        A collection of sequences that are presented either
        as a list of sequences or a dictionary of key-value
        pairs where values are sequences.

    version : string
        The network to use for prediction. Default is DEFAULT_NETWORK,
        which is defined at the top of /parameters.
        Options currently include V1, V2, or V3. 

    device : int or str 
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

    show_progress_bar : bool
        Flag which, if set to True, means a progress bar is printed as 
        predictions are made, while if False no progress bar is printed.
        Default  =  True

    disable_batch : bool
        Whether to override any use of batch predictions and predict
        sequences individually.
        Default = False    

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

    """
    # check version and make sure it is an uppercase string
    version = _meta_tools.valid_version(version, 'disorder')

    return _predict(input_sequences,
                        version=version,
                        use_device=device,
                        round_values=round_values,
                        return_numpy=return_numpy,
                        return_domains = return_domains,                          
                        disorder_threshold = disorder_threshold,
                        minimum_IDR_size = minimum_IDR_size,
                        minimum_folded_domain = minimum_folded_domain,
                        override_folded_domain_minsize=False,
                        gap_closure = gap_closure,
                        show_progress_bar = show_progress_bar,
                        force_disable_batch = disable_batch)



# ..........................................................................................
#
def graph_disorder(sequence, 
                   version = DEFAULT_NETWORK,
                   pLDDT_version = DEFAULT_NETWORK_PLDDT,
                   title = 'Predicted protein disorder', 
                   disorder_threshold = None,
                   pLDDT_scores=False,
                   shaded_regions = None,
                   shaded_region_color = 'red',
                   DPI=150, 
                   output_file=None):
    """
    Function to plot the disorder of an input sequece. Displays immediately.

    Parameters
    -------------

    sequence : str 
        Input amino acid sequence (as string) to be predicted.

    version : string
        The network to use for prediction. Default is DEFAULT_NETWORK,
        which is defined at the top of /parameters.
        Options currently include V1, V2, or V3. 

    pLDDT_version : string
        The network to use for pLDDT prediction. Default is DEFAULT_NETWORK,
        which is defined at the top of /parameters.
        Options currently include V1, V2.

    title : str
        Sets the title of the generated figure. Default = "Predicted protein 
        disorder"

    disorder_threshold : float
        Set to None by default such that if the user chooses to set
        legacy=True, the threshhold line will be at 0.3 and if legacy
        is set to false (default) then the threshold line will be at 0.5.

        Sets a threshold which draws a horizontal black line as a visual 
        guide along the length of the figure. Must be a value between 0 
        and 1. Default = 0.3 for legacy and 0.5 for new version of metapredict.
            
    pLDDT_scores : Bool
        Sets whether to include the predicted pLDDT scores in the figure

    shaded_regions : list of lists
        A list of lists, where sub-elements are of length 2 and contain 
        start and end values for regions to be shaded. Assumes that sanity 
        checking on positions has already been done. Default is None, but 
        if there were specific regions you wanted to highlight this might, 
        for example, look like shaded_regions=[[1,10],[40,50]], which would 
        shade between 1 and 10 and then between 40 and 50. This can be useful
        to either highlight specific IDRs or specific folded domains

    shaded_region_color : str or list of sts
        String that defines the color of the shaded region. The shaded region 
        is always set with an alpha of 0.3 but the color can be any valid 
        matplotlib color name or a hex color string (i.e. "#ff0000" is red).
        Alternatively a list where number of elements matches number in 
        shaded_regions, assigning a color-per-shaded regions.
    
    DPI : int
        Dots-per-inch. Defines the resolution of the generated figure. 
        Passed to the dpi argument in ``matplotlib.pyplot.savefig()``.
        
    output_file : str
        If provided, the output_file variable defines the location and type 
        of the file to be saved. This should be a file location and filename 
        with a valid matplotlib extension (such as .png, or .pdf) and, if 
        provided, this value is passed directly to the 
        ``matplotlib.pyplot.savefig()`` function as the ``fname`` parameter. 
        Default = None.


    Returns
    --------

    None
        No return object, but, the graph is saved to disk or displayed 
        locally.
    """

    # sanity check
    _meta_tools.raise_exception_on_zero_length(sequence)

    # check version and make sure it is an uppercase string
    version = _meta_tools.valid_version(version, 'disorder')
    pLDDT_version = _meta_tools.valid_version(pLDDT_version, 'pLDDT')

    # get disorder threshold
    if disorder_threshold == None:
        disorder_threshold=metapredict_networks[version]['parameters']['disorder_threshold']
    
    # check that a valid range was passed for disorder_threshold
    _meta_tools.valid_range(disorder_threshold, 0.0, 1.0)

    # ensure sequence is upper case
    sequence = sequence.upper()

    # check that a valid set of shaded regions was passed
    _meta_tools.valid_shaded_region(shaded_regions, len(sequence))

    # call the graph function
    _graph(sequence, title = title, disorder_threshold = disorder_threshold, 
        pLDDT_scores = pLDDT_scores, shaded_regions = shaded_regions,
        shaded_region_color = shaded_region_color, 
        DPI=DPI, output_file = output_file, version=version,
        pLDDT_version=pLDDT_version) 


# ..........................................................................................
#
def predict_pLDDT(inputs, pLDDT_version=DEFAULT_NETWORK_PLDDT, return_decimals=False,
    device=None, normalized=True, round_values=True, return_numpy=True,
    print_performance=False, show_progress_bar=False, force_disable_batch=False,
    disable_pack_n_pad=False, silence_warnings=False, return_as_disorder_score=False):
    """
    Function to return predicted pLDDT scores. pLDDT scores are the scores
    reported by AlphaFold2 (AF2) that provide a measure of the confidence 
    with which AF2 has on the local structure prediction. This now has massively 
    improved functionality and supporst the same batch mode as the disorder.

    Parameters
    ----------
    inputs : string list or dictionary
        An individual sequence or a collection of sequences 
        that are presented either as a list of sequences or 
        a dictionary of key-value pairs where values are sequences.

    pLDDT_version : string
        The network to use for prediction. Default is DEFAULT_NETWORK_PLDDT,
        which is defined at the top of /parameters.
        Options currently include V1 or V2. V1 is the version used
        to make legacy metapredict and is from 'alphaPredict'. V2 
        is a new network made much more recently. 

    return_decimals : bool
        If False, values be between 0 and 100. If True, the values 
        will be between 0 and 1. 
        Default is False. 

    device : int or str 
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
        This basically inverts the score as a decimal and normalizes so that
        it looks like a disorder score (higher value=disordereed and lower
        value = not disordered). This is similar to the approach that we used
        to generate the scores that were combined with legacy metapredict to make
        V2 and V3. 

    Returns
    --------
    
    list or np.ndarray
        Returns a list (or np.ndarray) of floats that corresponds to the 
        per-residue pLDDT score. Return type depends on the flag 
        return_numpy

    """

    # sanity check
    _meta_tools.raise_exception_on_zero_length(inputs)

    # check version and make sure it is an uppercase string
    pLDDT_version = _meta_tools.valid_version(pLDDT_version, 'pLDDT')    

    # return predicted values of disorder for sequence
    return  _predict_pLDDT(inputs,
            version=pLDDT_version, return_decimals=return_decimals,
            use_device=device, normalized=normalized,
            round_values=round_values, return_numpy=return_numpy,
            print_performance=print_performance,
            show_progress_bar = show_progress_bar,
            force_disable_batch=force_disable_batch,
            disable_pack_n_pad = disable_pack_n_pad,
            silence_warnings = silence_warnings,
            return_as_disorder_score=return_as_disorder_score)


# ..........................................................................................
#
def graph_pLDDT(sequence, 
                title = 'Predicted AF2 pLDDT Confidence Score',
                disorder_scores=False, 
                shaded_regions = None,
                shaded_region_color = 'red',
                DPI=150, 
                output_file=None,
                pLDDT_version = DEFAULT_NETWORK_PLDDT):
    """
    Function to plot the AF2 pLDDT scores of an input sequece. Displays immediately.

    Parameters
    -------------

    sequence : str 
        Input amino acid sequence (as string) to be predicted.

    title : str
        Sets the title of the generated figure. 
        Default = "Predicted AF2 pLDDT Confidence Score"

    disorder_scores : Bool
        Whether to include disorder scores. Can set to False if you
        just want the AF2 confidence scores. 
        Default = False

    shaded_regions : list of lists
        A list of lists, where sub-elements are of length 2 and contain 
        start and end values for regions to be shaded. Assumes that sanity 
        checking on positions has already been done. Default is None, but 
        if there were specific regions you wanted to highlight this might, 
        for example, look like shaded_regions=[[1,10],[40,50]], which would 
        shade between 1 and 10 and then between 40 and 50. This can be useful
        to either highlight specific IDRs or specific folded domains.
        Default = None

    shaded_region_color : str
        String that defines the color of the shaded region. The shaded region 
        is always set with an alpha of 0.3 but the color can be any valid 
        matplotlib color name or a hex color string (i.e. "#ff0000" is red).

    DPI : int
        Dots-per-inch. Defines the resolution of the generated figure. 
        Passed to the dpi argument in ``matplotlib.pyplot.savefig()``.
        
    output_file : str
        If provided, the output_file variable defines the location and type 
        of the file to be saved. This should be a file location and filename 
        with a valid matplotlib extension (such as .png, or .pdf) and, if 
        provided, this value is passed directly to the 
        ``matplotlib.pyplot.savefig()`` function as the ``fname`` parameter. 
        Default = None.

    pLDDT_version : string
        The network to use for prediction. Default is DEFAULT_NETWORK_PLDDT,
        which is defined at the top of /parameters.
        Options currently include V1 or V2 

    Returns
    --------

    None
        No return object, but, the graph is saved to disk or displayed locally.


    """

    # sanity check
    _meta_tools.raise_exception_on_zero_length(sequence)

    # check that a valid set of shaded regions was passed
    _meta_tools.valid_shaded_region(shaded_regions, len(sequence))

    # check version and make sure it is an uppercase string
    pLDDT_version = _meta_tools.valid_version(pLDDT_version, 'pLDDT')

    # call the graph function
    _graph(sequence, title = title, pLDDT_scores = True,
        disorder_scores=disorder_scores, shaded_regions = shaded_regions,
        shaded_region_color = shaded_region_color, 
        DPI=DPI, output_file = output_file, pLDDT_version=pLDDT_version) 


# ..........................................................................................
#
def percent_disorder(sequence, disorder_threshold=None, mode='threshold', 
                    version=DEFAULT_NETWORK):
    """
    Function that returns the percent disorder for any given protein.
    By default, uses 0.5 as a cutoff for the new version of metapredict
    and 0.3 for the legacy version of metapredict (values greater than or equal
    to 0.5 will be considered disordered). If a value for cutoff is specified,
    that value will be used.

    Mode lets you toggle between 'threshold' and 'disorder_domains'. If 
    threshold is used a simple per-residue logic operation is applied
    and the fraction of residues above the disorder_threshold is used.
    If 'disorder_domains' is used then the sequence is divided into
    IDRs and folded domains using the predict_disordered_domains() 
    function. 

    
    Parameters
    -------------

    sequence : str 
        Input amino acid sequence (as string) to be predicted.

    disorder_threshold : float
        Set to None by default such that it will change depending
        on whether legacy is set to True or False.

        Sets a threshold which defines if a residue is considered disordered
        or not. Default for new metapredict = 0.5. Default for legacy metapredict
        is 0.3.

    mode : str
        Selector which lets you choose which mode to calculate percent disorder
        with. Default is 'threshold', meaning the percentage of disorder is 
        calculated as what fraction of residues are above the disorder_threshold.
        Alternatively, 'disorder_domains' means we use the 
        predict_disorder_domains() function and then calculate what fraction of
        the protein's residues are in the predicted IDRs.
        

    version : string
        The network to use for prediction. Default is DEFAULT_NETWORK,
        which is defined at the top of /parameters.
        Options currently include V1, V2, or V3. 

    Returns
    -----------

    float
        Returns a floating point value between 0 and 100 that defines what
        percentage of the sequence is considered disordered.

    """

    # sanity check
    _meta_tools.raise_exception_on_zero_length(sequence)

    # check mode is valid first
    mode = mode.lower()
    if mode not in ['threshold', 'disorder_domains']:
        raise MetapredictError(f"Mode must be one of 'threshold' or 'disorder_domains', but '{mode}' was passed instead")

    # check version and make sure it is an uppercase string
    version = _meta_tools.valid_version(version, 'disorder')

    # make all residues upper case 
    sequence = sequence.upper()

    # set the disorder threshold
    if disorder_threshold == None:        
        disorder_threshold=metapredict_networks[version]['parameters']['disorder_threshold']

    if mode == 'threshold':

        # get disorder
        dis = _predict(sequence, version=version, return_numpy=True)
        
        # check threshold is valid
        _meta_tools.valid_range(disorder_threshold, 0.0, 1.0)
            
        # get number over value
        disorder_count = (dis >= disorder_threshold).sum()

        """
        percent disorder is equal to n (number of residues with predicted
        value >= cutoff) divided by the total number of residues in the
        input sequence.
        """

        percent_disordered = round(100*((disorder_count / len(sequence))), 3)

    # else using disordered domains
    else:
        # if no specified threshold use the defaults
        idrs=predict_disorder_domains(sequence, disorder_threshold, version=version).disordered_domains
        fraction_disordered = sum([len(i) for i in idrs])/len(sequence)
        percent_disordered = round(100*(fraction_disordered), 3)

    return percent_disordered



#./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\
#./\./\./\./\./\./\./\./\./\./\./\./\.FASTA STUFF./\./\./\./\./\./\./\./\./\./\./\./\
#./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\././\./\

#Various functions for working with fasta files to make everyones life easier.


def predict_disorder_fasta(filepath, 
                           output_file = None,
                           normalized=True,
                           invalid_sequence_action='convert',
                           version=DEFAULT_NETWORK,
                           device=None,
                           show_progress_bar=True):
    """
    Function to read in a .fasta file from a specified filepath.
    Returns a dictionary of disorder values where the key is the 
    fasta header and the values are the predicted disorder values.
    
    Parameters
    -------------

    filepath : str 
        The path to where the .fasta file is located. The filepath should
        end in the file name, and can be an absolute or relative path

    output_file : str
        By default, a dictionary of predicted values is returned 
        immediately. However, you can specify an output filename and path 
        and a .csv file will be saved. This should include any file extensions.
        Default = None.

    normalized : bool
        Flag which defines in the predictor should control and normalize such 
        that all values fall between 0 and 1. The underlying learning model can, 
        in fact output some negative values and some values greater than 1. 
        Normalization controls for this. Default = True

    invalid_sequence_action : str
        Tells the function how to deal with sequences that lack standard amino 
        acids. Default is convert, which as the name implies converts via standard 
        rules. See https://protfasta.readthedocs.io/en/latest/read_fasta.html 
        for more information.

     version : string
        The network to use for prediction. Default is DEFAULT_NETWORK,
        which is defined at the top of /parameters.
        Options currently include V1, V2, or V3. 

    device : string
        the device to use for prediction. Default is None, which means
        the function will try to use a GPU if one is available. 
        Options include 'cpu', 'cuda', 'mps', or an int that corresponds
        to the index of a specific cuda-enabled GPU. To specify by index, 
        use 'cuda:int' where int is the index of the GPU you want to use.
        For example, 'cuda:0' would use the first GPU. If 'cuda' is specified
        and cuda.is_available() returns False, instead of falling back to
        CPU, metapredict will raise an Exception so you know that you are
        not using CUDA as you were expecting.

    show_progress_bar : bool
        Flag which, if set to True, means a progress bar is printed as 
        predictions are made, while if False no progress bar is printed.

    Returns
    --------

    dict or None
        If output_file is set to None (as default) then this fiction returns 
        a dictionary of sequence ID to disorder np.ndarrays(dtype=np.float32). 

        If output_file is set to a filename then a .csv file will instead 
        be written and no return data will be provided.         

    """

    # Importantly, by default this function corrects invalid residue
    # values using protfasta.read_fasta() because the disorder predictor
    # cannot have non-amino acid values as an input.

    # Test to see if the data_file exists
    test_data_file = os.path.abspath(filepath)

    # check version and make sure it is an uppercase string
    version = _meta_tools.valid_version(version, 'disorder')

    # check path
    if not os.path.isfile(test_data_file):
        raise FileNotFoundError(f'Datafile [{filepath}] does not exist.')

    # get seqs via protfasta
    protfasta_seqs = _protfasta.read_fasta(filepath, invalid_sequence_action = invalid_sequence_action)

    # initialize return dictionary
    disorder_dict = _predict(protfasta_seqs, version=version, 
                            normalized=normalized, return_numpy=False,
                            show_progress_bar=show_progress_bar, 
                            use_device=device)

    # if we did not request an output file 
    if output_file is None:
        return disorder_dict

    # else write to disk 
    else:
        _meta_tools.write_csv(disorder_dict, output_file)



# ..........................................................................................
#
def predict_pLDDT_fasta(filepath, 
                        output_file = None,
                        invalid_sequence_action='convert',
                        pLDDT_version=DEFAULT_NETWORK_PLDDT,
                        device=None,
                        show_progress_bar=True):
    """
    Function to read in a .fasta file from a specified filepath.
    Returns a dictionary of pLDDT values where the key is the 
    fasta header and the values are the predicted pLDDT values.
    
    Parameters
    -------------

    filepath : str 
        The path to where the .fasta file is located. The filepath should
        end in the file name, and can be an absolute or relative path


    output_file : str
        By default, a dictionary of predicted values is returned 
        immediately. However, you can specify an output filename and path 
        and a .csv file will be saved. This should include any file extensions.
        Default = None.

    invalid_sequence_action : str
        Tells the function how to deal with sequences that lack standard amino 
        acids. Default is convert, which as the name implies converts via standard 
        rules. See https://protfasta.readthedocs.io/en/latest/read_fasta.html 
        for more information.

    pLDDT_version : string
        The network to use for prediction. Default is DEFAULT_NETWORK_PLDDT,
        which is defined at the top of /parameters.
        Options currently include V1 or V2 

    device : string
        the device to use for prediction. Default is None, which means
        the function will try to use a GPU if one is available. 
        Options include 'cpu', 'cuda', 'mps', or an int that corresponds
        to the index of a specific cuda-enabled GPU. To specify by index, 
        use 'cuda:int' where int is the index of the GPU you want to use.
        For example, 'cuda:0' would use the first GPU. If 'cuda' is specified
        and cuda.is_available() returns False, instead of falling back to
        CPU, metapredict will raise an Exception so you know that you are
        not using CUDA as you were expecting.

    show_progress_bar : bool
        Flag which, if set to True, means a progress bar is printed as 
        predictions are made, while if False no progress bar is printed.

    Returns
    --------

    dict or None
        If output_file is set to None (as default) then this fiction returns a 
        dictionary of sequence ID to pLDDT vector. If output_file is set to a 
        filename then a .csv file will instead be written and no return data 
        will be provided.
    """

    # Importantly, by default this function corrects invalid residue
    # values using protfasta.read_fasta() because the pLDDT predictor
    # cannot have non-amino acid values as an input.

    # Test to see if the data_file exists
    test_data_file = os.path.abspath(filepath)

    if not os.path.isfile(test_data_file):
        raise FileNotFoundError(f'Datafile does not exist.')

    protfasta_seqs = _protfasta.read_fasta(filepath, invalid_sequence_action = invalid_sequence_action)

    # check version and make sure it is an uppercase string
    pLDDT_version = _meta_tools.valid_version(pLDDT_version, 'pLDDT')

    # new predict_pLDDT function can handle string, list, or dict. 
    confidence_dict = _predict_pLDDT(protfasta_seqs, 
                                    version=pLDDT_version, 
                                    return_numpy=False, 
                                    show_progress_bar=show_progress_bar, 
                                    use_device=device)

    # if we did not request an output file 
    if output_file is None:
        return confidence_dict

    # else write to disk 
    else:
        _meta_tools.write_csv(confidence_dict, output_file)


# ..........................................................................................
#
def graph_disorder_fasta(filepath, 
                         pLDDT_scores=False,
                         disorder_threshold = None,
                         DPI=150, 
                         output_dir = None,
                         output_filetype='png', 
                         invalid_sequence_action='convert',
                         indexed_filenames=False,
                         version=DEFAULT_NETWORK,
                         pLDDT_version=DEFAULT_NETWORK_PLDDT):

    """
    Function to make graphs of predicted disorder from the sequences
    in a specified .fasta file. By default will save the generated
    graphs to the location output_path specified in filepath.

    **WARNING**: It is unadvisable to not include an output directory if you are reading in a .fasta 
    file with many sequences! This is because each graph must be closed individually before the next 
    will appear. Therefore, you will spend a bunch of time closing each graph.

    **NB**: You cannot specify the output file name here! By default, the file name will
    be the first 14 characters of the FASTA header followed by the filetype as specified 
    by filetype. If you wish for the files to include a unique leading number (i.e. X_rest_of_name
    where X starts at 1 and increments) then set indexed_filenames to True. This can be useful if you
    have sequences where the 1st 14 characters may be identical, which would otherwise overwrite an 
    output file.

    Parameters
    -----------

    filepath : str 
        The path to where the .fasta file is located. The filepath should end in the file name. 
        For example (on MacOS):filepath="/Users/thisUser/Desktop/folder_of_seqs/interesting_proteins.fasta"

    pLDDT_scores : Bool
        Sets whether to include the predicted pLDDT scores from
        AlphaFold2

    disorder_threshold : float
        Sets a threshold which draws a horizontal black line as a visual guide along
        the length of the figure. Must be a value between 0 and 1.
    
    DPI : int
        Dots-per-inch. Defines the resolution of the generated figure. Passed to the
        dpi argument in ``matplotlib.pyplot.savefig()``.

    output_dir : str
        If provided, the output_dir variable defines the directory where file should besaved
        to be saved. This should be a writeable filepath. Default is None. Output files are 
        saved with filename as first 14 chars of fasta header (minus bad characters) plus the
        appropriate file extension, as defined by filetype.

    output_filetype : str
        String that defines the output filetype to be used. Must be one of pdf, png, jpg.

    invalid_sequence_action : str
        Tells the function how to deal with sequences that lack standard amino acids. Default is 
        convert, which as the name implies converts via standard rules. See 
        https://protfasta.readthedocs.io/en/latest/read_fasta.html for more information.

    indexed_filenames : bool
        Bool which, if set to true, means filenames start with an unique integer.

    version : string
        The network to use for prediction. Default is DEFAULT_NETWORK,
        which is defined at the top of /parameters.
        Options currently include V1, V2, or V3. 

    pLDDT_version : string
        The network to use for pLDDT prediction. 
        Default is DEFAULT_NETWORK_PLDDT,
        which is defined at the top of /parameters.
        Options currently include V1 or V2

    Returns
    ---------

    None
        No return object, but, the graph is saved to disk or displayed locally.

    """
    # check version and make sure it is an uppercase string
    version = _meta_tools.valid_version(version, 'disorder')

    # see if we need to set the disorder threshold
    if disorder_threshold == None:
        disorder_threshold = metapredict_networks[version]['parameters']['disorder_threshold']

    # check pLDDT version and make sure it is an uppercase string
    pLDDT_version = _meta_tools.valid_version(pLDDT_version, 'pLDDT')

    # check that a valid range was passed for disorder_threshold
    _meta_tools.valid_range(disorder_threshold, 0.0, 1.0)

    # Test to see if the data_file exists
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f'Datafile [{filepath:s}] does not exist')

    # Test to see if output directory exists
    if output_dir is not None:
        if not os.path.isdir(output_dir):
            raise FileNotFoundError(f'Proposed output directory could not be found')

    # validate disorder_threshold
    _meta_tools.valid_range(disorder_threshold, 0,1)

    # use protfasta to read in fasta file
    sequences =  _protfasta.read_fasta(filepath, invalid_sequence_action = invalid_sequence_action)

    # now for each sequence...
    idx_counter = 0
    for idx in tqdm(sequences):
        
        # increment the index counter...
        idx_counter = idx_counter + 1

        # grab the sequence and convert to upper as well
        local_sequence = sequences[idx].upper()

        # make sure file doesn't try to save if no output dir specified
        if output_dir is not None:

            # define the full filename with filetype. NOTE - we use os.sep as an OS-independent way to define
            # filename and filepath. This may end up with the filename containing a double slash, but this is fine
            # and matplotlib deals with this appropriately. This should be a POSIX-compliant way to do cross-platform
            # file writing
            if indexed_filenames:
                filename = output_dir + os.sep + f"{idx_counter:d}_" + _meta_tools.sanitize_filename(idx)[0:14] + f".{output_filetype:s}"
            else:
                filename = output_dir + os.sep + _meta_tools.sanitize_filename(idx)[0:14] + f".{output_filetype:s}"

            # define title (including bad chars)
            title = idx[0:14]

            # plot!        
            graph_disorder(local_sequence, title=title, pLDDT_scores=pLDDT_scores, 
                DPI=DPI, output_file=filename, version=version, 
                pLDDT_version=pLDDT_version, disorder_threshold=disorder_threshold)

        # if no output_dir specified just graph the seq        
        else:
            # define title (including bad chars)
            title = idx[0:14]            
            graph_disorder(local_sequence, title=title, pLDDT_scores=pLDDT_scores, DPI=DPI, 
                version=version, pLDDT_version=pLDDT_version,
                disorder_threshold=disorder_threshold)


# ..........................................................................................
#
def graph_pLDDT_fasta(filepath, 
                         DPI=150, 
                         output_dir = None,
                         output_filetype='png', 
                         invalid_sequence_action='convert',
                         indexed_filenames=False,
                         pLDDT_version=DEFAULT_NETWORK_PLDDT):

    """
    Function to make graphs of predicted pLDDT from the sequences
    in a specified .fasta file. By default will save the generated
    graphs to the location output_path specified in filepath.

    **WARNING**: It is unadvisable to not include an output directory if you are reading in a .fasta 
    file with many sequences! This is because each graph must be closed individually before the next 
    will appear. Therefore, you will spend a bunch of time closing each graph.

    **NB**: You cannot specify the output file name here! By default, the file name will
    be the first 14 characters of the FASTA header followed by the filetype as specified 
    by filetype. If you wish for the files to include a unique leading number (i.e. X_rest_of_name
    where X starts at 1 and increments) then set indexed_filenames to True. This can be useful if you
    have sequences where the 1st 14 characters may be identical, which would otherwise overwrite an 
    output file.

    Parameters
    -----------

    filepath : str 
        The path to where the .fasta file is located. The filepath should end in the file name. 
        For example (on MacOS):filepath="/Users/thisUser/Desktop/folder_of_seqs/interesting_proteins.fasta"
    
    DPI : int
        Dots-per-inch. Defines the resolution of the generated figure. Passed to the
        dpi argument in ``matplotlib.pyplot.savefig()``.

    output_dir : str
        If provided, the output_dir variable defines the directory where file should besaved
        to be saved. This should be a writeable filepath. Default is None. Output files are 
        saved with filename as first 14 chars of fasta header (minus bad characters) plus the
        appropriate file extension, as defined by filetype.

    output_filetype : str
        String that defines the output filetype to be used. Must be one of pdf, png, jpg.

    invalid_sequence_action : str
        Tells the function how to deal with sequences that lack standard amino acids. Default is 
        convert, which as the name implies converts via standard rules. See 
        https://protfasta.readthedocs.io/en/latest/read_fasta.html for more information.

    indexed_filenames : bool
        Bool which, if set to true, means filenames start with an unique integer.
    
    pLDDT_version : string
        The network to use for prediction. Default is DEFAULT_NETWORK_PLDDT,
        which is defined at the top of /parameters.
        Options currently include V1 or V2 

    Returns
    ---------

    None
        No return object, but, the graph is saved to disk or displayed locally.

    """

    # Test to see if the data_file exists
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f'Datafile [{filepath:s}] does not exist')

    # Test to see if output directory exists
    if output_dir is not None:
        if not os.path.isdir(output_dir):
            raise FileNotFoundError(f'Proposed output directory could not be found')

    # check version and make sure it is an uppercase string
    pLDDT_version = _meta_tools.valid_version(pLDDT_version, 'pLDDT')

    # use protfasta to read in fasta file
    sequences =  _protfasta.read_fasta(filepath, invalid_sequence_action = invalid_sequence_action)


    # now for each sequence...
    idx_counter = 0
    for idx in tqdm(sequences):
        
        # increment the index counter...
        idx_counter = idx_counter + 1

        # grab the sequence and convert to upper as well
        local_sequence = sequences[idx].upper()

        # make sure file doesn't try to save if no output dir specified
        if output_dir is not None:

            # define the full filename with filetype. NOTE - we use os.sep as an OS-independent way to define
            # filename and filepath. This may end up with the filename containing a double slash, but this is fine
            # and matplotlib deals with this appropriately. This should be a POSIX-compliant way to do cross-platform
            # file writing
            if indexed_filenames:
                filename = output_dir + os.sep + f"{idx_counter:d}_" + _meta_tools.sanitize_filename(idx)[0:14] + f".{output_filetype:s}"
            else:
                filename = output_dir + os.sep + _meta_tools.sanitize_filename(idx)[0:14] + f".{output_filetype:s}"

            # define title (including bad chars)
            title = idx[0:14]

            # plot!        
            graph_pLDDT(local_sequence, title=title, DPI=DPI, output_file=filename, pLDDT_version=pLDDT_version)

        # if no output_dir specified just graph the seq        
        else:
            # define title (including bad chars)
            title = idx[0:14]      
            graph_pLDDT(local_sequence, title=title, DPI=DPI, pLDDT_version=pLDDT_version)


# ..........................................................................................
#
def predict_disorder_uniprot(uniprot_id, normalized=True, version=DEFAULT_NETWORK):
    """
    Function to return disorder of a single input sequence. Uses a 
    Uniprot ID to get the sequence.

    Parameters
    ------------

    uniprot_ID : str
         The uniprot ID of the sequence to predict

    no_ID : str
         The uniprot ID of the sequence to predict

    version : string
        The network to use for prediction. Default is DEFAULT_NETWORK,
        which is defined at the top of /parameters.
        Options currently include V1, V2, or V3. 

    Returns
    ----------

    None
        No return object, but, the graph is saved to disk or displayed locally.
    
    """
    # check version and make sure it is an uppercase string
    version = _meta_tools.valid_version(version, 'disorder')

    # fetch sequence from Uniprot
    sequence = _getseq(uniprot_id)[1]
        
    # return predicted values of disorder for sequence
    return _predict(sequence, normalized=normalized, version=version)


# ..........................................................................................
#
def predict_pLDDT_uniprot(uniprot_id, pLDDT_version=DEFAULT_NETWORK_PLDDT):
    """
    Function to return pLDDT score of a single input sequence. Uses a 
    Uniprot ID to get the sequence.

    Parameters
    ------------

    uniprot_ID : str
         The uniprot ID of the sequence to predict

    pLDDT_version : string
        The network to use for prediction. Default is DEFAULT_NETWORK_PLDDT,
        which is defined at the top of /parameters.
        Options currently include V1 or V2 

    Returns
    ----------

    None
        No return object, but, the graph is saved to disk or displayed locally.
    
    """
    # fetch sequence from Uniprot
    sequence = _getseq(uniprot_id)[1]

    # check version and make sure it is an uppercase string
    pLDDT_version = _meta_tools.valid_version(pLDDT_version, 'pLDDT')
        
    # return predicted values of disorder for sequence
    return _predict_pLDDT(sequence, version=pLDDT_version)


# ..........................................................................................
#
def graph_disorder_uniprot(uniprot_id, 
                           title = 'Predicted protein disorder',
                           pLDDT_scores=False, 
                           disorder_threshold = None,
                           shaded_regions = None,
                           shaded_region_color = 'red',
                           DPI=150, 
                           output_file=None,
                           version=DEFAULT_NETWORK,
                           pLDDT_version=DEFAULT_NETWORK_PLDDT):

    """
    Function to plot the disorder of an input sequece. Displays immediately.

    Parameters
    -------------

    sequence : str 
        Input amino acid sequence (as string) to be predicted.

    title : str
        Sets the title of the generated figure. Default = "Predicted protein disorder"

    pLDDT_scores : Bool
        Sets whether to include the predicted pLDDT scores from
        AlphaFold2

    disorder_threshold : float
        Set to None by default such that it will change depending of if the user
        sets legacy to True of if legacy remains = False. Can still be set manually.

        Sets a threshold which draws a horizontal black line as a visual guide along
        the length of the figure. Must be a value between 0 and 1.
    
    shaded_regions : list of lists
        A list of lists, where sub-elements are of length 2 and contain start and end
        values for regions to be shaded. Assumes that sanity checking on positions has
        already been done. Default is None, but if there were specific regions you wanted
        to highlight this might, for example, look like shaded_regions=[[1,10],[40,50]], 
        which would shade between 1 and 10 and then between 40 and 50. This can be useful
        to either highlight specific IDRs or specific folded domains

    shaded_region_color : str
        String that defines the color of the shaded region. The shaded region is always
        set with an alpha of 0.3 but the color can be any valid matplotlib color name
        or a hex color string (i.e. "#ff0000" is red).
    
    DPI : int
        Dots-per-inch. Defines the resolution of the generated figure. Passed to the
        dpi argument in ``matplotlib.pyplot.savefig()``.

    output_file : str
        If provided, the output_file variable defines the location and type of the file
        to be saved. This should be a file location and filename with a valid matplotlib
        extension (such as .png, or .pdf) and, if provided, this value is passed directly
        to the ``matplotlib.pyplot.savefig()`` function as the ``fname`` parameter. 
        Default = None.

    version : string
        The network to use for prediction. Default is DEFAULT_NETWORK,
        which is defined at the top of /parameters.
        Options currently include V1, V2, or V3. 

    pLDDT_version : string
        The network to use for prediction. Default is DEFAULT_NETWORK_PLDDT,
        which is defined at the top of /parameters.
        Options currently include V1 or V2         

    Returns
    ----------

    None
        No return object, but, the graph is saved to disk or displayed locally.
    
    """
    # check version and make sure it is an uppercase string
    version = _meta_tools.valid_version(version, 'disorder')

    if disorder_threshold==None:
        disorder_threshold=metapredict_networks[version]['parameters']['disorder_threshold']

    # check version and make sure it is an uppercase string
    pLDDT_version = _meta_tools.valid_version(pLDDT_version, 'pLDDT')

    # check that a valid range was passed for 
    _meta_tools.valid_range(disorder_threshold, 0.0, 1.0)

    # grab uniprot sequence
    sequence = _getseq(uniprot_id)[1]

    # graph sequence
    _graph(sequence, title=title, pLDDT_scores=pLDDT_scores, disorder_threshold=disorder_threshold, shaded_regions=shaded_regions, 
        shaded_region_color=shaded_region_color, DPI=DPI, output_file = output_file, 
        version=version, pLDDT_version=pLDDT_version) 
    

# ..........................................................................................
#
def graph_pLDDT_uniprot(uniprot_id, 
                           title = 'Predicted AF2 pLDDT Scores', 
                           shaded_regions = None,
                           shaded_region_color = 'red',
                           DPI=150, 
                           output_file=None,
                           pLDDT_version=DEFAULT_NETWORK_PLDDT):

    """
    Function to plot the disorder of an input sequece. Displays immediately.

    Parameters
    -------------

    sequence : str 
        Input amino acid sequence (as string) to be predicted.

    title : str
        Sets the title of the generated figure. Default = "Predicted protein disorder"
    
    shaded_regions : list of lists
        A list of lists, where sub-elements are of length 2 and contain start and end
        values for regions to be shaded. Assumes that sanity checking on positions has
        already been done. Default is None, but if there were specific regions you wanted
        to highlight this might, for example, look like shaded_regions=[[1,10],[40,50]], 
        which would shade between 1 and 10 and then between 40 and 50. This can be useful
        to either highlight specific IDRs or specific folded domains

    shaded_region_color : str
        String that defines the color of the shaded region. The shaded region is always
        set with an alpha of 0.3 but the color can be any valid matplotlib color name
        or a hex color string (i.e. "#ff0000" is red).
    
    DPI : int
        Dots-per-inch. Defines the resolution of the generated figure. Passed to the
        dpi argument in ``matplotlib.pyplot.savefig()``.

    output_file : str
        If provided, the output_file variable defines the location and type of the file
        to be saved. This should be a file location and filename with a valid matplotlib
        extension (such as .png, or .pdf) and, if provided, this value is passed directly
        to the ``matplotlib.pyplot.savefig()`` function as the ``fname`` parameter. 
        Default = None.

    pLDDT_version : string
        The network to use for prediction. Default is DEFAULT_NETWORK_PLDDT,
        which is defined at the top of /parameters.
        Options currently include V1 or V2    

    Returns
    ----------

    None
        No return object, but, the graph is saved to disk or displayed locally.
    
    """

    # grab uniprot sequence
    sequence = _getseq(uniprot_id)[1]

    # check version and make sure it is an uppercase string
    pLDDT_version = _meta_tools.valid_version(pLDDT_version, 'pLDDT')

    # graph sequence
    _graph(sequence, title=title, disorder_scores=False, pLDDT_scores=True, 
        shaded_regions=shaded_regions, shaded_region_color=shaded_region_color, 
        DPI=DPI, output_file = output_file, pLDDT_version=pLDDT_version) 
    
# ..........................................................................................
#
def predict_disorder_domains_uniprot(uniprot_id, 
                             disorder_threshold=None, 
                             minimum_IDR_size=12, 
                             minimum_folded_domain=50,
                             gap_closure=10, 
                             normalized=True,
                             return_numpy=True,
                             version=DEFAULT_NETWORK):
    """

    This function takes an amino acid sequence, a disorder score, and 
    returns either a DisorderObjec 4-position tuple with the information
    listed below.

    Parameters
    -------------

    uniprot_ID : String
        The uniprot ID of the sequence to predict

    sequence : str
        Amino acid sequence

    disorder_threshold : float
        Set to None by default such that the threshold value is is dependent
        on whether legacy is set to True. The default for legacy is 0.42, the
        default for the new metapredict is 0.5.

        Value that defines what 'disordered' is based on the metapredict 
        disorder score. 

    minimum_IDR_size : int
        Defines the smallest possible IDR. This is a hard limit - i.e. we 
        CANNOT get IDRs smaller than this. Default = 12.

    minimum_folded_domain : int
        Defines where we expect the limit of small folded domains to be. 
        This is NOT a hard limit and functions to modulate the removal of 
        large gaps (i.e. gaps less than this size are treated less strictly). 
        Note that, in addition, gaps < 35 are evaluated with a threshold of 
        0.35*disorder_threshold and gaps < 20 are evaluated with a threshold         
        of 0.25*disorder_threshold. These two lengthscales were decided based 
        on the fact that coiled-coiled regions (which are IDRs in isolation) 
        often show up with reduced apparent disorder within IDRs, and but can 
        be as short as 20-30 residues. The folded_domain_threshold is used 
        based on the idea that it allows a 'shortest reasonable' folded domain 
        to be identified. Default=50.

    gap_closure : int
        Defines the largest gap that would be 'closed'. Gaps here refer to a 
        scenario in which you have two groups of disordered residues seprated 
        by a 'gap' of un-disordered residues. In general large gap sizes will 
        favour larger contigous IDRs. It's worth noting that gap_closure becomes 
        relevant only when minimum_region_size becomes very small (i.e. < 5) 
        because really gaps emerge when the smoothed disorder fit is "noisy", but 
        when smoothed gaps are increasingly rare. Default=10.

    return_numpy : bool
        Flag which if set to true means all numerical types are returned
        as numpy.ndlist. Default is True

    version : string
        The network to use for prediction. Default is DEFAULT_NETWORK,
        which is defined at the top of /parameters.
        Options currently include V1, V2, or V3. 

    Returns
    ---------
    DisorderObject
        Returns a DisorderObject. DisorderObject has 7 dot variables:

        .sequence : str    
            Amino acid sequence 

        .disorder : list or np.ndaarray
            Hybrid disorder score

        .disordered_domain_boundaries : list
            List of domain boundaries for IDRs using Python indexing

        .folded_domain_boundaries : list
            List of domain boundaries for folded domains using Python indexing

        .disordered_domains : list
            List of the actual sequences for IDRs

        .folded_domains : list
            List of the actual sequences for folded domains


    """

    # check version and make sure it is an uppercase string
    version = _meta_tools.valid_version(version, 'disorder')

    if disorder_threshold==None:
        disorder_threshold=metapredict_networks[version]['parameters']['disorder_threshold']

    sequence = _getseq(uniprot_id)[1]

    DisObj = _predict(sequence, normalized=normalized, version=version, return_domains=True,
                                disorder_threshold=disorder_threshold, minimum_IDR_size=minimum_IDR_size,
                                minimum_folded_domain=minimum_folded_domain,return_numpy=return_numpy,
                                gap_closure=gap_closure)

    return DisObj



# ..........................................................................................
#
def predict_disorder_caid(input_fasta, output_path, version=DEFAULT_NETWORK):
    '''
    executing script for generating a caid-compliant output file for disorder
    predictions using a .fasta file as the input.

    Parameters
    -----------
    input_fasta : str
        the input file as a string that includes the file path preceeding
        the file name if the file is not in the curdir

    output_path : str
        the path where to save the output files.

    version : string
        The network to use for prediction. Default is DEFAULT_NETWORK,
        which is defined at the top of /parameters.
        Options currently include V1, V2, or V3. 

    Returns
    --------
    None
        Does not return anything, saves a file to the destination output file

    '''

    # check version and make sure it is an uppercase string
    version = _meta_tools.valid_version(version, 'disorder')

    # read in the ids and seqs as a list of lists where each list has a first element that corresponds
    # to the ID and the second corresponds to the sequence. Convert invalid amino acids if needed.
    entry_id_and_seqs = _protfasta.read_fasta(input_fasta, return_list=False, invalid_sequence_action = 'convert')

    # predict
    predictions = _predict(entry_id_and_seqs, version=version, return_numpy=False)

    # write the output file
    _meta_tools.write_caid_format(predictions, output_path, version=version)


