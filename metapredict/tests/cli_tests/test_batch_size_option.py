## Tests for the -b/--batch-size option of the command-line tools that predict
## a whole FASTA file (metapredict-predict-disorder, -predict-pLDDT,
## -predict-idrs and -caid).
##
## The wiring tests run each tool's main() in-process with the library call it
## makes replaced by a stand-in that records its keyword arguments, so they
## check the option reaches the prediction code without running a prediction.

import os
import sys

import numpy as np
import protfasta
import pytest

import metapredict
import metapredict as meta
from metapredict.metapredict_exceptions import MetapredictError
from metapredict.scripts import (metapredict_caid, metapredict_predict_disorder,
                                 metapredict_predict_idrs, metapredict_predict_pLDDT)

from . import run_cli, THREE_SEQS_FASTA, OUTPUT_DIR

# a valid, non-default batch size, and one that isn't a power of two
VALID_BATCH_SIZE = 64
INVALID_BATCH_SIZE = 33

# scores are written rounded to 4 decimal places
SCORE_TOLERANCE = 1e-4


class StopPrediction(Exception):
    """Raised by the stand-in library functions once they have recorded their arguments."""


def _tool_cases(tmp_path):
    """
    The four tools, each as (script module, library function it calls, extra
    command-line arguments it needs).
    """
    return [
        (metapredict_predict_disorder, 'predict_disorder_fasta', ['-o', str(tmp_path / 'out.csv'), '-s']),
        (metapredict_predict_pLDDT, 'predict_pLDDT_fasta', ['-o', str(tmp_path / 'out.csv'), '-s']),
        (metapredict_predict_idrs, 'predict_disorder', ['-o', str(tmp_path / 'out.fasta'), '-s']),
        (metapredict_caid, 'predict_disorder_caid', [str(tmp_path / 'caid_out'), 'v3']),
    ]


TOOL_IDS = ['predict-disorder', 'predict-pLDDT', 'predict-idrs', 'caid']


def _run_main_with_stand_in(monkeypatch, module, library_function, argv):
    """Run a tool's main() with its library call replaced; return the kwargs it was called with."""
    recorded = {}

    def stand_in(*args, **kwargs):
        recorded.update(kwargs)
        raise StopPrediction()

    monkeypatch.setattr(metapredict, library_function, stand_in)
    monkeypatch.setattr(sys, 'argv', argv)

    # each tool catches errors from the prediction and exits with status 1
    with pytest.raises(SystemExit):
        module.main()
    return recorded


@pytest.mark.parametrize('case_index', range(4), ids=TOOL_IDS)
@pytest.mark.parametrize('batch_option, expected', [(['-b', str(VALID_BATCH_SIZE)], VALID_BATCH_SIZE),
                                                    (['--batch-size', str(VALID_BATCH_SIZE)], VALID_BATCH_SIZE),
                                                    ([], None)],
                         ids=['-b', '--batch-size', 'not given'])
def test_batch_size_reaches_the_prediction(monkeypatch, tmp_path, case_index, batch_option, expected):
    module, library_function, extra_args = _tool_cases(tmp_path)[case_index]
    argv = ['tool', THREE_SEQS_FASTA] + extra_args + batch_option

    recorded = _run_main_with_stand_in(monkeypatch, module, library_function, argv)
    assert recorded['batch_size'] == expected


@pytest.mark.parametrize('case_index', range(4), ids=TOOL_IDS)
def test_invalid_batch_size_is_rejected(monkeypatch, tmp_path, capsys, case_index):
    module, library_function, extra_args = _tool_cases(tmp_path)[case_index]
    argv = ['tool', THREE_SEQS_FASTA] + extra_args + ['-b', str(INVALID_BATCH_SIZE)]

    recorded = _run_main_with_stand_in(monkeypatch, module, library_function, argv)

    # stopped by the check, before any prediction was attempted
    assert recorded == {}
    error = capsys.readouterr().err
    assert '--batch-size must be a power of two of at least 32' in error
    assert f'got {INVALID_BATCH_SIZE}' in error


