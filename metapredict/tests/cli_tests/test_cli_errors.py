## Regression tests for how the command-line tools handle bad input.
##
## Each case here used to end in a Python traceback, or silently wrote empty
## output. Every one should now stop with a clear error message on stderr, exit
## with status 1, and write no output. Outputs go to pytest's tmp_path, which is
## fresh for each test, so 'nothing was written' can be checked reliably.

import socket

import pytest
import torch

from metapredict.scripts import fasta_has_records

from . import run_cli, THREE_SEQS_FASTA

# every tool that reads a FASTA file
FASTA_TOOLS = ['metapredict-predict-disorder',
               'metapredict-predict-idrs',
               'metapredict-predict-pLDDT',
               'metapredict-graph-disorder',
               'metapredict-graph-pLDDT',
               'metapredict-caid']

# the FASTA tools with an --invalid-sequence-action option (metapredict-caid always uses 'convert')
INVALID_SEQUENCE_ACTION_TOOLS = [tool for tool in FASTA_TOOLS if tool != 'metapredict-caid']

# the graphing tools write into an output directory that must already exist
GRAPH_TOOLS = ['metapredict-graph-disorder', 'metapredict-graph-pLDDT']

# the tools that predict on a device chosen with -d
DEVICE_TOOLS = ['metapredict-predict-idrs', 'metapredict-predict-pLDDT']

# contents of FASTA files that contain no records
NO_RECORD_FILE_CONTENTS = {'empty': '',
                           'no_headers': 'this is not a fasta file\nMKKKPPPSSS\n'}

# a FASTA file where every sequence contains 'J', which is not a standard amino
# acid and can't be converted to one, so 'remove' and 'convert-remove' remove them all
ALL_INVALID_FASTA_CONTENTS = '>a\nMKJKK\n>b\nPEPJIDE\n'

# a FASTA file whose first sequence is fine but whose second contains 'J', so a
# tool only finds the problem after it could have written output for the first
LATER_INVALID_FASTA_CONTENTS = '>a\nMKKKPPPSSSDDDEEE\n>b\nPEPJIDE\n'

# a FASTA file where the second header has no '|' to take a UniProt ID from
MIXED_UNIPROT_HEADERS_FASTA_CONTENTS = '>sp|P04637|P53_HUMAN\nMKKKPPPSSSDDDEEE\n>not_uniprot\nMKKKPPPSSSDDDEEE\n'

# UniProt lookups that reliably fail: an accession in an invalid format, and a
# name that matches nothing
INVALID_UNIPROT_ACCESSION = 'NOT_AN_ACCESSION'
UNMATCHED_PROTEIN_NAME = 'zzqxjvkwplmzzqx'

# human glutathione peroxidase 1 is a selenoprotein, so its UniProt sequence
# contains 'U', which metapredict can't predict; searching for the accession as
# a name also finds this entry
SELENOPROTEIN_ACCESSION = 'P07203'

# where the UniProt REST API is, and how long to wait when checking we can reach it
UNIPROT_HOST = 'rest.uniprot.org'
HTTPS_PORT = 443
UNIPROT_CONNECT_TIMEOUT_S = 5

# thresholds that are outside [0, 1] (nan is included because it slips past a plain < / > check)
OUT_OF_RANGE_THRESHOLDS = ['1.5', '-0.1', 'nan']

# an amino acid sequence for the tools that take one directly
TEST_SEQUENCE = 'MKKKPPPSSSDDDEEE'

# network versions that don't exist: there are three disorder networks but only two pLDDT networks
INVALID_DISORDER_VERSION = '4'
INVALID_PLDDT_VERSION = '3'

# (tool, version flag, invalid value, option name used in the error message) for every version flag
INVALID_VERSION_CASES = [('metapredict-predict-disorder', '-v', INVALID_DISORDER_VERSION, '--version'),
                         ('metapredict-predict-idrs', '-v', INVALID_DISORDER_VERSION, '--version'),
                         ('metapredict-predict-pLDDT', '-v', INVALID_PLDDT_VERSION, '--pLDDT-version'),
                         ('metapredict-graph-disorder', '-v', INVALID_DISORDER_VERSION, '--version'),
                         ('metapredict-graph-disorder', '-pv', INVALID_PLDDT_VERSION, '--pLDDT_version'),
                         ('metapredict-graph-pLDDT', '-v', INVALID_PLDDT_VERSION, '--pLDDT-version'),
                         ('metapredict-quick-predict', '-v', INVALID_DISORDER_VERSION, '--version'),
                         ('metapredict-quick-graph', '-v', INVALID_DISORDER_VERSION, '--version'),
                         ('metapredict-quick-graph', '-pv', INVALID_PLDDT_VERSION, '--pLDDT_version'),
                         ('metapredict-uniprot', '-v', INVALID_DISORDER_VERSION, '--version'),
                         ('metapredict-uniprot', '-pv', INVALID_PLDDT_VERSION, '--pLDDT_version'),
                         ('metapredict-name', '-v', INVALID_DISORDER_VERSION, '--version'),
                         ('metapredict-name', '-pv', INVALID_PLDDT_VERSION, '--pLDDT_version')]


