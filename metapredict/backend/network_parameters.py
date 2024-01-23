#!/usr/bin/env python
"""
Dictionary that just holds the hyper parameters
for each network. This is used to load them
so we don't have to do that dynamically. Also can
include other useful information about the network here
if available. 
"""

#V1
meta_predict_disorder_100e_v1 = {
    'input_size': 20,
    'hidden_size': 5,
    'num_layers': 1, 
    'num_classes': 1, 
    'problem_type': 'regression', 
    'datatype': 'residues', 
    'learn_rate': 0.001, 
    'batch_size': 32,
    'epochs': 100,
    'used_lightning': False,
    'disorder_threshold':0.42
}

#V2
metameta_2_7_22_nl2_hs20_b32_V3 = {
    'input_size': 20,
    'hidden_size': 10,
    'num_layers': 2, 
    'num_classes': 1, 
    'problem_type': 'regression', 
    'datatype': 'residues', 
    'learn_rate': 0.001, 
    'batch_size': 32,
    'epochs': 100,
    'used_lightning': False,
    'disorder_threshold':0.5
}

# a network Jeff gave me then didn't like
epoch023_val_loss1529_48_ckpt={
    'pytorch-lightning_version': '2.0.4', 
    'input_size': 20,
    'hidden_size': 36,
    'num_layers': 2, 
    'num_classes': 1, 
    'problem_type': 'regression', 
    'datatype': 'residues', 
    'optimizer_name': 'SGD', 
    'learn_rate': 0.009888257928864106, 
    'momentum': 0.9973749278428164, 
    'batch_size': 256,
    'used_lightning': True,
    'disorder_threshold':0.5
}

# V3
epoch_49_step_42600_ckpt={
    'pytorch-lightning_version': '2.0.4', 
    'input_size': 20, 
    'lstm_hidden_size': 45, 
    'num_lstm_layers': 2, 
    'num_classes': 1, 
    'problem_type': 'regression', 
    'datatype': 'residues', 
    'optimizer_name': 'SGD', 
    'learn_rate': 0.009927612390810909, 
    'num_linear_layers': 4, 
    'linear_hidden_size': 376, 
    'use_dropout': False, 
    'dropout': 0.0,
    'momentum': 0.9924023043863971,
    'batch_size': 256,
    'used_lightning': True,
    'last_epoch': 62,
    'disorder_threshold': 0.5
}

# dict to hold the networks.
metapredict_networks = {
    'V1':{'weights':'meta_predict_disorder_100e_v1.pt',
          'parameters': meta_predict_disorder_100e_v1},
    'V2':{'weights':'metameta_2_7_22_nl2_hs20_b32_V3.pt',
          'parameters': metameta_2_7_22_nl2_hs20_b32_V3},
    'V3':{'weights':'epoch-49-step-42600.ckpt',
          'parameters': epoch_49_step_42600_ckpt},
}




