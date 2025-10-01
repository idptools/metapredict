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
import weakref
from functools import lru_cache
from typing import Union, List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

# local imports
from metapredict.backend.meta_tools import exceeds_max_length
from metapredict.backend.predictor_tools import build_DisorderObject as _build_DisorderObject
from metapredict.backend.predictor_tools import size_filter as _size_filter
from metapredict.backend.predictor_tools import handle_input as _handle_input
from metapredict.backend.predictor_tools import check_device as _check_device
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

    def __init__(self,
                 device=None, 
                 default_device='cuda'):
        self.device = device
        self.default_device = default_device
        self.available_disorder_models = list(metapredict_networks.keys())
        self.available_plddt_models = list(pplddt_networks.keys())

        # model caches
        self._model_cache = {}
        
        # Cache for model parameters to avoid repeated dictionary lookups
        self._params_cache = {}
        
        # Performance optimization flags
        self._compiled_models = {}  # Cache for torch.compile
        self._use_amp = False  # Automatic Mixed Precision (can be enabled per prediction)
        
        # Enable TF32 for faster matrix multiplications on Ampere+ GPUs
        if torch.cuda.is_available():
            torch.set_float32_matmul_precision('high')
        
        # Initialize device
        self._verify_device()


    def _verify_device(self, device=None):
        """
        Verify that the specified device is available for use.
        """
        if device is not None:
            return _check_device(device, self.default_device)
        self.device = _check_device(self.device, self.default_device)
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
        
        # Optionally compile model for faster inference (PyTorch 2.0+)
        # This provides 20-30% speedup on average
        if hasattr(torch, 'compile') and cache_key not in self._compiled_models:
            try:
                # Use reduce-overhead mode for inference
                compiled_model = torch.compile(model, mode='reduce-overhead')
                self._compiled_models[cache_key] = weakref.ref(compiled_model)
            except Exception:
                # Fall back to uncompiled if compilation fails
                pass
        
        return model
    
    def _normalize_outputs(self, outputs, normalized=True, round_values=True):
        """
        Normalize and round outputs efficiently.
        
        Parameters
        ----------
        outputs : np.ndarray
            Raw model outputs
        normalized : bool
            Whether to clip values between 0 and 1
        round_values : bool
            Whether to round to 4 decimal places
            
        Returns
        -------
        np.ndarray
            Processed outputs
        """
        if normalized and round_values:
            return np.round(np.clip(outputs, a_min=0, a_max=1), 4)
        elif normalized:
            return np.clip(outputs, a_min=0, a_max=1)
        elif round_values:
            return np.round(outputs, 4)
        return outputs
    
    def modulate_plddt_output(self, outputs, plddt_version,
                              return_decimals=False,
                              return_as_disorder_score=False,
                              plddt_base=0.35, plddt_top=0.95):
        """
        modulate pLDDT outputs to either return as decimals or as disorder scores.
        Parameters
        ----------
        outputs : np.ndarray
            Raw pLDDT outputs from the model
        plddt_version : str
            The version of the pLDDT model used ('V1' or 'V2')
        return_decimals : bool
            Whether to return pLDDT as decimals (0-1)
        return_as_disorder_score : bool
            Whether to return pLDDT as disorder scores (1 - pLDDT)
        plddt_base : float
            Base value for scaling pLDDT to disorder score
        plddt_top : float
            Top value for scaling pLDDT to disorder score
        Returns
        -------
        np.ndarray
            Processed pLDDT outputs
        """
        # see if we are returning the plddt as disorder scores. 
        if return_as_disorder_score==True:
            return_decimals=True

        # see if we are return pLDDT values or raw decimal values.
        if return_decimals==True:
            if plddt_version=='V1':
                multiplier=0.01
            else:
                multiplier=1
            max_val_clipped=1
        else:
            if plddt_version=='V1':
                multiplier=1
            else:
                multiplier=100
            max_val_clipped=100    

        # mutiply
        outputs=outputs*multiplier

        if return_as_disorder_score==True:
            outputs = outputs-plddt_base
            outputs = outputs*(1/(plddt_top-plddt_base))
            # means value of 1 = disordered and 0 is disordered
            outputs = 1-outputs 
        
    def _forward_pass(self, model, packed_seqs, model_parameters):
        """
        Execute forward pass through the model.
        
        Parameters
        ----------
        model : nn.Module
            The model to use for prediction
        packed_seqs : PackedSequence
            Packed and padded sequences
        model_parameters : dict
            Model parameters dictionary
            
        Returns
        -------
        torch.Tensor
            Model outputs (unpacked)
        """
        if model_parameters['used_lightning']==False:
            # For BRNN_MtM: LSTM can handle PackedSequence directly
            lstm_out, _ = model.lstm(packed_seqs)
            # unpack sequences
            lstm_out, _ = torch.nn.utils.rnn.pad_packed_sequence(lstm_out, batch_first=True)
            outputs = model.fc(lstm_out)
        else:
            # For Lightning models: LSTM can handle PackedSequence, but layer_norm cannot
            # So we pass PackedSequence to LSTM, then unpack before layer_norm
            lstm_out, _ = model.lstm(packed_seqs)
            # unpack sequences before layer_norm
            lstm_out, _ = torch.nn.utils.rnn.pad_packed_sequence(lstm_out, batch_first=True)
            # Apply layer_norm and linear layers
            outputs = model.layer_norm(lstm_out)
            for layer in model.linear_layers:
                outputs = layer(outputs)
        
        return outputs
    
    def enable_amp(self, enable=True):
        """
        Enable or disable Automatic Mixed Precision (AMP) for faster inference on CUDA.
        
        AMP can provide 20-50% speedup on modern GPUs (Volta, Turing, Ampere+)
        with minimal accuracy loss. Only works with CUDA devices.
        
        Parameters
        ----------
        enable : bool
            Whether to enable AMP (default: True)
        """
        self._use_amp = enable
        if enable and torch.cuda.is_available():
            print("AMP enabled. Predictions will use mixed precision on CUDA.")
        elif enable and not torch.cuda.is_available():
            print("Warning: AMP requested but CUDA not available. AMP will be disabled.")

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
        
        Returns
        -------
        dict
            Dictionary with model names as keys and whether they're loaded as values.
        """
        loaded = {}
        for cache_key in list(self._model_cache.keys()):
            model_ref = self._model_cache[cache_key]
            model = model_ref()
            if model is not None:
                loaded[cache_key] = True
            else:
                # Clean up dead references
                del self._model_cache[cache_key]
                loaded[cache_key] = False
        return loaded
    
    def get_cache_info(self):
        """
        Get detailed information about the model cache.
        
        Returns
        -------
        dict
            Information about cached models including count and memory usage estimate.
        """
        active_models = []
        dead_refs = []
        
        for cache_key in list(self._model_cache.keys()):
            model_ref = self._model_cache[cache_key]
            model = model_ref()
            if model is not None:
                active_models.append(cache_key)
            else:
                dead_refs.append(cache_key)
        
        # Clean up dead references
        for key in dead_refs:
            del self._model_cache[key]
        
        return {
            'active_models': active_models,
            'active_count': len(active_models),
            'cleaned_dead_refs': len(dead_refs)
        }
    
    def set_device(self, device: Optional[str] = None):
        """
        Set the device for computation.

        Parameters
        ----------
        device : str, optional
            The device to use for computation. If None, the default device will be used.
            Default is None.
        """
        self.device = device
        self._verify_device()
        self._clear_models()  # Clear models to ensure they are reloaded on the new device
    
    def predict(self, 
                inseqs: Union[str, List[str]],
                prediction_type: str,
                model_version: str = None,  
                return_domains: bool = False,
                device: Optional[str] = None, 
                show_progress_bar: bool = False,
                normalized: bool = True,
                round_values: bool = True,
                return_decimals: bool = False,
                return_as_disorder_score: bool = False,
                disorder_threshold: float = None,
                minimum_IDR_size: int = 12,
                minimum_folded_domain: int = 50,
                gap_closure: int = 10,
                use_slow: bool = False
               ) -> List[np.ndarray]:
        """
        Predict disorder or plddt scores for input sequences where input
        sequences are either a single sequence or a list of sequences.

        Parameters
        -----------
        inseqs : str, list
            A single amino acid sequence (str), a list of amino acid sequences (list).
        prediction_type : str
            The type of prediction to perform. Options are 'disorder' or 'plddt'.
        model_version : str
            The version of the model to use for prediction. For disorder prediction, available models are:
            'v1', 'v2', 'v3'
            For pLDDT prediction, available models are:
            'v1', 'v2'
        return_domains : bool, optional
            Whether to return DisorderDomain objects instead of raw scores. Only valid for disorder predictions.
        device : str, optional
            The device to use for computation. If None, the default device will be used.
            Default is None.
        show_progress_bar : bool, optional
            Whether to display a progress bar during prediction. Default is False.
        normalized : bool, optional
            Whether to normalize the output scores to between 0 and 1. Default is True.
        round_values : bool, optional
            Whether to round the output scores to 4 decimal places. Default is True.
        return_decimals : bool, optional
            For pLDDT predictions, whether to return scores as decimals (0-1)
            instead of percentages (0-100). Default is False.
        return_as_disorder_score : bool, optional  
            For pLDDT predictions, whether to return scores as disorder scores
            (1 - pLDDT). Default is False.
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
        Returns
        -----------
        dict
            A dictionary with sequences as keys and predicted scores as values.
        """
        # verify device
        if device is None:
            device = self.device
        device = self._verify_device(device)

        if 'cuda' in str(self.device):
            if exceeds_max_length(inseqs, max_length=MAX_CUDA_LENGTH):
                raise MetapredictError(f'One of the input sequences is too long to run on GPU. The max length for a sequence on a CUDA GPU is {MAX_CUDA_LENGTH}.\nPlease use CPU if you want to run sequences longer than 65535 amino acids.')

        # make sure prediction_type is either disorder or plddt
        prediction_type=prediction_type.lower()
        if prediction_type not in ['disorder', 'plddt']:
            raise MetapredictError(f'Invalid prediction_type: {prediction_type}. Must be "disorder" or "plddt".')
        
        # if model_version is None, set to default
        if model_version is None:
            if prediction_type=='disorder':
                model_version=DEFAULT_NETWORK
                # set parameters to metapredict_networks
                available_params = metapredict_networks
            else:
                model_version=DEFAULT_NETWORK_PLDDT
                # set parameters to pplddt_networks
                available_params = pplddt_networks
        else:
            # format user input model version
            model_version=self._format_model_string(model_version)
            
            # check that model_version is valid and set available_params
            if prediction_type=='disorder':
                if model_version not in metapredict_networks:
                    raise MetapredictError(
                        f'Invalid model_version: {model_version}. '
                        f'Available disorder models: {", ".join(metapredict_networks.keys())}'
                    )
                available_params = metapredict_networks
            else:
                if model_version not in pplddt_networks:
                    raise MetapredictError(
                        f'Invalid model_version: {model_version}. '
                        f'Available pLDDT models: {", ".join(pplddt_networks.keys())}'
                    )
                available_params = pplddt_networks
        
        # if user input is a string, convert to list
        if isinstance(inseqs, str):
            inseqs = [inseqs]
        elif not isinstance(inseqs, list):
            raise MetapredictError('Input sequences must be a string or a list of strings.')
        
        # now load model. First get info on model and model parameters.
        model_network_name = available_params[model_version]['weights']
        model_parameters = available_params[model_version]['parameters']
        predictor_path = os.path.join(os.path.dirname(__file__), 'networks', f'{model_network_name}')
        cache_name = model_network_name.replace('.ckpt', '').replace('.pt', '')

        # load model (model is already on device and in eval mode after loading)
        loaded_model = self._get_model(cache_name, model_parameters, predictor_path, device)
        loaded_model.to(device)  # Ensure on correct device
        loaded_model.eval()  # Ensure in eval mode

        # see if we can use inference mode othewise will use torch.no_grad
        _inference_ctx = (
            torch.inference_mode if hasattr(torch, "inference_mode") else torch.no_grad
            )
        
        # initialize the return dictionary that maps sequence to
        # disorder profile
        pred_dict = {}

        # sort the list of sequences by length
        inseqs.sort(key=len, reverse=True)
        
        # we will be using pack-n-pad.
        # load seqs into DataLoader
        seq_loader = DataLoader(inseqs, batch_size=model_parameters['batch_size'], shuffle=False) 
        num_batches=len(seq_loader)
        
        # set progress bar info if we are going to display it. 
        # have to do this differently because you can't iterate over DataLoader
        # and get tqdm to update. 
        if show_progress_bar:
            pbar = tqdm(total=num_batches)

        # Pre-encode all sequences in parallel (move encoding outside the batch loop for better performance)
        # Use ThreadPoolExecutor for parallel encoding (GIL released during numpy operations)
        num_workers = min(4, multiprocessing.cpu_count())  # Limit workers to avoid overhead
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            encoded_list = list(executor.map(lambda s: encode_sequence.one_hot(s).float(), inseqs))
        encoded_seqs = dict(zip(inseqs, encoded_list))
        
        # Determine if we should use compiled model
        model_to_use = loaded_model
        cache_key = f"{cache_name}_{device}"
        if cache_key in self._compiled_models:
            compiled_ref = self._compiled_models[cache_key]
            compiled_model = compiled_ref()
            if compiled_model is not None:
                model_to_use = compiled_model
        
        # iterate through each batch
        for batch in seq_loader:
            # Use pre-encoded sequences
            seqs_padded = torch.nn.utils.rnn.pad_sequence([encoded_seqs[seq] for seq in batch], batch_first=True)
            lengths = torch.tensor([len(seq) for seq in batch], dtype=torch.long)

            # Move to device with pin_memory for faster transfer, use non_blocking for async transfer
            if device != 'cpu':
                seqs_padded = seqs_padded.pin_memory().to(device, non_blocking=True)
                packed_seqs = torch.nn.utils.rnn.pack_padded_sequence(seqs_padded, lengths.cpu(), batch_first=True, enforce_sorted=True)
            else:
                packed_seqs = torch.nn.utils.rnn.pack_padded_sequence(seqs_padded, lengths, batch_first=True, enforce_sorted=True)

            # Forward pass with inference mode and optional AMP
            with _inference_ctx():
                # Use autocast for mixed precision if enabled and on CUDA
                use_amp = self._use_amp and device.startswith('cuda')
                
                if use_amp:
                    with torch.cuda.amp.autocast():
                        outputs = self._forward_pass(model_to_use, packed_seqs, model_parameters)
                else:
                    outputs = self._forward_pass(model_to_use, packed_seqs, model_parameters)

            # convert to numpy array and move to cpu (non-blocking for async transfer)
            if device != 'cpu':
                outputs = outputs.detach().cpu().numpy()
            else:
                outputs = outputs.detach().numpy()
            
            # if pLDDT, modulate outputs
            if prediction_type=='plddt':
                outputs = self.modulate_plddt_output(
                    outputs, 
                    model_version, 
                    return_decimals=return_decimals, 
                    return_as_disorder_score=return_as_disorder_score
                )

            # Normalize outputs using helper method
            outputs = self._normalize_outputs(outputs, normalized, round_values)

            # get individual seqs ignoring padded parts (vectorized where possible)
            lengths_list = lengths.tolist() if isinstance(lengths, torch.Tensor) else lengths
            for seq_num, (seq, length) in enumerate(zip(batch, lengths_list)):
                pred_dict[seq] = outputs[seq_num, :length].ravel()  # ravel() is faster than flatten()

            if show_progress_bar:
                pbar.update(1)
        
        if return_domains:
            if prediction_type != 'disorder':
                raise MetapredictError('return_domains can only be True for disorder predictions.')
            if disorder_threshold is None:
                disorder_threshold=model_parameters['disorder_threshold']

            # we're going to first build a dictionary to map sequence to DisorderObject - this ensures
            # we only build one DO per sequence, even if we have multiple repetitve sequences
            seq2DisorderObject = {}

            # for each sequence in the prediction dictionary. Note this loop may take a second...
            for s in pred_dict:
                seq2DisorderObject[s] = _build_DisorderObject(s,
                                                             pred_dict[s],
                                                             disorder_threshold=disorder_threshold,
                                                             minimum_IDR_size=minimum_IDR_size, 
                                                             minimum_folded_domain=minimum_folded_domain,
                                                             gap_closure=gap_closure,
                                                             use_slow=use_slow)

        if show_progress_bar:
            pbar.close()
        
        return pred_dict
