## Helper functions shared by the metapredict command-line tools.
##
## The exit_if_* functions check one kind of input. If the input is fine they
## return normally; if not, they print a one-line error to stderr and stop the
## tool with exit status 1, like the other input checks in the scripts.

import sys

import protfasta

from metapredict.backend.meta_tools import valid_batch_size, valid_version
from metapredict.backend.network_parameters import metapredict_networks, pplddt_networks
from metapredict.backend.predictor import resolve_batch_size
from metapredict.metapredict_exceptions import MetapredictError

# Devices described in the --batch-size help text, in the order they are
# listed, with the names shown to users
BATCH_SIZE_HELP_DEVICES = [('cpu', 'CPU'), ('cuda', 'CUDA'), ('mps', 'MPS (Apple Silicon)')]


def fasta_has_records(filename, invalid_sequence_action='ignore'):
    """
    Check whether a FASTA file has at least one record left to predict.

    We use this so the command-line tools can stop with a clear error when
    there is nothing to predict (for example an empty file, a text file with no
    '>' header lines, or a file where --invalid-sequence-action remove takes
    out every sequence), rather than silently writing an empty output file.
    Records are read one at a time and we stop at the first one that is kept,
    so this is quick even for very large files.

    Empty sequences are deliberately not checked here: the tools report those
    themselves when they read the file properly.

    Parameters
    ----------
    filename : str
        Path to the FASTA file. The file must exist.

    invalid_sequence_action : str
        How protfasta should deal with sequences that contain non-standard
        amino acids, as for --invalid-sequence-action. Records that this
        action removes (with 'remove' or 'convert-remove') don't count.
        Default = 'ignore', which counts every record in the file.

    Returns
    -------
    bool
        True if at least one record is kept, False if there are none.

    Raises
    ------
    protfasta.ProtfastaException
        If protfasta can't read a record it reaches, for example because it
        contains a non-standard amino acid and invalid_sequence_action is
        'fail', or if invalid_sequence_action isn't a valid option.
    """

    # protfasta's streaming reader parses and filters the file exactly as
    # read_fasta does, but lets us stop after the first record that is kept
    records = protfasta.read_fasta_stream(filename,
                                          invalid_sequence_action=invalid_sequence_action,
                                          empty_sequence_action='ignore')
    try:
        first_record = next(records, None)
    finally:
        records.close()

    return first_record is not None


def exit_if_no_sequences(filename, invalid_sequence_action, read_whole_file=False):
    """
    Stop the tool with a clear error if a FASTA file has no sequences to predict.

    This covers a file with no records at all, a file where
    invalid_sequence_action removes every sequence, and a file protfasta
    can't read (for example a non-standard amino acid with
    invalid_sequence_action='fail').

    Parameters
    ----------
    filename : str
        Path to the FASTA file. The file must exist.

    invalid_sequence_action : str
        The --invalid-sequence-action the tool will read the file with.

    read_whole_file : bool
        If False (default), only read as far as the first sequence that is
        kept, which is quick but only catches read problems up to that point.
        If True, read the whole file exactly as the prediction functions will,
        so a problem in any record is reported now, with the same clear error,
        before the tool writes anything. The graphing tools need this because
        they create their default output directory before graphing; the
        graphing tools and metapredict-caid otherwise only find a bad record
        partway through their own work.

    Returns
    -------
    None
        Returns normally if there is at least one sequence to predict.
        Otherwise prints a one-line error to stderr and exits with status 1.
    """
    try:
        if read_whole_file:
            sequences = protfasta.read_fasta(filename, invalid_sequence_action=invalid_sequence_action)
            has_sequences = len(sequences) > 0
        else:
            has_sequences = fasta_has_records(filename, invalid_sequence_action)
    except protfasta.ProtfastaException as e:
        # protfasta's messages can run over several lines; keep ours to one
        message = ' '.join(str(e).split())
        print(f'Error: Could not read passed fasta file [{filename}]: {message}', file=sys.stderr)
        sys.exit(1)

    if has_sequences:
        return

    # say whether the file was empty, or whether every sequence was removed
    if fasta_has_records(filename):
        print(f'Error: No sequences left in passed fasta file [{filename}] after applying --invalid-sequence-action {invalid_sequence_action}', file=sys.stderr)
    else:
        print(f'Error: No sequences found in passed fasta file [{filename}]', file=sys.stderr)
    sys.exit(1)


