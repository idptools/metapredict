import numpy as np

class DisorderObject:
    """
    Simple datastructure that is returned from predict_disorder_domains_hybrid()
    and provides dot-notation access to key variables.
    """

    def __init__(self, seq, meta, ppLDDT, hybrid, hybrid_smoothed, disordered_domains, folded_domains, return_numpy=False):
        """
        Constructor
        """
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

