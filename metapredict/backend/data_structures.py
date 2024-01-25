import numpy as np

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
            if not isinstance(meta, np.ndarray):
                self.disorder = np.array(meta)

            if not isinstance(meta, np.ndarray):
                self.meta = np.array(meta)
        
        else:

            if isinstance(meta, np.ndarray):
                self.disorder = meta.tolist()

            if isinstance(meta, np.ndarray):
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
        rs = rs + f"Available dot variables are:\n  .sequence\n  .disorder\n  .disordered_domain_boundaries\n  .folded_domain_boundaries\n  .disordered_domains\n  .folded_domains\n"

        return rs
        

    def __repr__(self):
        return str(self)