def exit_if_invalid_version(version, prediction_type, option_name):
    """
    Stop the tool with a clear error if a network version doesn't exist.

    The version is checked with the same function the prediction code uses,
    so anything accepted here (e.g. '3', 'v3' or 'V3') is accepted there.

    Parameters
    ----------
    version : str
        The network version passed on the command line.

    prediction_type : str
        'disorder' for a disorder network version, or 'pLDDT' for a pLDDT
        network version.

    option_name : str
        The command-line option (or argument) the version came from, e.g.
        '--version', which is named in the error message.

    Returns
    -------
    None
        Returns normally if the version exists. Otherwise prints a one-line
        error to stderr and exits with status 1.
    """
    if prediction_type == 'disorder':
        valid_networks = list(metapredict_networks)
    elif prediction_type == 'pLDDT':
        valid_networks = list(pplddt_networks)
    else:
        raise ValueError(f"prediction_type must be 'disorder' or 'pLDDT' (got {prediction_type!r})")

    try:
        valid_version(version, prediction_type)
    except MetapredictError:
        print(f"Error: {option_name} must be one of {', '.join(valid_networks)} (got '{version}')", file=sys.stderr)
        sys.exit(1)


def exit_if_invalid_batch_size(batch_size, option_name):
    """
    Stop the tool with a clear error if a batch size isn't allowed.

    The batch size is checked with the same function the prediction code uses
    (it must be a power of two of at least 32), so a bad value is reported
    before any file is read, rather than partway through a prediction.

    Parameters
    ----------
    batch_size : int or None
        The batch size passed on the command line, or None if the option
        wasn't given (metapredict then picks a default for the network and
        device).

    option_name : str
        The command-line option the batch size came from, e.g.
        '--batch-size', which is named in the error message.

    Returns
    -------
    None
        Returns normally if the batch size is valid or None. Otherwise prints
        a one-line error to stderr and exits with status 1.
    """
    try:
        valid_batch_size(batch_size)
    except MetapredictError:
        print(f'Error: {option_name} must be a power of two of at least 32, e.g. 32, 64, 128, 256, 512 or 1024 (got {batch_size})', file=sys.stderr)
        sys.exit(1)


def _join_words(words, conjunction='and'):
    """
    Join words as English prose: 'a', 'a and b', or 'a, b and c'.

    Parameters
    ----------
    words : list of str
        The words to join; must not be empty.

    conjunction : str
        The word placed before the last item. Default = 'and'.

    Returns
    -------
    str
        The joined words.
    """
    if len(words) == 1:
        return words[0]
    return ', '.join(words[:-1]) + f' {conjunction} ' + words[-1]


def describe_default_batch_sizes(networks):
    """
    Describe, in one sentence, each network's default batch size on each device.

    The defaults are worked out with resolve_batch_size(), the same function
    the predictor uses when no batch size is given, so the description always
    matches what is actually used. Networks with identical defaults are
    described together.

    Parameters
    ----------
    networks : dict
        Maps a network version (e.g. 'V1') to its entry in
        metapredict_networks or pplddt_networks (a dict with a 'parameters'
        entry).

    Returns
    -------
    str
        For example 'V1, V2 and V3 use 256 on CPU or CUDA and 512 on MPS
        (Apple Silicon).'
    """
    # versions whose defaults are described the same way are grouped together
    versions_by_description = {}
    for version, network in networks.items():
        devices_by_size = {}
        for device, device_name in BATCH_SIZE_HELP_DEVICES:
            size = resolve_batch_size(None, device, network['parameters'])
            devices_by_size.setdefault(size, []).append(device_name)

        size_phrases = [f"{size} on {_join_words(device_names, 'or')}" for size, device_names in devices_by_size.items()]
        description = _join_words(size_phrases)
        versions_by_description.setdefault(description, []).append(version)

    clauses = []
    for description, versions in versions_by_description.items():
        verb = 'uses' if len(versions) == 1 else 'use'
        clauses.append(f'{_join_words(versions)} {verb} {description}')
    return '; '.join(clauses) + '.'


def batch_size_help(prediction_type):
    """
    The --batch-size help text for a command-line tool, including the default
    batch size of each network on each device.

    Parameters
    ----------
    prediction_type : str
        'disorder' for a tool that predicts disorder, or 'pLDDT' for a tool
        that predicts pLDDT scores.

    Returns
    -------
    str
        The help text.
    """
    if prediction_type == 'disorder':
        networks = metapredict_networks
    elif prediction_type == 'pLDDT':
        networks = pplddt_networks
    else:
        raise ValueError(f"prediction_type must be 'disorder' or 'pLDDT' (got {prediction_type!r})")

    return ('Optional. Number of sequences run through the network together in each batch. '
            'Must be a power of two of at least 32 (e.g. 32, 64, 128, 256, 512, 1024). '
            'Larger batches are usually faster on a GPU but use more memory. '
            'Default batch size, by network: ' + describe_default_batch_sizes(networks))