def uniprot_is_reachable():
    """
    Check whether the UniProt REST API can be reached from this machine.

    Returns
    -------
    bool
        True if a connection to UniProt could be opened within
        UNIPROT_CONNECT_TIMEOUT_S seconds, False otherwise.
    """
    try:
        with socket.create_connection((UNIPROT_HOST, HTTPS_PORT), timeout=UNIPROT_CONNECT_TIMEOUT_S):
            return True
    except OSError:
        return False


# tests that look sequences up on UniProt are skipped when it can't be reached,
# so the suite doesn't fail (or wait on network timeouts) when run offline
requires_uniprot = pytest.mark.skipif(not uniprot_is_reachable(), reason=f'UniProt ({UNIPROT_HOST}) is not reachable')


def write_text_file(path, contents):
    """
    Write a text file for a test to use as input.

    Parameters
    ----------
    path : pathlib.Path
        Where to write the file.

    contents : str
        The text to write.

    Returns
    -------
    str
        The path of the written file, as a string for passing to run_cli.
    """
    with open(path, 'w') as fh:
        fh.write(contents)
    return str(path)


def fasta_tool_arguments(tool, fasta_file, output_path):
    """
    Build the command-line arguments that run a FASTA-reading tool.

    Parameters
    ----------
    tool : str
        Name of the command-line tool (one of FASTA_TOOLS).

    fasta_file : str
        Path to the input FASTA file.

    output_path : str
        Where the tool should write its output: a file for the predict tools,
        a directory for the graphing tools and metapredict-caid.

    Returns
    -------
    list of str
        Arguments to pass to run_cli.
    """
    # metapredict-caid takes the output directory and network version as positional arguments
    if tool == 'metapredict-caid':
        return [fasta_file, output_path, 'v3']
    return [fasta_file, '-o', output_path]


def input_arguments(tool, output_dir):
    """
    Build arguments that run any tool on a small input, with any output
    written inside output_dir.

    Parameters
    ----------
    tool : str
        Name of the command-line tool (one of the tools in INVALID_VERSION_CASES).

    output_dir : pathlib.Path
        An existing, empty directory for the tool's output.

    Returns
    -------
    list of str
        Arguments to pass to run_cli, before any version option.
    """
    if tool in GRAPH_TOOLS:
        return fasta_tool_arguments(tool, THREE_SEQS_FASTA, str(output_dir))
    if tool in FASTA_TOOLS:
        return fasta_tool_arguments(tool, THREE_SEQS_FASTA, str(output_dir / 'output'))
    if tool == 'metapredict-uniprot':
        return ['P04637']
    if tool == 'metapredict-name':
        return ['p53']
    return [TEST_SEQUENCE]


def assert_clean_error(result, expected_message):
    """
    Check that a tool stopped with a clean error rather than a traceback.

    Parameters
    ----------
    result : subprocess.CompletedProcess
        The finished process returned by run_cli.

    expected_message : str
        Text that must appear in the error message on stderr.

    Returns
    -------
    None
        Raises AssertionError if the tool did not stop cleanly.
    """
    assert result.returncode == 1, result.stderr + result.stdout
    assert expected_message in result.stderr, result.stderr + result.stdout
    assert 'Traceback' not in result.stderr, result.stderr


def assert_no_output(tool, output_path):
    """
    Check that a FASTA-reading tool wrote no output.

    Parameters
    ----------
    tool : str
        Name of the command-line tool (one of FASTA_TOOLS).

    output_path : pathlib.Path
        The output path the tool was given: an existing directory for the
        graphing tools (which must still be empty), otherwise a file or
        directory that must not have been created.

    Returns
    -------
    None
        Raises AssertionError if any output was written.
    """
    if tool in GRAPH_TOOLS:
        assert list(output_path.iterdir()) == []
    else:
        assert not output_path.exists()


@pytest.mark.parametrize('contents, invalid_sequence_action, expected', [('', 'ignore', False),
                                                                         ('this is not a fasta file\nMKKK\n', 'ignore', False),
                                                                         ('>a\nMKKKPPPSSS\n', 'ignore', True),
                                                                         # an empty sequence still counts as a record; the
                                                                         # tools report it when they read the file properly
                                                                         ('>header_only\n', 'ignore', True),
                                                                         ('>a\nMKJKK\n', 'ignore', True),
                                                                         ('>a\nMKJKK\n', 'remove', False),
                                                                         ('>a\nMKJKK\n>b\nMKKK\n', 'remove', True)])
