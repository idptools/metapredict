## Regression tests for bugs found in the October 2026 code review. Each test
## pins down the corrected behaviour so the bug can't quietly come back.

import os
import subprocess
import sys

import numpy as np
import pytest

import metapredict as meta
from metapredict.backend import predictor
from metapredict.backend import meta_tools
from metapredict.backend.data_structures import DisorderObject
from metapredict.metapredict_exceptions import MetapredictError
from metapredict.parameters import MAX_CUDA_LENGTH

# a disordered sequence whose raw (unnormalized) V3 scores go above 1, so that
# normalization and rounding behaviour is visible in the output
DISORDERED_SEQ = 'MKKKPGSSAEEESSDDKKKPPGQWERTYLIVACDEFGHIKLMNPQRSTVWYAAGGSSPPDDEEKK' * 3

# p53 has both IDRs and a folded domain, so it exercises the full domain decomposition
P53_SEQ = 'MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD'

# predictions are rounded to 4 decimal places
ROUNDING_TOLERANCE = 1e-4

# Batch-reproducibility test set: many sequences of one length, so that the order
# in which equal-length sequences are batched (which set() used to randomise per
# process) decides which sequences share a batch. Generated from a fixed seed.
AMINO_ACIDS = list('ACDEFGHIKLMNPQRSTVWY')
REPRO_SEED = 20261005
REPRO_N_SEQUENCES = 120
REPRO_LENGTH = 60
# smallest allowed batch size, so the set above is split over several batches
REPRO_BATCH_SIZE = 32

# run in a fresh interpreter: reads sequences (one per line) from argv[1] and
# saves the concatenated raw V3 batch scores to argv[2]
REPRO_SCRIPT = '''
import sys
import numpy as np
from metapredict.backend.predictor import predict
with open(sys.argv[1]) as fh:
    sequences = fh.read().split()
out = predict(sequences, version='V3', use_device='cpu', normalized=False, round_values=False, batch_size=%d)
np.save(sys.argv[2], np.concatenate([scores for _, scores in out]))
''' % REPRO_BATCH_SIZE


# --------------------------------------------------------------------------- #
# Prediction values
# --------------------------------------------------------------------------- #

def test_no_pack_n_pad_rounds_to_four_decimals():
    """With normalized=False and round_values=True, the no-pack-n-pad path used
    to round to whole numbers; it must match the pack-n-pad path."""
    packed = predictor.predict([DISORDERED_SEQ, P53_SEQ], use_device='cpu', normalized=False, round_values=True)
    unpacked = predictor.predict([DISORDERED_SEQ, P53_SEQ], use_device='cpu', normalized=False, round_values=True,
                                 disable_pack_n_pad=True)
    for (_, packed_scores), (_, unpacked_scores) in zip(packed, unpacked):
        assert np.allclose(packed_scores, unpacked_scores, atol=ROUNDING_TOLERANCE)


def test_no_pack_n_pad_pLDDT_rounds_to_four_decimals():
    packed = predictor.predict_pLDDT([DISORDERED_SEQ, P53_SEQ], use_device='cpu', normalized=False,
                                     round_values=True, return_decimals=True)
    unpacked = predictor.predict_pLDDT([DISORDERED_SEQ, P53_SEQ], use_device='cpu', normalized=False,
                                       round_values=True, return_decimals=True, disable_pack_n_pad=True)
    for (_, packed_scores), (_, unpacked_scores) in zip(packed, unpacked):
        assert np.allclose(packed_scores, unpacked_scores, atol=ROUNDING_TOLERANCE)


def test_predict_disorder_batch_respects_normalized():
    raw = predictor.predict([DISORDERED_SEQ], use_device='cpu', normalized=False, round_values=False)[0][1]
    via_batch = meta.predict_disorder_batch([DISORDERED_SEQ], device='cpu', normalized=False,
                                            round_values=False, show_progress_bar=False)[0][1]

    # this sequence's raw scores go above 1, so normalization would have changed them
    assert raw.max() > 1
    assert np.allclose(raw, via_batch)


@pytest.mark.parametrize('disable_batch', [False, True])
def test_pLDDT_list_output_is_python_floats(disable_batch):
    result = predictor.predict_pLDDT([DISORDERED_SEQ, P53_SEQ], use_device='cpu', return_numpy=False,
                                     force_disable_batch=disable_batch)
    for _, scores in result:
        assert all(type(value) is float for value in scores)


