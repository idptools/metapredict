import numpy as np



'''
The DisorderObjectHybrid class was originally used for a hybrid version of metapredict
where ppLDDT scores and the original metapredict network were combined to generate
predicted disorder scores. This is no longer user facing, so it was renamed from 
DisorderObject to DisorderObjectHybrid such that DisorderObject could be used in 
the predict_disorder_domains() function. The code is kept in case for some reason anyone
wants to go back and use the hybrid predictor.
'''


## commented out because I don't think we use this any more?
"""
class DisorderObjectHybrid:
    "
    Simple datastructure that is returned from predict_disorder_domains_hybrid()
    and provides dot-notation access to key variables.
    "

    def __init__(self, seq, meta, ppLDDT, hybrid, hybrid_smoothed, disordered_domains, folded_domains, return_numpy=False):
        "
        Constructor
        "
        self.sequence = seq
        self.disorder = hybrid
        self.disorder_smoothed = hybrid_smoothed

        self.ppLDDT = ppLDDT
        self.metapredict_disorder = meta 

        self.disordered_domain_boundaries = disordered_domains
        self.folded_domain_boundaries = folded_domains

        # convert numerical vector types as per input argument
        if return_numpy:
            if type(meta) is not np.ndarray:
                self.metapredict_disorder = np.array(meta)

            if type(hybrid) is not np.ndarray:
                self.disorder = np.array(hybrid)

            if type(hybrid_smoothed) is not np.ndarray:
                self.disorder_smoothed = np.array(hybrid_smoothed)

            if type(meta) is not np.ndarray:
                self.meta = np.array(meta)
        else:

            if type(meta) is np.ndarray:
                self.metapredict_disorder = meta.tolist()

            if type(hybrid) is np.ndarray:
                self.disorder = hybrid.tolist()

            if type(hybrid_smoothed) is  np.ndarray:
                self.disorder_smoothed = hybrid_smoothed.tolist()

            if type(meta) is np.ndarray:
                self.meta = meta.tolist()
            

    @property
    def disordered_domains(self):
        return self.__get_domains(self.disordered_domain_boundaries)


    @property
    def folded_domains(self):
        return self.__get_domains(self.folded_domain_boundaries)
            
    def __get_domains(self, b):
        doms = []
        for local in b:
            doms.append(self.sequence[local[0]:local[1]])
        return doms

"""


class DisorderObject:
    """
    Simple datastructure that is returned from predict_disorder_domains
    and provides dot-notation access to key variables.
    """

    def __init__(self, seq, meta, disordered_domains, folded_domains, return_numpy=False):
        """
        Constructor
        """
        self.sequence = seq

        self.disorder = meta 

        self.disordered_domain_boundaries = disordered_domains

        self.folded_domain_boundaries = folded_domains

        # convert numerical vector types as per input argument
        if return_numpy:
            if type(meta) is not np.ndarray:
                self.disorder = np.array(meta)

            if type(meta) is not np.ndarray:
                self.meta = np.array(meta)
        
        else:

            if type(meta) is np.ndarray:
                self.disorder = meta.tolist()

            if type(meta) is np.ndarray:
                self.meta = meta.tolist()
            

    @property
    def disordered_domains(self):
        return self.__get_domains(self.disordered_domain_boundaries)


    @property
    def folded_domains(self):
        return self.__get_domains(self.folded_domain_boundaries)
            
    def __get_domains(self, b):
        doms = []
        for local in b:
            doms.append(self.sequence[local[0]:local[1]])
        return doms

    def __str__(self):
        rs =  f"DisorderObject for sequence with {len(self.sequence)} residues, {len(self.disordered_domains)} IDRs, and {len(self.folded_domains)} folded domains\n"
        rs = rs + "Available dot variables are:\n  .sequence\n  .disorder\n  .disordered_domain_boundaries\n  .folded_domain_boundaries\n  .disordered_domains\n  .folded_domains\n"

        return rs
        

    def __repr__(self):
        return str(self)