def test_fasta_has_records(contents, invalid_sequence_action, expected, tmp_path):
    fasta_file = write_text_file(tmp_path / 'input.fasta', contents)
    assert fasta_has_records(fasta_file, invalid_sequence_action) == expected


@pytest.mark.parametrize('file_kind', list(NO_RECORD_FILE_CONTENTS))
@pytest.mark.parametrize('tool', FASTA_TOOLS)
def test_fasta_with_no_records(tool, file_kind, tmp_path):
    # these tools used to silently write an empty CSV, or an empty output directory
    fasta_file = write_text_file(tmp_path / f'{file_kind}.fasta', NO_RECORD_FILE_CONTENTS[file_kind])
    output_path = tmp_path / 'output'
    if tool in GRAPH_TOOLS:
        output_path.mkdir()

    result = run_cli(tool, fasta_tool_arguments(tool, fasta_file, str(output_path)))
    assert_clean_error(result, 'No sequences found in passed fasta file')
    assert_no_output(tool, output_path)


@pytest.mark.parametrize('action', ['remove', 'convert-remove'])
@pytest.mark.parametrize('tool', INVALID_SEQUENCE_ACTION_TOOLS)
def test_all_sequences_removed(tool, action, tmp_path):
    # removing every sequence used to give the same silent empty output as an empty file
    fasta_file = write_text_file(tmp_path / 'invalid.fasta', ALL_INVALID_FASTA_CONTENTS)
    output_path = tmp_path / 'output'
    if tool in GRAPH_TOOLS:
        output_path.mkdir()

    result = run_cli(tool, fasta_tool_arguments(tool, fasta_file, str(output_path)) + ['--invalid-sequence-action', action])
    assert_clean_error(result, 'No sequences left in passed fasta file')
    assert_no_output(tool, output_path)


def test_some_sequences_removed(tmp_path):
    # when only some sequences are removed, the rest are still predicted as before
    fasta_file = write_text_file(tmp_path / 'mixed.fasta', '>bad\nMKJKK\n>good\nMKKKPPPSSSDDDEEE\n')
    output_file = tmp_path / 'scores.csv'

    result = run_cli('metapredict-predict-disorder', [fasta_file, '-o', str(output_file), '-d', 'cpu', '-s', '--invalid-sequence-action', 'remove'])
    assert result.returncode == 0, result.stderr + result.stdout

    with open(output_file) as fh:
        headers = [line.split(',')[0] for line in fh.read().splitlines()]
    assert headers == ['good']


@pytest.mark.parametrize('tool', INVALID_SEQUENCE_ACTION_TOOLS)
def test_unreadable_first_record(tool, tmp_path):
    # with 'fail', the first non-standard amino acid stops the tool before anything is written
    fasta_file = write_text_file(tmp_path / 'invalid.fasta', ALL_INVALID_FASTA_CONTENTS)
    output_path = tmp_path / 'output'
    if tool in GRAPH_TOOLS:
        output_path.mkdir()

    result = run_cli(tool, fasta_tool_arguments(tool, fasta_file, str(output_path)) + ['--invalid-sequence-action', 'fail'])
    assert_clean_error(result, 'Could not read passed fasta file')
    assert_no_output(tool, output_path)


@pytest.mark.parametrize('tool', FASTA_TOOLS)
def test_missing_input_file(tool, tmp_path):
    missing_fasta = str(tmp_path / 'does_not_exist.fasta')
    output_path = tmp_path / 'output'
    if tool in GRAPH_TOOLS:
        output_path.mkdir()

    result = run_cli(tool, fasta_tool_arguments(tool, missing_fasta, str(output_path)))
    assert_clean_error(result, 'Could not find passed fasta file')
    assert_no_output(tool, output_path)


@pytest.mark.parametrize('tool, version_flag, invalid_version, option_name', INVALID_VERSION_CASES)
def test_invalid_version(tool, version_flag, invalid_version, option_name, tmp_path):
    # the version is checked before anything else, so metapredict-uniprot and
    # metapredict-name stop before they look anything up online
    result = run_cli(tool, input_arguments(tool, tmp_path) + [version_flag, invalid_version])
    assert_clean_error(result, f'{option_name} must be one of')
    assert list(tmp_path.iterdir()) == []


def test_caid_invalid_version(tmp_path):
    output_dir = tmp_path / 'caid'
    result = run_cli('metapredict-caid', [THREE_SEQS_FASTA, str(output_dir), 'v4'])
    assert_clean_error(result, 'version must be one of')
    assert not output_dir.exists()


@pytest.mark.parametrize('threshold', OUT_OF_RANGE_THRESHOLDS)
def test_predict_idrs_threshold_out_of_range(threshold, tmp_path):
    output_file = tmp_path / 'idrs.fasta'
    result = run_cli('metapredict-predict-idrs', [THREE_SEQS_FASTA, '-o', str(output_file), '-d', 'cpu', '-s', '--threshold', threshold])
    assert_clean_error(result, '--threshold must be between')
    assert not output_file.exists()


