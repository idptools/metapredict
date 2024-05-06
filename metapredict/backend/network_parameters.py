#!/usr/bin/env python
"""
This holds all of the information on the networks we have in /backend/networks for disorder
and /backend/ppLDDT/networks for pLDDT.
This includes networks that we have published and those that we tested but didn't end up using. 
Explainations for networks can be found by calling the 'info' key in the dictionary for the 
network. 
Why make this? Great question. The reason is that a lot of the names for the
networks in the /networks folder are downright terrible (metaDisorder.pt is... bad). However,
I don't want to change the names of those networks at this point because it would make them
hard to track down. This is my Not So Clever Workaround™.  

The other reason for this module is to hold the hyperparameters for networks we made before we
started using Pytorch-lightning. The importance of this is Pytorch-lightning holds more easily 
accessible hyperparameter information that you don't need to dynamically load. However, we can't 
use this functionalty for the old networks, so the workaround is to just have
things hardcoded here. This will also future proof us in case the Pytorch-lightning functionality
changes for whatever reason. It's also a nice place to look things up to see what parameters
we used for each network.
"""

# import the cutoff value parameters for each network from parameters.
from metapredict.parameters import METAPREDICT_LEGACY_THRESHOLD, METAPREDICT_V2_THRESHOLD, METAPREDICT_V3_THRESHOLD

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
#=-=-=-=-=-= DISORDER NETWORKS =-=-=-=-=-=#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#

#V1 AKA metapredict legacy
meta_predict_disorder_100e_v1 = {
    'public_name': 'V1',
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
    'disorder_threshold':METAPREDICT_LEGACY_THRESHOLD,
    'info': "This network is the original metapredict network as published in 'Metapredict: a fast, accurate, and easy-to-use predictor of consensus disorder and structure', Biophysical Journal 120, 4312–4319, October 19, 2021",
    'type': 'disorder'
}

#V2
metameta_2_7_22_nl2_hs20_b32_V3 = {
    'public_name': 'V2',
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
    'disorder_threshold':METAPREDICT_V2_THRESHOLD,
    'info': "This network is the network known as metapredict V2 or V2-FF. From 'Metapredict V2: An update to metapredict, a fast, accurate, and easy-to-use predictor of consensus disorder and structure' - Biorixv, doi: https://doi.org/10.1101/2022.06.06.494887"    ,
    'type': 'disorder'
}

# V3 network
smoothed_v3 = {
    'network_name': 'epoch099_val_loss1107.08.ckpt',
    'public_name': 'V3',
    'pytorch-lightning_version': '2.1.3',
    'input_size': 20,
    'lstm_hidden_size': 52,
    'num_lstm_layers': 2,
    'num_classes': 1,
    'problem_type': 'regression',
    'datatype': 'residues',
    'optimizer_name': 'SGD',
    'learn_rate': 0.014268372321431562,
    'num_linear_layers': 1,
    'gradient_clip_val':   1,
    'use_dropout': False,
    'batch_size': 256,
    'used_lightning': True,
    'momentum':    0.9968434498981696,
    'last_epoch': 100,
    'disorder_threshold': METAPREDICT_V3_THRESHOLD,
    'info': 'Similar to v2 metapredict as far as training data except we used real pLDDT scores based on AF2 V4 structures instead of predicted pLDDT. In addition, values were smoothed over a 25 residue sliding window before being used for training. Depending on some additional testing, this is likely to be our next released network.',
    'type': 'disorder'
}

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
#=-=-=-=-=-= pLDDT NETWORKS -=-=-=-=-=#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#

# predicted PLDDT network (v1)
alpha_fold_networkV7_hs100_nL2_200e_all_prot={
    'public_name': 'ppLDDT_V1',
    'input_size': 20, 
    'hidden_size': 100, 
    'num_layers': 2, 
    'num_classes': 1, 
    'problem_type': 'regression', 
    'datatype': 'residues', 
    'learn_rate': 0.001, 
    'batch_size': 32,
    'epochs': 200,
    'used_lightning': False,
    'disorder_threshold': 'N/A',
    'info': "pLDDT predictor network implemented in AlphaPredict. Original pLDDT predictor. Trained on same proteomes as metapredict V1 (legacy) pLDDT scores. Output scores from this predictor combined with metapredict legacy disorder scores were used to make the metapredict V2 network.", 
    'type': 'pLDDT'
}