def test_pLDDT_no_pack_n_pad_list_output_is_python_floats():
    result = predictor.predict_pLDDT([DISORDERED_SEQ, P53_SEQ], use_device='cpu', return_numpy=False,
                                     disable_pack_n_pad=True)
    for _, scores in result:
        assert all(type(value) is float for value in scores)


# --------------------------------------------------------------------------- #
# Domain decomposition settings
# --------------------------------------------------------------------------- #

def test_override_folded_domain_minsize_changes_domains():
    """A 25-residue low-disorder gap between two IDRs is absorbed into the IDR by
    default (folded domains < 35 residues are treated leniently), but kept as a
    folded domain when the override sets the minimum to 20."""
    sequence = 'A' * 125
    profile = np.array([0.9] * 50 + [0.25] * 25 + [0.9] * 50)

    default = predictor.build_DisorderObject(sequence, profile, minimum_folded_domain=20)
    override = predictor.build_DisorderObject(sequence, profile, minimum_folded_domain=20,
                                              override_folded_domain_minsize=True)

    assert default.folded_domain_boundaries == []
    assert len(override.folded_domain_boundaries) == 1


def test_override_folded_domain_minsize_is_forwarded(monkeypatch):
    """Every user-facing path must pass override_folded_domain_minsize through
    to the domain decomposition (it used to be silently dropped)."""
    seen_values = []
    real_get_domains = predictor._domain_definition.get_domains

    def spy_get_domains(*args, **kwargs):
        seen_values.append(kwargs.get('override_folded_domain_minsize'))
        return real_get_domains(*args, **kwargs)

    monkeypatch.setattr(predictor._domain_definition, 'get_domains', spy_get_domains)

    predictor.predict(P53_SEQ, return_domains=True, override_folded_domain_minsize=True)
    predictor.predict([P53_SEQ, DISORDERED_SEQ], use_device='cpu', return_domains=True,
                      override_folded_domain_minsize=True)
    meta.predict_disorder_batch([P53_SEQ], device='cpu', return_domains=True,
                                override_folded_domain_minsize=True, show_progress_bar=False)

    assert len(seen_values) == 4
    assert all(value is True for value in seen_values)


def test_string_threshold_is_rejected():
    """A threshold passed as a string must fail clearly rather than crash (or be
    compared as text) inside the domain decomposition."""
    with pytest.raises(MetapredictError):
        predictor.predict([P53_SEQ], use_device='cpu', return_domains=True, disorder_threshold='0.5')

    with pytest.raises(MetapredictError):
        meta_tools.valid_range('0.5', 0.0, 1.0)

    with pytest.raises(MetapredictError):
        meta_tools.valid_range(True, 0.0, 1.0)

    # numpy floats are still fine
    meta_tools.valid_range(np.float32(0.5), 0.0, 1.0)


def test_short_sequence_window_message_is_a_warning(capsys):
    with pytest.warns(RuntimeWarning, match='smoothing window'):
        predictor.predict('MKKSAEEPKS', return_domains=True)
    assert 'Warning: length of disorder' not in capsys.readouterr().out


def test_external_scores_length_mismatch_message():
    with pytest.raises(MetapredictError, match='not length matched'):
        meta.predict_disorder_domains_from_external_scores([0.5] * 10, 'A' * 12)


@pytest.mark.parametrize('return_numpy', [True, False])
@pytest.mark.parametrize('scores', [np.array([0.1, 0.9, 0.5]), [0.1, 0.9, 0.5]])
def test_disorder_object_meta_alias(return_numpy, scores):
    disorder_object = DisorderObject('MKK', scores, [], [[0, 3]], return_numpy=return_numpy)
    assert disorder_object.meta is disorder_object.disorder
    if return_numpy:
        assert isinstance(disorder_object.disorder, np.ndarray)
    else:
        assert isinstance(disorder_object.disorder, list)


# --------------------------------------------------------------------------- #
# Input validation
# --------------------------------------------------------------------------- #

def test_empty_sequence_in_list_is_reported():
    with pytest.raises(MetapredictError, match=r'position\(s\).*\[1\]'):
        meta.predict_disorder([P53_SEQ, ''], device='cpu')


def test_empty_sequence_in_dict_is_reported():
    with pytest.raises(MetapredictError, match='empty_one'):
        meta.predict_pLDDT({'good': P53_SEQ, 'empty_one': ''}, device='cpu')