@pytest.mark.parametrize('threshold', OUT_OF_RANGE_THRESHOLDS)
def test_graph_disorder_threshold_out_of_range(threshold, tmp_path):
    result = run_cli('metapredict-graph-disorder', [THREE_SEQS_FASTA, '-o', str(tmp_path), '--disorder-threshold', threshold])
    assert_clean_error(result, '--disorder-threshold must be between')
    assert list(tmp_path.iterdir()) == []


def test_predict_idrs_invalid_mode(tmp_path):
    output_file = tmp_path / 'idrs.tsv'
    result = run_cli('metapredict-predict-idrs', [THREE_SEQS_FASTA, '-o', str(output_file), '-d', 'cpu', '-s', '--mode', 'csv'])
    assert_clean_error(result, '--mode must be set to one of')
    assert not output_file.exists()


@pytest.mark.parametrize('tool', DEVICE_TOOLS)
def test_invalid_device(tool, tmp_path):
    # 'gpu' is not a device name metapredict accepts on any machine
    output_file = tmp_path / 'output'
    result = run_cli(tool, [THREE_SEQS_FASTA, '-o', str(output_file), '-d', 'gpu', '-s'])
    assert_clean_error(result, "Invalid device 'gpu'")
    assert not output_file.exists()


@pytest.mark.parametrize('tool', DEVICE_TOOLS)
def test_integer_device(tool, tmp_path):
    # a bare GPU index is treated as cuda:0, which fails cleanly on a machine without CUDA
    output_file = tmp_path / 'output'
    result = run_cli(tool, [THREE_SEQS_FASTA, '-o', str(output_file), '-d', '0', '-s'])

    if torch.cuda.is_available():
        assert result.returncode == 0, result.stderr + result.stdout
    else:
        assert_clean_error(result, 'cuda:0 was specified as the device')
        assert not output_file.exists()


def test_predict_idrs_shephard_uniprot_bad_header_writes_nothing(tmp_path):
    # the bad header comes after a good one; the tool used to start writing the
    # output file before it found the problem, leaving a partial file behind
    fasta_file = write_text_file(tmp_path / 'headers.fasta', MIXED_UNIPROT_HEADERS_FASTA_CONTENTS)
    output_file = tmp_path / 'idrs.tsv'

    result = run_cli('metapredict-predict-idrs', [fasta_file, '-o', str(output_file), '-d', 'cpu', '-s', '--mode', 'shephard-domains-uniprot'])
    assert_clean_error(result, 'Error parsing header line: not_uniprot')
    assert not output_file.exists()


@pytest.mark.parametrize('tool', FASTA_TOOLS)
def test_invalid_residue_after_first_record(tool, tmp_path):
    # metapredict-caid always uses 'convert', which can't convert 'J', so it fails in the same way
    fasta_file = write_text_file(tmp_path / 'later_invalid.fasta', LATER_INVALID_FASTA_CONTENTS)
    output_path = tmp_path / 'output'
    if tool in GRAPH_TOOLS:
        output_path.mkdir()

    arguments = fasta_tool_arguments(tool, fasta_file, str(output_path))
    if tool in INVALID_SEQUENCE_ACTION_TOOLS:
        arguments += ['--invalid-sequence-action', 'fail']

    result = run_cli(tool, arguments)
    assert_clean_error(result, 'invalid amino acid: J')
    assert_no_output(tool, output_path)


@requires_uniprot
def test_uniprot_invalid_accession():
    result = run_cli('metapredict-uniprot', [INVALID_UNIPROT_ACCESSION])
    assert_clean_error(result, 'Could not get a sequence from UniProt')


@requires_uniprot
def test_name_with_no_match():
    result = run_cli('metapredict-name', [UNMATCHED_PROTEIN_NAME])
    assert_clean_error(result, 'Could not get a sequence from UniProt')


@requires_uniprot
@pytest.mark.parametrize('save_graph', [False, True])
def test_uniprot_graph_error(save_graph, tmp_path):
    # the sequence contains selenocysteine ('U'), so the graph can't be made
    output_file = tmp_path / 'graph.png'
    arguments = [SELENOPROTEIN_ACCESSION]
    if save_graph:
        arguments += ['-o', str(output_file)]

    result = run_cli('metapredict-uniprot', arguments)
    assert_clean_error(result, 'Could not graph disorder')
    assert not output_file.exists()


@requires_uniprot
def test_name_graph_error():
    # searching for the selenoprotein's accession finds it, and its 'U' stops the graph
    result = run_cli('metapredict-name', [SELENOPROTEIN_ACCESSION])
    assert_clean_error(result, 'Could not graph disorder')
