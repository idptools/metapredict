#!/usr/bin/env python
'''
Rewrite of predictor.py to use a class instead of function-based
logic. Hoping to improve hadnling of models and improve performance. 
'''

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
import weakref
from functools import lru_cache
from typing import Union, List, Dict, Tuple, Optional

# local imports
from metapredict.backend.meta_tools import exceeds_max_length
from metapredict.backend.predictor_tools import build_DisorderObject as _build_DisorderObject
from metapredict.backend.predictor_tools import size_filter as _size_filter
from metapredict.backend.predictor_tools import check_device
from metapredict.backend.network_parameters import metapredict_networks, pplddt_networks
from metapredict.parameters import DEFAULT_NETWORK, DEFAULT_NETWORK_PLDDT, MAX_CUDA_LENGTH
from metapredict.backend import encode_sequence
from metapredict.backend import architectures
from metapredict.metapredict_exceptions import MetapredictError

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class MetapredictPredictor:
    """
    A predictor class that manages model loading as well as prediction functionality. 
    """

    def __init__(self, device=None, default_device='cuda'):
        self.device = device
        self.default_device = default_device

        # model caches
        self._model_cache = {}

    def _verify_device(self):
        """
        Verify that the specified device is available for use.
        """
        self.device = check_device(self.device, self.default_device)
        return self.device

    def _format_model_string(self, model_name: str) -> str:
        """
        Format the model string for loading.
        """
        # make sure the version is a string
        version_input=str(model_name)
        # set to be upper case.
        version_input=version_input.upper()

        # now convert over to what we need version to be. 
        if version_input=='LEGACY':
            version_input='V1'
        
        # if len version is 1, add a 'V' to the front. 
        if len(version_input)==1:
            version_input=f'V{version_input}'

        # make version uppercase
        version_input=version_input.upper()

        return version_input

    def _get_model(self, model_name, params, predictor_path, device):
        """
        Load and cache models with automatic cleanup for unused models.
        Models are kept alive as long as they're being used somewhere.
        """
        cache_key = f"{model_name}_{device}"
        
        # Check if we have a valid cached model
        if cache_key in self._model_cache:
            model_ref = self._model_cache[cache_key]
            model = model_ref()  # Get the actual model from weak reference
            if model is not None:
                return model
            else:
                # Model was garbage collected, remove the dead reference
                del self._model_cache[cache_key]

        # Load the model
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
        
        # Store weak reference to allow garbage collection
        self._model_cache[cache_key] = weakref.ref(model)
        return model

    def _clear_models(self):
        """
        Clear all cached models.
        """
        self._model_cache.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def get_loaded_models(self):
        """
        Get a list of all loaded models.
        """
        return [model_ref() for model_ref in self._model_cache.values() if model_ref() is not None]