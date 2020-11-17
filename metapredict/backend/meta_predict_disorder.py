"""
Backend of the IDR machine learning predictor. Based partly
on code from Dan Griffith's IDP-Parrot from the Holehouse lab
(specifically the test_unlabeled_data function in train_network.py).
"""

#import packages for predictor
import sys
import os

import numpy as np
import torch 
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader


#import modules that predictor depends on
from metapredict.backend import encode_sequence
from metapredict.backend import brnn_architecture


#set path for location of predictor. Using this in case I want to update the predictor or 
#eventually make multiple predictors.
PATH = os.path.dirname(os.path.realpath(__file__))

#Setting predictor equal to location of weighted values.
predictor = "{}/meta_predict_disorder_100e.pt".format(PATH)

##################################################################################################
#hyperparameters used by when metapredict was trained. Manually setting them here for clarity.
##################################################################################################

device = 'cpu'
hidden_size = 5
num_layers = 1
dtype = 'residues'
num_classes = 1
encoding_scheme = 'onehot'
input_size = 20
problem_type = 'regression'

#set location of saved_weights for load_state_dict
saved_weights = predictor

###############################################################################
# Initialize network architecture using previously defined hyperparameters
###############################################################################
brnn_network = brnn_architecture.BRNN_MtM(input_size, hidden_size, num_layers, num_classes, device).to(device)
brnn_network.load_state_dict(torch.load(saved_weights, map_location=torch.device(device)))
###############################################################################


def meta_predict(sequence, normalized=True, network=brnn_network, device=device, encoding_scheme=encoding_scheme):
	"""
	The actual executing function for predicting the disorder of a sequence using metapredict.
	Returns a list containing predicted disorder values for the input sequence. 

	Arguments
	---------
	sequence - the amino acid sequence to be predicted

	normalized (optional) - by default, negative values are set to be equal to 0 and values greater
	than 1 are set to be equal to 1. User can set normalized=False to get raw prediction values.

	network - the network used by the predictor. See brnn_architecture BRNN_MtM for more info.

	device - String describing where the network is physically stored on the computer. 
	Should be either 'cpu' or 'cuda' (GPU).
	
	encoding_scheme - encoding scheme used when metapredict was trained. The encoding scheme was onehot.
	"""
	#set seq_vector equal to converted amino acid sequence that is a PyTorch tensor of one-hot vectors
	seq_vector = encode_sequence.one_hot(sequence)
	seq_vector=seq_vector.view(1, len(seq_vector), -1)

	#get output values from the seq_vector based on the network (brnn_network)
	outputs = network(seq_vector.float()).detach().numpy()[0]
	
	#make empty list to add in outputs
	output_values = []
	#for the values 'i' in outputs
	for i in outputs:
		#append each value (which is the predicted disorder value) to output values as a float.
		#round each value to six digits.
		output_values.append(round(float(i),3))

	#if normalized=True (defualt)
	if normalized == True:
		#initialize empty list to populate normalized values
		normalized_IDR_values = []
		#determine the lowest value in the output_values list
		min_IDR = min(output_values)
		#if the lowset value is less than 0, normalize the list by replacing negative values with 0.
		if min_IDR < 0:
			for j in range(0, len(output_values)):
				cur_value = output_values[j]
				if cur_value < 0:	
					normalized_IDR_values.append(0)
				else:
					normalized_IDR_values.append(round(cur_value, 3))
			#overwrite output_values with normalized_IDR_values (which are now all non-negative).
			output_values = normalized_IDR_values
		#overwrite normalized_IDR_values with an empty list
		normalized_IDR_values = []
		#determine the greatest value in the ouputValues list
		max_IDR = max(output_values)
		#if the greatest value is greater than 1, replace values greater than 1 with 1.
		if max_IDR > 1:
			for k in range (0, len(output_values)):
				cur_value = output_values[k]
				if cur_value > 1:
					normalized_IDR_values.append(1)
				else:
					normalized_IDR_values.append(round(cur_value, 3))
			#overwrite output_values with normalized_IDR_values (which are now all less than or equal to 1).
			output_values = normalized_IDR_values
		#return output_values
		return output_values
	#if normalized=False, just return the output_values.
	else:
		return output_values

