## Tests for the metapredict-predict-idrs command-line tool.
##
## Rather than comparing against hard-coded IDR strings (which go stale every
## time the default network changes), each test checks that the CLI writes
## exactly the IDRs that the Python API returns for the same settings. Both are
## run on the CPU so the comparison is deterministic.

import os

import protfasta
import pytest

import metapredict as meta

from . import run_cli, THREE_SEQS_FASTA, OUTPUT_DIR

OUTFILE_FASTA = os.path.join(OUTPUT_DIR, 'cli_idrs.fasta')
OUTFILE_TSV = os.path.join(OUTPUT_DIR, 'cli_idrs.tsv')


def expected_idr_records(**predict_kwargs):
    """
    Build the FASTA records metapredict-predict-idrs should write, using the
    Python API directly.

    Parameters
    ----------
    **predict_kwargs
        Extra keyword arguments passed to meta.predict_disorder (e.g. version
        or disorder_threshold).

    Returns
    -------
    dict
        Maps '<header> IDR_START=<start> IDR_END=<end>' to the IDR sequence.
    """
    sequences = protfasta.read_fasta(THREE_SEQS_FASTA)
    predictions = meta.predict_disorder(sequences, device='cpu', return_domains=True, **predict_kwargs)

    expected = {}
    for header, disorder_object in predictions.items():
        for boundary, idr_sequence in zip(disorder_object.disordered_domain_boundaries, disorder_object.disordered_domains):
            expected[f'{header} IDR_START={boundary[0]} IDR_END={boundary[1]}'] = idr_sequence

    # guard against a vacuous comparison if nothing were predicted
    assert len(expected) > 0
    return expected


def test_predict_idrs_default():
    result = run_cli('metapredict-predict-idrs', [THREE_SEQS_FASTA, '-o', OUTFILE_FASTA, '-d', 'cpu', '-s'], OUTFILE_FASTA)
    assert result.returncode == 0, result.stderr

    assert protfasta.read_fasta(OUTFILE_FASTA) == expected_idr_records()


def test_predict_idrs_threshold():
    # --threshold arrives from argparse; this checks it is parsed as a float and
    # actually changes the domain decomposition
    result = run_cli('metapredict-predict-idrs', [THREE_SEQS_FASTA, '-o', OUTFILE_FASTA, '-d', 'cpu', '-s', '--threshold', '0.9'], OUTFILE_FASTA)
    assert result.returncode == 0, result.stderr

    expected = expected_idr_records(disorder_threshold=0.9)
    assert protfasta.read_fasta(OUTFILE_FASTA) == expected
    assert expected != expected_idr_records()


def test_predict_idrs_version_1():
    result = run_cli('metapredict-predict-idrs', [THREE_SEQS_FASTA, '-o', OUTFILE_FASTA, '-d', 'cpu', '-s', '-v', '1'], OUTFILE_FASTA)
    assert result.returncode == 0, result.stderr

    assert protfasta.read_fasta(OUTFILE_FASTA) == expected_idr_records(version='V1')


@pytest.mark.parametrize('action', ['ignore', 'fail', 'remove', 'convert-ignore', 'convert-remove'])
def test_predict_idrs_invalid_sequence_actions(action):
    # three_seqs.fasta only has standard residues, so every action gives the default result
    result = run_cli('metapredict-predict-idrs', [THREE_SEQS_FASTA, '-o', OUTFILE_FASTA, '-d', 'cpu', '-s', '--invalid-sequence-action', action], OUTFILE_FASTA)
    assert result.returncode == 0, result.stderr

    assert protfasta.read_fasta(OUTFILE_FASTA) == expected_idr_records()


def test_predict_idrs_fake_invalid_sequence_action():
    result = run_cli('metapredict-predict-idrs', [THREE_SEQS_FASTA, '-o', OUTFILE_FASTA, '-d', 'cpu', '-s', '--invalid-sequence-action', 'FAKE-ACTION'], OUTFILE_FASTA)
    assert result.returncode != 0


def test_predict_idrs_shephard_domains():
    result = run_cli('metapredict-predict-idrs', [THREE_SEQS_FASTA, '-o', OUTFILE_TSV, '-d', 'cpu', '-s', '--mode', 'shephard-domains'], OUTFILE_TSV)
    assert result.returncode == 0, result.stderr

    # SHEPHARD domain files are 1-indexed and inclusive, so start = Python start + 1
    expected_lines = []
    for record in expected_idr_records():
        header, start_field, end_field = record.rsplit(' ', 2)
        start = int(start_field.split('=')[1]) + 1
        end = int(end_field.split('=')[1])
        expected_lines.append(f'{header}\t{start}\t{end}\tIDR')

    with open(OUTFILE_TSV) as fh:
        assert fh.read().splitlines() == expected_lines


def test_predict_idrs_shephard_uniprot_bad_header():
    # 'Q8N6T3' and 'p53' are not UniProt-style headers, so the tool should stop with an error
    result = run_cli('metapredict-predict-idrs', [THREE_SEQS_FASTA, '-o', OUTFILE_TSV, '-d', 'cpu', '-s', '--mode', 'shephard-domains-uniprot'], OUTFILE_TSV)
    assert result.returncode == 1
    assert 'Error parsing header line' in result.stdout


def test_predict_idrs_missing_input_file():
    missing_fasta = os.path.join(OUTPUT_DIR, 'does_not_exist.fasta')
    result = run_cli('metapredict-predict-idrs', [missing_fasta, '-o', OUTFILE_FASTA, '-s'], OUTFILE_FASTA)
    assert result.returncode == 1
    assert 'Could not find passed fasta file' in result.stdout
    assert not os.path.isfile(OUTFILE_FASTA)
