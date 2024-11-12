#!/usr/bin/env python
"""
previously called 'brnn_architecture.py'. This holds the architectures
used for metapredict. This includes the original achitecture used for
metapredict V1 (legacy), V2, and the new architecture based on pytorch-
lightning (V3). 

BRNN_MtM code originally written by Dan Griffith for PARROT.
See idptools-parrot. 
"""
import torch
import torch.nn as nn
import pytorch_lightning as L

'''
USED BY V1 and V2 disorder predictors!
USED BY V1 pLDDT predictor!
'''

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
        self.lstm = torch.nn.LSTM(input_size, hidden_size, num_layers,
                                  batch_first=True, bidirectional=True)
        self.fc = torch.nn.Linear(in_features=hidden_size*2,  # *2 for bidirection
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

        # Forward propagate LSTM
        # out: tensor of shape: [batch_size, seq_length, hidden_size*2]
        out, _ = self.lstm(x)

        # Decode the hidden state for each time step    
        fc_out = self.fc(out)

        # return decoded hidden state
        return fc_out

'''
USED BY V3 disorder predictor!
USED BY V2 pLDDT predictor!
'''

class BRNN_MtM_lightning(L.LightningModule):
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
    lstm_hidden_size : int
        Size of hidden vectors in the network
    num_lstm_layers : int
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
    """

    def __init__(self, input_size, lstm_hidden_size, num_lstm_layers, 
                        num_classes, problem_type,
                        datatype, **kwargs):
        """
        Parameters
        ----------
        input_size : int
            Length of the input vectors at each timestep
        lstm_hidden_size : int
            Size of hidden vectors in the network
        num_lstm_layers : int
            Number of hidden layers (for each direction) in the network
        num_classes : int
            Number of classes for the machine learning task. If it is a regression
            problem, `num_classes` should be 1. If it is a classification problem,
            it should be the number of classes.
        """
        super(BRNN_MtM_lightning, self).__init__()
        self.lstm_hidden_size = lstm_hidden_size
        self.num_lstm_layers = num_lstm_layers
        self.num_classes = num_classes
        self.datatype = datatype
        self.problem_type = problem_type
        
        self.num_linear_layers = kwargs.get("num_linear_layers", 1)
        self.optimizer_name = kwargs.get('optimizer_name', 'SGD')
        self.linear_hidden_size = kwargs.get('linear_hidden_size', None)
        self.learn_rate = kwargs.get('learn_rate', 1e-3)
        self.dropout = kwargs.get('dropout', None)

        # Core Model architecture!
        self.lstm = nn.LSTM(input_size, lstm_hidden_size, num_lstm_layers,
                                batch_first=True, bidirectional=True)
        
        # improve generalization, stability, and model capacity
        self.layer_norm = nn.LayerNorm(lstm_hidden_size*2)

        self.linear_layers = nn.ModuleList()
        # increase LSTM embedding to linear hidden size dimension * 2 because bidirection-LSTM
        for i in range(0,self.num_linear_layers):
            if i == 0 and i == self.num_linear_layers - 1:
                # if theres only one linear layer map to output (old parrot-style)
                self.linear_layers.append(nn.Linear(self.lstm_hidden_size*2, num_classes)) # *2 for bidirection LSTM
            elif i == 0:
                # if we're not going directly to output, add first layer to map to linear hidden size
                self.linear_layers.append(nn.Linear(self.lstm_hidden_size*2, self.linear_hidden_size)) 

                # add dropout on this initial layer if specified
                if self.dropout != 0.0 and self.dropout is not None:
                    self.linear_layers.append(nn.Dropout(self.dropout))
            elif i < self.num_linear_layers - 1:
                # if linear layer is even, add some dropout
                if i % 2 == 0 and self.dropout != 0.0:
                    self.linear_layers.append(nn.Linear(self.linear_hidden_size, self.linear_hidden_size))
                    self.linear_layers.append(nn.Dropout(self.dropout))
                    self.linear_layers.append(nn.ReLU())
                else:
                    # add second linear layer (index 1) to n-1. 
                    self.linear_layers.append(nn.Linear(self.linear_hidden_size, self.linear_hidden_size))
                    self.linear_layers.append(nn.ReLU())
            elif i == self.num_linear_layers - 1:
                # add final output layer
                self.linear_layers.append(nn.Linear(self.linear_hidden_size, num_classes))
            else:
                raise ValueError("Invalid number of linear layers. Must be greater than 0.")


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
        # Forward propagate LSTM
        # out: tensor of shape: [batch_size, seq_length, lstm_hidden_size*2]
        out, _ = self.lstm(x)
        out = self.layer_norm(out)
        for layer in self.linear_layers:
            out = layer(out)

        return out





