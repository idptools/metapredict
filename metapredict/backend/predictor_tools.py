'''
various helpful tools for the predictor class
'''
import re
import itertools
import torch
from typing import Union, List, Dict, Tuple, Optional
from functools import lru_cache

from metapredict.backend.data_structures import DisorderObject as _DisorderObject
from metapredict.backend import domain_definition as _domain_definition
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
    return {length: list(seqs) for length, seqs in 
            itertools.groupby(sorted(inseqs, key=len), key=len)}

# ....................................................................................
#
@lru_cache(maxsize=1)
def _get_available_devices() -> list:
    '''
    Cached function to get available devices as a list of strings.
    '''
    available_devices = ['cpu']
    if torch.cuda.is_available():
        available_devices.append('cuda')
        for i in range(torch.cuda.device_count()):
            available_devices.append(f'cuda:{i}')
    if torch.backends.mps.is_available():
        available_devices.append('mps')
    return available_devices

def _validate_mps_device() -> str:
    '''
    Validate and return the MPS device if available.
    '''
    if not torch.backends.mps.is_available():
        raise MetapredictError("MPS is not available.")
    return 'mps'

def _validate_cuda_device(device_str) -> str:
    '''
    Validate and return the CUDA device if available.
    '''

    if not torch.cuda.is_available():
        raise MetapredictError("CUDA is not available.")
    
    if device_str == 'cuda':
        return 'cuda'
    
    if not device_str.startswith('cuda:'):
        raise MetapredictError(f"Invalid CUDA device specification: {device_str}")
    
    try:
        device_index = int(device_str.split(':')[1])
        if device_index < 0 or device_index >= torch.cuda.device_count():
            raise MetapredictError(f"CUDA device {device_str} is not available.")
    except (ValueError, IndexError):
        raise MetapredictError(f"Invalid CUDA device specification: {device_str}")
    
    num_devices = torch.cuda.device_count()
    if device_index >= num_devices:
        available_indices = list(range(num_devices))
        raise MetapredictError(
            f"CUDA device {device_str} is not available. "
            f"Available devices: cuda, {', '.join(f'cuda:{i}' for i in available_indices)}"
        )    
    
    return device_str


    
def check_device(use_device: Optional[Union[str, int]] = None, 
                default_device: str = 'cuda') -> str:
    """
    Validate and normalize device specification.
    
    Args:
        use_device: Device specification ('cpu', 'mps', 'cuda', 'cuda:N', or int)
        default_device: Fallback device when use_device is None
        
    Returns:
        Normalized device string
        
    Raises:
        MetapredictError: If device is invalid or unavailable
        
    Examples:
        >>> check_device('cpu')
        'cpu'
        >>> check_device(0)  # Converts to 'cuda:0'
        'cuda:0'
        >>> check_device(None, 'cuda')  # Falls back to CUDA if available
        'cuda'
    """
    if use_device is None:
        # check which devices are available. 
        available_devices = _get_available_devices()
        if not available_devices:
            raise MetapredictError("No available devices found.")
        if default_device in available_devices:
            use_device = default_device
        else:
            # fall back to cpu
            use_device = 'cpu'
    else:
        if isinstance(use_device, int):
            use_device = f'cuda:{use_device}'

    # make sure lowercase
    use_device = use_device.lower()

    # validate and return.
    if use_device == 'cpu':
        return 'cpu'
    elif use_device == 'mps':
        return _validate_mps_device()
    elif use_device.startswith('cuda'):
        return _validate_cuda_device(use_device)
    else:
        raise MetapredictError(f"Invalid device specification: {use_device}")