# predicted PLDDT network (v2)
epoch019_val_loss1477_45_ckpt={
    'public_name': 'ppLDDT_V2',
    'pytorch-lightning_version': '2.0.4', 
    'input_size': 20, 
    'lstm_hidden_size': 29, 
    'num_lstm_layers': 1, 
    'num_classes': 1, 
    'problem_type': 'regression', 
    'datatype': 'residues', 
    'optimizer_name': 'SGD', 
    'learn_rate': 0.1, 
    'num_linear_layers': 1, 
    'use_dropout': False, 
    'momentum': 0.9950558532837848,
    'batch_size': 256,
    'used_lightning': True,
    'last_epoch': 20,
    'disorder_threshold': 'N/A',
    'info': "Network made by Jeff. Trained on pLDDT scores from swissprot AF2 V4 PDBs. March 2024.", 
    'type': 'pLDDT'
}

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
#=-=-=-=-=-= ADD USER-FACING STUFF HERE -=-=-=-=-=#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
'''
Everything user-facing needs to be added here. For a version,
add 'V#' as a new key to the dictionary. That should then have 
a value that is an additional key with two values: 
'weights': the name of the file that holds the weights for the network
'parameters': the dictionary that holds the hyperparameters for the network. 
the dictionary specified in 'parameters' needs to be defined with the same
key : value pairs as the dictionaries above.
'''


# dict to hold the networks that are user-facing.
metapredict_networks = {
    'V1':{'weights':'meta_predict_disorder_100e_v1.pt',
          'parameters': meta_predict_disorder_100e_v1},
    'V2':{'weights':'metameta_2_7_22_nl2_hs20_b32_V3.pt',
          'parameters': metameta_2_7_22_nl2_hs20_b32_V3},
    'V3':{'weights':'epoch099_val_loss1107.08.ckpt',
          'parameters': smoothed_v3}
}

# dict to hold pLDDT score prediction networks that are user-facing
pplddt_networks = {
    'V1': {'weights':'alpha_fold_networkV7_hs100_nL2_200e_all_prot.pt',
        'parameters':alpha_fold_networkV7_hs100_nL2_200e_all_prot},
    'V2': {'weights':'epoch019_val_loss1477.45.ckpt',
        'parameters':epoch019_val_loss1477_45_ckpt}
}


# ....................................................................................
# ................................. UNUSED NETWORKS! .................................
# ....................................................................................

''' 
A bunch of networks that ... we aren't currently using. Not throwing them away, kind
of like a strain in a -80°C that will never again see the light of day.
'''


# Unpublished V1 network. Probably the least accurate network I ever made but was used for 
# some of the originaly early days development of the metapredict python package.
metaDisorder = {
    'public_name': 'N/A',
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
    'disorder_threshold':0.5,
    'type': 'disorder'
}


# Unpublished V2. Worse than V2 and slower so was not used. Only 1 hidden layer likely wasn't enough. 
metapredict_network_v2_200epochs_nl1_hs20 = {
    'public_name': 'N/A',
    'input_size': 20,
    'hidden_size': 20,
    'num_layers': 1, 
    'num_classes': 1, 
    'problem_type': 'regression', 
    'datatype': 'residues', 
    'learn_rate': 0.001, 
    'batch_size': 32,
    'epochs': 200,
    'used_lightning': False,
    'disorder_threshold':0.5,
    'info': "Trained on same dataset as V2 but was not as good.",
    'type': 'disorder'    
}


# Unpublished V2. Slower than V2 but not significantly better. 
metapredict_network_v3_200epochs_nl2_hs20 = {
    'public_name': 'N/A',
    'input_size': 20,
    'hidden_size': 20,
    'num_layers': 2, 
    'num_classes': 1, 
    'problem_type': 'regression', 
    'datatype': 'residues', 
    'learn_rate': 0.001, 
    'batch_size': 32,
    'epochs': 200,
    'used_lightning': False,
    'disorder_threshold':0.5,
    'info': "Trained on same dataset as V2. Had a HS of 20 instead of 10. Wasn't significantly better than V2 and was slower, so wasn't used for final V2 network.",
    'type': 'disorder'
}

# a network Jeff gave me then didn't like. Used to develop Lightning functionality in metapredict. 
epoch023_val_loss1529_48_ckpt={
    'public_name': 'N/A',
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
    'disorder_threshold':0.5,
    'info': "Network given to me by Jeff to start testing out Lightning implementations into metapredict.",
    'type': 'disorder'
}

# V2 training data used but with a Pytorch-lightning implementation .
epoch_49_step_42600_ckpt={
    'public_name': 'V2_lightning',
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
    'disorder_threshold': METAPREDICT_V3_THRESHOLD,
    'info': "Network given to me by Jeff to start testing out Lightning implementations into metapredict. Trained on dataset similar to V2.",
    'type': 'disorder'
}

