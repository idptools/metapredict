## Tests for the metapredict-predict-disorder and metapredict-graph-disorder
## command-line tools.
##
## Scores written by the CLI are compared against the Python API run on the CPU
## with the same settings.

import os

import numpy as np
import protfasta
import torch

import metapredict as meta
from metapredict.backend.meta_tools import sanitize_filename

from . import run_cli, THREE_SEQS_FASTA, OUTPUT_DIR

OUTFILE_CSV = os.path.join(OUTPUT_DIR, 'cli_disorder.csv')
GRAPH_DIR = os.path.join(OUTPUT_DIR, 'cli_graphs')

# scores are written rounded to 4 decimal places
SCORE_TOLERANCE = 1e-4


def read_scores_csv(filename, sequences):
    """
    Read a CSV written by metapredict-predict-disorder.

    Parameters
    ----------
    filename : str
        Path to the CSV file.

    sequences : dict
        Maps header to sequence for the FASTA file that was predicted. The
        sequence length is used to pull the per-residue scores from the end of
        each row, so this works whether or not the row also includes the
        sequence itself.

    Returns
    -------
    dict
        Maps header to a numpy array of per-residue scores.
    """
    scores = {}
    with open(filename) as fh:
        for line in fh:
            fields = [field.strip() for field in line.rstrip('\n').split(',')]
            header = fields[0]
            n_residues = len(sequences[header])
            scores[header] = np.array(fields[-n_residues:], dtype=float)
    return scores


def test_predict_disorder_default():
    result = run_cli('metapredict-predict-disorder', [THREE_SEQS_FASTA, '-o', OUTFILE_CSV, '-d', 'cpu', '-s'], OUTFILE_CSV)
    assert result.returncode == 0, result.stderr + result.stdout

    sequences = protfasta.read_fasta(THREE_SEQS_FASTA)
    expected = meta.predict_disorder(sequences, device='cpu')
    written = read_scores_csv(OUTFILE_CSV, sequences)

    assert list(written) == list(expected)
    for header in expected:
        assert np.allclose(written[header], expected[header][1], atol=SCORE_TOLERANCE)


def test_predict_disorder_version_1():
    result = run_cli('metapredict-predict-disorder', [THREE_SEQS_FASTA, '-o', OUTFILE_CSV, '-d', 'cpu', '-s', '-v', '1'], OUTFILE_CSV)
    assert result.returncode == 0, result.stderr + result.stdout

    sequences = protfasta.read_fasta(THREE_SEQS_FASTA)
    expected = meta.predict_disorder(sequences, device='cpu', version='V1')
    written = read_scores_csv(OUTFILE_CSV, sequences)

    for header in expected:
        assert np.allclose(written[header], expected[header][1], atol=SCORE_TOLERANCE)


def test_predict_disorder_integer_device():
    # the help text says an int GPU index is accepted; argparse passes it as the
    # string '0', which must be treated as cuda:0 rather than hitting an internal error
    result = run_cli('metapredict-predict-disorder', [THREE_SEQS_FASTA, '-o', OUTFILE_CSV, '-d', '0', '-s'], OUTFILE_CSV)

    if torch.cuda.is_available():
        assert result.returncode == 0, result.stderr + result.stdout
    else:
        assert result.returncode == 1
        assert 'cuda:0 was specified as the device' in result.stdout
        assert "shouldn't be able to see this message" not in result.stdout


def test_predict_disorder_missing_input_file():
    missing_fasta = os.path.join(OUTPUT_DIR, 'does_not_exist.fasta')
    result = run_cli('metapredict-predict-disorder', [missing_fasta, '-o', OUTFILE_CSV, '-s'], OUTFILE_CSV)
    assert result.returncode == 1
    assert not os.path.isfile(OUTFILE_CSV)


def test_graph_disorder_threshold():
    # --disorder-threshold arrives from argparse and must be parsed as a float
    os.makedirs(GRAPH_DIR, exist_ok=True)

    # graph_disorder_fasta names each file after the first 14 characters of the sanitized header
    headers = protfasta.read_fasta(THREE_SEQS_FASTA).keys()
    expected_files = [os.path.join(GRAPH_DIR, sanitize_filename(header)[0:14] + '.png') for header in headers]
    for filename in expected_files:
        if os.path.isfile(filename):
            os.remove(filename)

    result = run_cli('metapredict-graph-disorder', [THREE_SEQS_FASTA, '-o', GRAPH_DIR, '--disorder-threshold', '0.4'])
    assert result.returncode == 0, result.stderr + result.stdout

    for filename in expected_files:
        assert os.path.isfile(filename)
