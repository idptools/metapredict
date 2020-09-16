"""
metapredict
A protein disorder predictor based on a BRNN (IDP-Parrot) trained on the consensus disorder values from 8 disorder predictors from 12 proteomes.
"""

# Add imports here
from .meta import *
from .backend.brnn_architecture import *
from .backend.encode_sequence import *
from .backend.meta_graph import *
from .backend.meta_predict_disorder import *





# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
