import numpy as np

class DisorderObject:
    """
    Simple datastructure that is returned from predict_disorder_domains
    and provides dot-notation access to key variables.
    """
    
    # OPTIMIZATION: Use __slots__ to reduce memory footprint and slightly improve attribute access speed
    __slots__ = ('sequence', 'disorder', 'disordered_domain_boundaries', 
                 'folded_domain_boundaries', '_disordered_domains_cache', 
                 '_folded_domains_cache')

    def __init__(self, seq, meta, disordered_domains, folded_domains, return_numpy=False):
        """
        Constructor
        """
        self.sequence = seq

        self.disordered_domain_boundaries = disordered_domains

        self.folded_domain_boundaries = folded_domains

        # OPTIMIZATION: Streamlined type conversion - avoid redundant isinstance checks
        # convert numerical vector types as per input argument
        if return_numpy:
            self.disorder = np.asarray(meta) if not isinstance(meta, np.ndarray) else meta
        else:
            self.disorder = meta.tolist() if isinstance(meta, np.ndarray) else meta

        # Cache for domain sequences to avoid recomputation
        self._disordered_domains_cache = None
        self._folded_domains_cache = None

    @property
    def disordered_domains(self):
        if self._disordered_domains_cache is None:
            self._disordered_domains_cache = self.__get_domains(self.disordered_domain_boundaries)
        return self._disordered_domains_cache

    @property
    def folded_domains(self):
        if self._folded_domains_cache is None:
            self._folded_domains_cache = self.__get_domains(self.folded_domain_boundaries)
        return self._folded_domains_cache

    def __get_domains(self, b):
        return [self.sequence[local[0]:local[1]] for local in b]

    def __str__(self):
        rs =  f"DisorderObject for sequence with {len(self.sequence)} residues, {len(self.disordered_domain_boundaries)} IDRs, and {len(self.folded_domain_boundaries)} folded domains\n"
        rs = rs + f"Available dot variables are:\n  .sequence\n  .disorder\n  .disordered_domain_boundaries\n  .folded_domain_boundaries\n  .disordered_domains\n  .folded_domains\n"

        return rs
        

    def __repr__(self):
        return str(self)

