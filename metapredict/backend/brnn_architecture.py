#!/usr/bin/env python
"""
Code from Dan Griffith's IDP-Parrot tool from the Holehouse Lab.
All credit for this code should go to Dan.
See https://idptools-parrot.readthedocs.io/en/latest/api.html#module-parrot.encode_sequence
for more information.
"""

import torch 
import torch.nn as nn

class BRNN_MtM(nn.Module):
    """A PyTorch many-to-many bidirectional recurrent neural network

    A class containing the PyTorch implementation of a BRNN. The network consists
    of repeating LSTM units in the hidden layers that propogate sequence information
    in both the foward and reverse directions. A final fully connected layer
    aggregates the deepest hidden layers of both directions and produces the
    outputs.

    "Many-to-many" refers to the fact that the network will produce outputs 
    corresponding to every item of the input sequence. For example, an input 
    sequence of length 10 will produce 10 sequential outputs.

    Attributes
    ----------
    device : str
        String describing where the network is physically stored on the computer.
        Should be either 'cpu' or 'cuda' (GPU).
    hidden_size : int
        Size of hidden vectors in the network
    num_layers : int
        Number of hidden layers (for each direction) in the network
    num_classes : int
        Number of classes for the machine learning task. If it is a regression
        problem, `num_classes` should be 1. If it is a classification problem,
        it should be the number of classes.
    lstm : PyTorch LSTM object
        The bidirectional LSTM layer(s) of the recurrent neural network.
    fc : PyTorch Linear object  
        The fully connected linear layer of the recurrent neural network. Across 
        the length of the input sequence, this layer aggregates the output of the
        LSTM nodes from the deepest forward layer and deepest reverse layer and
        returns the output for that residue in the sequence.

    Methods
    -------
    forward(x)
        Propogate input sequences through the network to produce outputs
    """

    def __init__(self, input_size, hidden_size, num_layers, num_classes, device):
        """
        Parameters
        ----------
        input_size : int
            Length of the input vectors at each timestep
        hidden_size : int
            Size of hidden vectors in the network
        num_layers : int
            Number of hidden layers (for each direction) in the network
        num_classes : int
            Number of classes for the machine learning task. If it is a regression
            problem, `num_classes` should be 1. If it is a classification problem,
            it should be the number of classes.
        device : str
            String describing where the network is physically stored on the computer.
            Should be either 'cpu' or 'cuda' (GPU).
        """

        super(BRNN_MtM, self).__init__()
        self.device = device
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_classes = num_classes
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                            batch_first=True, bidirectional=True)
        self.fc = nn.Linear(in_features=hidden_size*2,  # *2 for bidirection
                            out_features=num_classes) 
    
    def forward(self, x):
        """Propogate input sequences through the network to produce outputs

        Parameters
        ----------
        x : 3-dimensional PyTorch IntTensor
            Input sequence to the network. Should be in the format:
            [batch_dim X sequence_length X input_size]

        Returns
        -------
        3-dimensional PyTorch FloatTensor
            Output after propogating the sequences through the network. Will
            be in the format:
            [batch_dim X sequence_length X num_classes]
        """

        # Set initial states
        # h0 and c0 dimensions: [num_layers*2 X batch_size X hidden_size]
        h0 = torch.zeros(self.num_layers*2,     # *2 for bidirection
                         x.size(0), self.hidden_size).to(self.device)
        c0 = torch.zeros(self.num_layers*2, 
                         x.size(0), self.hidden_size).to(self.device)
        
        # Forward propagate LSTM
        # out: tensor of shape: [batch_size, seq_length, hidden_size*2]
        out, (h_n, c_n) = self.lstm(x, (h0, c0))
        
        # Decode the hidden state for each time step
        fc_out = self.fc(out)    
        return fc_out
