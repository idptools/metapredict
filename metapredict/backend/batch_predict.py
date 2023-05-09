
import torch
import numpy as np

from torch.utils.data import DataLoader
from torch.nn.utils.rnn import pad_sequence

from tqdm import tqdm

from parrot import brnn_architecture
from parrot import encode_sequence

import os

from .metameta_hybrid_predict import predictor_string

# import settings for network
from .py_predictor_v2 import Predictor


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
                               


def batch_predict(sequences, gpuid=00) -> dict:
    """
    Batch prediction for metapredict. IN DEVELOPMENT. DO NOT USE

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



def batch_predict_v2(sequences, gpuid=00) -> dict:
    """
    Batch prediction for metapredict. IN DEVELOPMENT. DO NOT USE.

    NOTE that v2 breaks the sequence down so all batches ONLY
    take sequences of the same length.

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

    # load and setup the network (same code as used by the non-batch version)
    PATH = os.path.dirname(os.path.realpath(__file__))
    predictor_path = f'{PATH}/networks/{predictor_string}'
    brnn_predictor = Predictor(predictor_path, dtype="residues", gpuid=gpuid)

    device = brnn_predictor.device
    model  = brnn_predictor.network

    # hardcoded because this is where metapredict was trained
    batch_size = 32
   
    pred_dict = {}

    size_filtered =  size_filter(sequences)

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
    
    return pred_dict