@pytest.mark.parametrize('library_function, args', [
    (meta.predict_disorder_fasta, [THREE_SEQS_FASTA]),
    (meta.predict_pLDDT_fasta, [THREE_SEQS_FASTA]),
    (meta.predict_disorder_caid, [THREE_SEQS_FASTA, os.path.join(OUTPUT_DIR, 'caid_batch_size_test')]),
], ids=['predict_disorder_fasta', 'predict_pLDDT_fasta', 'predict_disorder_caid'])
def test_library_functions_forward_batch_size(library_function, args):
    """The library functions behind the tools pass batch_size on to the
    predictor, which rejects a batch size that isn't a power of two."""
    with pytest.raises(MetapredictError, match='batch_size'):
        library_function(*args, batch_size=INVALID_BATCH_SIZE)


def test_predict_disorder_cli_batch_size_end_to_end():
    """A real run with -b gives the same scores as the Python API with the same batch size."""
    outfile = os.path.join(OUTPUT_DIR, 'cli_batch_size.csv')
    result = run_cli('metapredict-predict-disorder',
                     [THREE_SEQS_FASTA, '-o', outfile, '-d', 'cpu', '-s', '-b', str(VALID_BATCH_SIZE)], outfile)
    assert result.returncode == 0, result.stderr + result.stdout

    sequences = protfasta.read_fasta(THREE_SEQS_FASTA)
    expected = meta.predict_disorder(sequences, device='cpu', batch_size=VALID_BATCH_SIZE)
    with open(outfile) as fh:
        for line, header in zip(fh, expected):
            fields = [field.strip() for field in line.rstrip('\n').split(',')]
            assert fields[0] == header
            written = np.array(fields[-len(sequences[header]):], dtype=float)
            assert np.allclose(written, expected[header][1], atol=SCORE_TOLERANCE)


# --------------------------------------------------------------------------- #
# Default batch sizes in the --help text
# --------------------------------------------------------------------------- #

def test_describe_default_batch_sizes_groups_networks_and_devices():
    """Networks with the same defaults are described together, and devices that
    share a batch size are joined with 'or'."""
    from metapredict.scripts import describe_default_batch_sizes

    networks = {
        'V1': {'parameters': {'device_batch_size': {'cpu': 256, 'cuda': 256, 'mps': 512}, 'batch_size': 512}},
        'V2': {'parameters': {'device_batch_size': {'cpu': 256, 'cuda': 256, 'mps': 512}, 'batch_size': 512}},
        'V3': {'parameters': {'device_batch_size': {'cpu': 32, 'cuda': 128, 'mps': 1024}, 'batch_size': 512}},
        'V4': {'parameters': {'device_batch_size': {'cpu': 64, 'cuda': 64, 'mps': 64}, 'batch_size': 512}},
    }
    assert describe_default_batch_sizes(networks) == (
        'V1 and V2 use 256 on CPU or CUDA and 512 on MPS (Apple Silicon); '
        'V3 uses 32 on CPU, 128 on CUDA and 1024 on MPS (Apple Silicon); '
        'V4 uses 64 on CPU, CUDA or MPS (Apple Silicon).')


HELP_CASES = [
    (metapredict_predict_disorder, 'disorder'),
    (metapredict_predict_idrs, 'disorder'),
    (metapredict_caid, 'disorder'),
    (metapredict_predict_pLDDT, 'pLDDT'),
]


@pytest.mark.parametrize('module, prediction_type', HELP_CASES, ids=['predict-disorder', 'predict-idrs', 'caid', 'predict-pLDDT'])
def test_help_lists_default_batch_sizes(monkeypatch, capsys, module, prediction_type):
    """Each tool's --help names every network's default batch size on every
    device, worked out exactly as the predictor works them out."""
    from metapredict.backend.network_parameters import metapredict_networks, pplddt_networks
    from metapredict.backend.predictor import resolve_batch_size
    from metapredict.scripts import describe_default_batch_sizes

    networks = metapredict_networks if prediction_type == 'disorder' else pplddt_networks

    monkeypatch.setattr(sys, 'argv', ['tool', '--help'])
    with pytest.raises(SystemExit) as exit_info:
        module.main()
    assert exit_info.value.code == 0

    # argparse wraps help text over several lines, so compare with whitespace collapsed
    help_text = ' '.join(capsys.readouterr().out.split())
    assert ' '.join(describe_default_batch_sizes(networks).split()) in help_text
    for version, network in networks.items():
        assert version in help_text
        for device in ('cpu', 'cuda', 'mps'):
            assert f"{resolve_batch_size(None, device, network['parameters'])} on" in help_text
