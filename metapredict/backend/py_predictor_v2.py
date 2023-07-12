'''
backend stuff for metahybrid predictor. Metahybrid predictor is now the default
predictor for metapredict. The backend needs to be different
than that for orignal metapredict because of the very differences in versions of
PARROT that was used for training.

Credit for code below goes to Dan Griffith from the Holehouse Lab.
'''

'''
Python module for integrating a trained network directly into a Python workflow.
.............................................................................
idptools-parrot was developed by the Holehouse lab
     Original release ---- 2020
Question/comments/concerns? Raise an issue on github:
https://github.com/idptools/parrot
Licensed under the MIT license. 
'''

from metapredict.backend import brnn_architecture
from metapredict.backend import encode_sequence

import torch
import numpy as np
import os

def softmax(v):
    return (np.e ** v) / np.sum(np.e ** v)

class Predictor():
    """Class that for integrating a trained PARROT network into a Python workflow
    Usage:
    >>> from parrot import py_predictor
    >>> my_predictor = py_predictor.Predictor(</path/to/saved_network.pt>, 
                                                dtype={"sequence" or "residues"})
    >>> value = my_predictor.predict(AA_sequence)
    ***
    NOTE:   Assumes all sequences are composed of canonical amino acids and 
            that all networks were implemented using one-hot encoding.
    ***
    Attributesb
    ----------
    dtype : str
            Data format that the network was trained for. Either "sequence" or 
            "residues".
    num_layers : int
            Number of hidden layers in the trained network.
    hidden_vector_size : int
            Size of hidden vectoer in the trained network.
    n_classes : int
            Number of data classes that the network was trained for. If 1, then
            network is designed for regression task. If >1, then classification
            task with n_classes.
    network : PyTorch object
            Initialized PARROT network with loaded weights.
    """

    def __init__(self, saved_weights, dtype, gpuid='cpu'):
        """
        Parameters
        ----------
        saved_weghts : str or Path
                Location of the saved network weights. If a valid file is provided,
                network parameters will be dynamically read in an network will be 
                initialized.
        dtype : str
                Data format that the network was trained for. Either "sequence" or 
                "residues".

        gpuid : str
            By default set to 'cpu', but if a value is passed will try and override 
        
        """

        self.dtype = dtype

        # if gpuid is not set to cpu
        if gpuid != 'cpu':
            if torch.cuda.is_available():
                device_string = f"cuda:{gpuid}"
                device = torch.device(device_string)
            else:
                device_string = "cpu"
                device = torch.device(device_string)
        else:
            device_string = "cpu"
            device = torch.device(device_string)

        self.device = device
        self.device_string = device_string

        # load using the requested device
        loaded_model = torch.load(saved_weights, map_location=device)

        # Dynamically read in correct network size:
        self.num_layers = 0
        while True:
            s = f'lstm.weight_ih_l{self.num_layers}'
            try:
                temp = loaded_model[s]
                self.num_layers += 1
            except KeyError:
                break
        
        # Extract other network hyperparams           
        self.hidden_vector_size = int(np.shape(loaded_model['lstm.weight_ih_l0'])[0] / 4)
        self.n_classes = np.shape(loaded_model['fc.bias'])[0]

        # Instantiate network weights into Predictor() object - note we have to ensure the network
        # is loaded onto the same model as the device type
        self.network = brnn_architecture.BRNN_MtM(20, self.hidden_vector_size, 
                                                      self.num_layers, self.n_classes, device_string)     
        self.network.load_state_dict(loaded_model)


    def predict(self, seq):
        """Use the network to predict values for a single sequence of valid amino acids
        Parameters
        ----------
        seq : str
            Valid amino acid sequence
            
        Returns
        -------
        np.ndarray
            Returns a 1D np.ndarray the length of the sequence where each position
            is the prediction at that position.
        """

        # convert sequence to uppercase
        seq = seq.upper()

        # Convert to one-hot sequence vector
        seq_vector = encode_sequence.one_hot(seq)
        seq_vector = seq_vector.view(1, len(seq_vector), -1)  # formatting

        # Forward pass
        with torch.no_grad():
            prediction = self.network(seq_vector.float()).detach().numpy().flatten()

        # return the prediction
        return prediction