@pytest.mark.parametrize('prediction_function', [predictor.predict, predictor.predict_pLDDT])
def test_cuda_length_guard(monkeypatch, prediction_function):
    """Both disorder and pLDDT prediction must refuse sequences that are too long
    for CUDA before anything is sent to the GPU. check_device is faked to return
    'cuda' so this runs on machines without a GPU."""
    monkeypatch.setattr(predictor, 'check_device', lambda use_device, default_device=None: 'cuda')
    too_long = 'A' * (MAX_CUDA_LENGTH + 1)
    with pytest.raises(MetapredictError, match='too long to run on GPU'):
        prediction_function([too_long, P53_SEQ])


# --------------------------------------------------------------------------- #
# Device selection
# --------------------------------------------------------------------------- #

def test_digit_string_device_is_a_gpu_index():
    """The CLI passes -d 0 as the string '0'; it must be read as cuda:0."""
    if predictor.torch.cuda.is_available():
        assert predictor.check_device('0') == 'cuda:0'
    else:
        with pytest.raises(MetapredictError, match='cuda:0 was specified'):
            predictor.check_device('0')


@pytest.mark.parametrize('bad_device', ['gpu', 'cuda0', 'cuda:x', 'tpu', True])
def test_invalid_device_gives_clear_error(bad_device):
    with pytest.raises(MetapredictError) as error_info:
        predictor.check_device(bad_device)
    assert "shouldn't be able to see this message" not in str(error_info.value)


# --------------------------------------------------------------------------- #
# Performance helpers
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize('version', ['legacy', 'v3', '3', 3])
def test_print_performance_accepts_documented_versions(version):
    residues_per_second = meta.print_performance(seq_len=30, num_seqs=10, version=version,
                                                 verbose=False, device='cpu')
    assert residues_per_second > 0


def test_print_performance_bad_version():
    with pytest.raises(MetapredictError):
        meta.print_performance(seq_len=30, num_seqs=10, version='V99', verbose=False, device='cpu')
    with pytest.raises(MetapredictError):
        meta.print_performance_backend(seq_len=30, num_seqs=10, version='V99', verbose=False, device='cpu')


# --------------------------------------------------------------------------- #
# Batch reproducibility
# --------------------------------------------------------------------------- #

def _repro_sequences():
    """The equal-length sequences used by the batch-reproducibility tests."""
    rng = np.random.default_rng(REPRO_SEED)
    return [''.join(rng.choice(AMINO_ACIDS, size=REPRO_LENGTH)) for _ in range(REPRO_N_SEQUENCES)]


def test_batch_predictions_identical_across_hash_seeds(tmp_path):
    """Batch predictions must not depend on Python's per-process string-hash
    seed. They used to, because sequences were deduplicated with set(), whose
    order (and so which sequences shared a batch) changed from run to run."""
    sequence_file = tmp_path / 'sequences.txt'
    sequence_file.write_text('\n'.join(_repro_sequences()))

    # make the subprocesses import the same metapredict this test is using
    package_parent = os.path.dirname(os.path.dirname(os.path.abspath(meta.__file__)))
    python_path = os.pathsep.join(p for p in [package_parent, os.environ.get('PYTHONPATH', '')] if p)

    results = []
    for hash_seed in ['1', '2']:
        out_file = tmp_path / f'scores_seed{hash_seed}.npy'
        env = dict(os.environ, PYTHONHASHSEED=hash_seed, PYTHONPATH=python_path)
        subprocess.run([sys.executable, '-c', REPRO_SCRIPT, str(sequence_file), str(out_file)],
                       env=env, check=True, capture_output=True)
        results.append(np.load(out_file))

    assert np.array_equal(results[0], results[1])


def test_batch_predictions_independent_of_input_order():
    """The same sequences give bit-for-bit the same scores whether passed as a
    list, a reversed list, or a dictionary."""
    sequences = _repro_sequences()
    common = dict(version='V3', use_device='cpu', normalized=False, round_values=False,
                  batch_size=REPRO_BATCH_SIZE)

    as_list = {seq: scores for seq, scores in predictor.predict(sequences, **common)}
    as_reversed = {seq: scores for seq, scores in predictor.predict(sequences[::-1], **common)}
    as_dict = {seq: scores for seq, scores in predictor.predict({f'id{i}': s for i, s in enumerate(sequences)}, **common).values()}

    for seq in sequences:
        assert np.array_equal(as_list[seq], as_reversed[seq])
        assert np.array_equal(as_list[seq], as_dict[seq])


