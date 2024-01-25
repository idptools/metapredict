##
## metapredict
## A protein disorder predictor based on a BRNN (IDP-Parrot) trained on the consensus disorder values from 
## 8 disorder predictors from 12 proteomes.
##
import sys
import importlib.util

# import user-facing functions
from metapredict.meta import *
from metapredict.parameters import DEFAULT_NETWORK
from metapredict.backend.network_parameters import metapredict_networks 
from metapredict.backend.predictor import predict

import os
from importlib.metadata import version, PackageNotFoundError

# import current version
from ._version import __version__

# To crash on LIBOMP error set this to False
IGNORE_LIBOMP_ERROR = True

# ------------------------------------------------------------
#
# Handle omplib error 
if IGNORE_LIBOMP_ERROR:
    if sys.platform == 'darwin':
        os.environ['KMP_DUPLICATE_LIB_OK']='True'



# Standardized function to check performance
def print_performance(seq_len=500, num_seqs=512, variable_length=False,
                        version=DEFAULT_NETWORK, disable_batch=False,
                        verbose=True, device=None):
    """
    Function that lets you test metapredicts performance on your local hardware.

    Parameters
    --------------
    seq_len : int 
        Length of each random sequence to be tested. Default = 500.

    num_seqs : int
        Number of sequences to compute over. Default = 512.

    variable_length : bool
        Flag which, if provided, means sequences vary between 20 and seq_len length.

    version : str
        The version of metapredict to use. Can specify 'legacy', 'v1' (which are the
        same thing), 'v2', or 'v3'. Default is DEFAULT_NETWORK, which is the network
        set as default in /backend/network_parameters.

    disable_batch : bool
        Flag which, if set to true, disables batch predictions.

    verbose : bool
        Flag which, if true, means the function prints a summary when finished. If 
        false simply returns an integer

    device : str
        Flag which, if provided, sets the device to use. If not provided, defaults to
        the a cuda GPU if available and a CPU if not.


    Returns
    ---------------
    int
        Returns the nearest number of sequences-per-second metapredict is currently
        predicting. For ref, on a spring 2020 MBP this value was ~10,000 sequences per
        second.

    """

    # make version uppercase
    version=version.upper()

    # make sure valid network
    if version not in list(metapredict_networks.keys()):
        raise MetapredictError(f'Specified version of {version} is not available. Use {list(metapredict_networks.keys())}')

    # this is a bit bad but, only import random is this FX is called
    import random
    import time

    # set valid amino acids
    VALID_AMINO_ACIDS = ['A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y']

    def genseq(n):
        """
        Function that generates a random 
        """
        if variable_length:
            local_n = random.randint(20,seq_len)
        else:
            local_n = n
        return "".join([random.choice(VALID_AMINO_ACIDS) for i in range(local_n)])

    # list to hold seqs. 
    seqs = []
    n_res = 0
    for i in range(num_seqs):
        s = genseq(seq_len)
        seqs.append(s)
        n_res = n_res + len(s)

    # track time
    start = time.time()

    # carry out prediction.
    predict(seqs, network=version, force_disable_batch=disable_batch, 
        use_device=device, normalized=False, show_progress_bar=verbose,
        round_values=False)

    # get residues predicted per second
    end = time.time()
    r_per_second = (n_res)/(end - start)

    # if verbose, print out resideus per second
    if verbose:
        print(f'Predicting {r_per_second:f} residues per second!')

    # return residues per second
    return r_per_second
    


def print_metapredict_legacy_network_version(return_network_info=False):
    """
    Function that returns a string with the current trained network version
    used in disorder prediction. This is useful to know if updated versions
    of the network are provided, which will always accompany a version bump
    so prior versions of the code will always be available.

    Parameters
    ----------
    return_network_info : bool
        Flag which, if set to True, returns the network information as well as the version.

    Returns
    ---------
    str 
        Returns a string in the format v<version information>
    
    """
    if return_network_info==False:
        return metapredict_networks['V1']['parameters']['public_name']
    else:
        return f"{metapredict_networks['parameters']['public_name']}\n{metapredict_networks['V1']['parameters']['info']}"


def print_metapredict_network_version(return_network_info=False):
    """
    Function that returns a string with the current trained network version
    used in disorder prediction. This is useful to know if updated versions
    of the network are provided, which will always accompany a version bump
    so prior versions of the code will always be available.

    Parameters
    ----------
    print_network_info : bool
        Flag which, if set to True, returns the network information as well as the version.


    Returns
    ---------
    str 
        Returns a string in the format v<version information>
    """
    if return_network_info==False:
        return metapredict_networks[DEFAULT_NETWORK]
    else:
        return f"{metapredict_networks[DEFAULT_NETWORK]}\n{metapredict_networks[DEFAULT_NETWORK]['parameters']['info']}"