# given to me by Jeff on Apr 15, was based on a 1-pLDDT score smoothed values
alphadisorder_movingavg = {
    'network_name': 'epoch029_val_loss791.84.ckpt',
    'public_name': 'alpha',
    'pytorch-lightning_version': '2.1.3',
    'input_size': 20,
    'lstm_hidden_size': 66,
    'num_lstm_layers': 2,
    'num_classes': 1,
    'problem_type': 'regression',
    'datatype': 'residues',
    'optimizer_name': 'AdamW',
    'learn_rate': 0.03497941828975909,
    'num_linear_layers': 2,
    'use_dropout': False,
    'batch_size': 256,
    'used_lightning': True,
    'last_epoch': 97,
    'disorder_threshold': 0.58,
    'info': 'A disorder protocol moving avg 1-plddt',
    'type': 'disorder'
}


# Same as above (alphadisorder_movingavg) but 1 Layer version. April 11 2024
pLDDT_disorder_1_layer = {
    'network_name': 'epoch029_val_loss959.58.ckpt',
    'public_name': 'plddt_disorder_1_layer',
    'pytorch-lightning_version': '2.0.4', 
    'input_size': 20, 
    'lstm_hidden_size': 61, 
    'num_lstm_layers': 1, 
    'num_classes': 1, 
    'problem_type': 'regression', 
    'datatype': 'residues', 
    'optimizer_name': 'SGD', 
    'learn_rate': 0.028282345952988428, 
    'num_linear_layers': 1, 
    'use_dropout': False, 
    'momentum': 0.9978645519597096,
    'batch_size': 256,
    'used_lightning': True,
    'last_epoch': 30,
    'disorder_threshold': 0.58,
    'info': "pLDDT-based disorder predictor Jeff made. 1 Layer version.", 
    'type': 'disorder'
}


# V3 scores not smoothed but using an AdamW optimizer instead of SGD
admaw = {
    'network_name': 'epoch096_val_loss1584.14.ckpt',
    'public_name': 'apr15_adamW',
    'pytorch-lightning_version': '2.1.3',
    'input_size': 20,
    'lstm_hidden_size': 66,
    'num_lstm_layers': 2,
    'num_classes': 1,
    'problem_type': 'regression',
    'datatype': 'residues',
    'optimizer_name': 'AdamW',
    'learn_rate': 0.03497941828975909,
    'num_linear_layers': 2,
    'linear_hidden_size':  144,
    'use_dropout': False,
    'batch_size': 256,
    'beta1':   0.9096370466379254,
    'beta2':   0.9890895717487497,
    'eps': 0.011417699888815918,
    'weight_decay':    0.002036277656062938,
    'used_lightning': True,
    'last_epoch': 97,
    'disorder_threshold': 0.5,
    'info': 'V3 scores using AdamW optimizer',
    'type': 'disorder'
}

# my curiousity to see if my network using old-school PARROT and my tried and true hyperparameters
# could beat Jeff's fancy approach using Pytorch-LIGHTNING. It could not. 
smoothed_v3_re={
    'network_name' : 'smoothed_v3_real_plddt_re.pt',
    'public_name': 'v3_re_beta',
    'input_size': 20, 
    'hidden_size': 40, 
    'num_layers': 2, 
    'num_classes': 1, 
    'problem_type': 'regression', 
    'datatype': 'residues', 
    'learn_rate': 0.001, 
    'batch_size': 256,
    'used_lightning': False,
    'disorder_threshold': 0.5,
    'info': "Real pLDDT scores and OG metapredict, smoothed over after with a window of 25.",
    'type': 'disorder'
}


# Network I made that used PAE matrices that were pre-processed to pull out disorder information. 
# ended up not being the most accuurate network. 
pae={
    'network_name' : 'non_bin_PAE_hs30_nl2.pt',
    'public_name': 'v3_beta',
    'input_size': 20, 
    'hidden_size': 40, 
    'num_layers': 2, 
    'num_classes': 1, 
    'problem_type': 'regression', 
    'datatype': 'residues', 
    'learn_rate': 0.0009, 
    'batch_size': 128,
    'used_lightning': False,
    'disorder_threshold': 0.5,
    'info': "Network that used PAE scores to predict disorder. Not optimized. Ended up not being much more accurate than v2.",
    'type': 'disorder'
}

# possibly overfit ... decided against using. 
smoothed_v3_2={
    'network_name': 'epoch096_val_loss1584.14.ckpt',
    'public_name': 'V3_2',
    'pytorch-lightning_version': '2.1.3',
    'input_size': 20,
    'lstm_hidden_size': 52,
    'num_lstm_layers': 2,
    'num_classes': 1,
    'problem_type': 'regression',
    'datatype': 'residues',
    'optimizer_name': 'SGD',
    'learn_rate': 0.014268372321431562,
    'num_linear_layers': 1,
    'gradient_clip_val':   1,
    'use_dropout': False,
    'momentum': 0.9968434498981696,
    'last_epoch': 180,
    'batch_size': 256,
    'used_lightning': True,
    'disorder_threshold': 0.5,
    'info': 'like V3 but trained longer',
    'type': 'disorder'
}