def test_unique_sequences_in_batch_order():
    ordered = predictor.unique_sequences_in_batch_order(['BB', 'AAA', 'AA', 'BB', 'CCC'])
    assert ordered == ['AAA', 'CCC', 'AA', 'BB']


# --------------------------------------------------------------------------- #
# File names
# --------------------------------------------------------------------------- #

def test_package_file_names_are_valid_on_windows():
    """Every file in the metapredict package must have a name Windows accepts.
    Three test fixtures named after a UniProt header (containing '|') used to
    make git clone and pip install fail on Windows."""
    package_dir = os.path.dirname(os.path.abspath(meta.__file__))
    invalid_names = []
    for root, dirs, files in os.walk(package_dir):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for name in dirs + files:
            has_invalid_character = meta_tools.INVALID_FILENAME_CHARACTERS.search(name) is not None
            has_trailing_dot_or_space = name.rstrip(' .') != name
            is_reserved = name.split('.')[0].upper() in meta_tools.WINDOWS_RESERVED_NAMES
            if has_invalid_character or has_trailing_dot_or_space or is_reserved:
                invalid_names.append(os.path.relpath(os.path.join(root, name), package_dir))
    assert invalid_names == []


# --------------------------------------------------------------------------- #
# Vectorized rounding of list outputs
# --------------------------------------------------------------------------- #

def test_scores_to_rounded_list_matches_python_round():
    """The vectorized rounding used for list outputs must give exactly what
    per-value round(float(x), 4) gives, including on 4-decimal halfway points,
    for disorder-scale and pLDDT-scale float32 scores."""
    rng = np.random.default_rng(REPRO_SEED)
    halfway_points = (np.arange(-20000, 20000) + 0.5) / 10000
    values = np.concatenate([rng.uniform(-0.5, 1.5, 200_000),
                             rng.uniform(0, 100, 200_000),
                             halfway_points]).astype(np.float32)

    vectorized = predictor.scores_to_rounded_list(values)
    assert vectorized == [round(float(x), 4) for x in values]
    assert all(type(x) is float for x in vectorized)


LIST_OUTPUT_CASES = [
    ('disorder single', predictor.predict, dict(version='V3'), True),
    ('disorder V3 batch', predictor.predict, dict(version='V3'), False),
    ('disorder V1 batch', predictor.predict, dict(version='V1'), False),
    ('disorder unnormalized', predictor.predict, dict(version='V3', normalized=False), False),
    ('disorder no pack-n-pad', predictor.predict, dict(version='V3', disable_pack_n_pad=True), False),
    ('disorder unbatched', predictor.predict, dict(version='V3', force_disable_batch=True), False),
    ('pLDDT V2 batch', predictor.predict_pLDDT, dict(version='V2'), False),
    ('pLDDT V1 decimals', predictor.predict_pLDDT, dict(version='V1', return_decimals=True), False),
    ('pLDDT as disorder', predictor.predict_pLDDT, dict(version='V2', return_as_disorder_score=True), False),
    ('pLDDT no pack-n-pad', predictor.predict_pLDDT, dict(version='V2', disable_pack_n_pad=True), False),
]


@pytest.mark.parametrize('label, prediction_function, options, single_sequence', LIST_OUTPUT_CASES,
                         ids=[case[0] for case in LIST_OUTPUT_CASES])
def test_list_output_matches_rounded_array_output(label, prediction_function, options, single_sequence):
    """return_numpy=False must give exactly the per-value Python rounding of
    the return_numpy=True scores, on every prediction path."""
    if single_sequence:
        as_array = prediction_function(P53_SEQ, return_numpy=True, **options)
        as_list = prediction_function(P53_SEQ, return_numpy=False, **options)
        assert as_list == [round(float(x), 4) for x in as_array]
        return

    sequences = [P53_SEQ, DISORDERED_SEQ] + _repro_sequences()[:10]
    as_array = prediction_function(sequences, use_device='cpu', return_numpy=True, **options)
    as_list = prediction_function(sequences, use_device='cpu', return_numpy=False, **options)
    for (_, array_scores), (_, list_scores) in zip(as_array, as_list):
        assert list_scores == [round(float(x), 4) for x in array_scores]
