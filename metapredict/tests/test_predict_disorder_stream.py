# Tests for predict_disorder_stream() -- the memory-bounded, streaming counterpart
# to predict_disorder() for very large FASTA files.
#
# These exercise the REAL protfasta.read_fasta_stream() (requires protfasta with
# read_fasta_stream; the module skips otherwise). The streaming path reads records
# lazily, predicts them in chunks, and yields results one at a time; it must
# produce exactly the same predictions as normal batch prediction, in file order,
# regardless of chunk size, while only holding one chunk in memory at a time.

import os
import types

import numpy as np
import protfasta
import pytest

import metapredict as meta
from metapredict.metapredict_exceptions import MetapredictError

HERE = os.path.dirname(os.path.abspath(__file__))
FASTA = os.path.join(HERE, "input_data", "ground_truth_500_seqs.fasta")

TOL = 1e-4

pytestmark = pytest.mark.skipif(
    not hasattr(protfasta, "read_fasta_stream"),
    reason="installed protfasta has no read_fasta_stream()",
)

# reference batch predictions (computed once)
_SEQS = protfasta.read_fasta(FASTA, invalid_sequence_action="convert")
_REF = {
    v: meta.predict_disorder(_SEQS, version=v, device="cpu", round_values=False, show_progress_bar=False)
    for v in ("1", "3")
}


# --------------------------------------------------------------------------- #
# Correctness: streamed predictions == all-in-memory batch predictions
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("version", ["1", "3"])
def test_stream_matches_batch(version):
    """Streamed predictions equal the batch predictions, in file order."""
    streamed = dict(meta.predict_disorder_stream(FASTA, version=version, device="cpu",
                                                 round_values=False, chunk_size=137))
    assert list(streamed.keys()) == list(_REF[version].keys())  # order preserved
    for h in _REF[version]:
        assert np.allclose(streamed[h][1], _REF[version][h][1], atol=TOL)


@pytest.mark.parametrize("chunk_size", [1, 50, 137, 500, 5000])
def test_stream_chunk_size_invariance(chunk_size):
    """The chunk size affects only memory/speed, never the predictions."""
    streamed = dict(meta.predict_disorder_stream(FASTA, version="3", device="cpu",
                                                 round_values=False, chunk_size=chunk_size))
    assert len(streamed) == len(_REF["3"])
    for h in _REF["3"]:
        assert np.allclose(streamed[h][1], _REF["3"][h][1], atol=TOL)


def test_stream_return_domains():
    """return_domains=True streams DisorderObjects whose scores match batch mode."""
    ref = meta.predict_disorder(_SEQS, version="3", device="cpu", return_domains=True,
                                show_progress_bar=False)
    streamed = dict(meta.predict_disorder_stream(FASTA, version="3", device="cpu",
                                                 return_domains=True, chunk_size=200))
    assert len(streamed) == len(ref)
    for h in list(ref)[:50]:
        assert type(streamed[h]).__name__ == "DisorderObject"
        assert np.allclose(streamed[h].disorder, ref[h].disorder, atol=TOL)


# --------------------------------------------------------------------------- #
# Streaming behaviour: laziness / bounded memory
# --------------------------------------------------------------------------- #

def test_stream_is_lazy_generator():
    """Calling the function returns a generator (no work done until iterated)."""
    gen = meta.predict_disorder_stream(FASTA, version="3", device="cpu")
    assert isinstance(gen, types.GeneratorType)
    gen.close()


def test_stream_reads_lazily(monkeypatch):
    """Consuming only the first few results must not read the whole file: peak
    memory is bounded by chunk_size, not file size."""
    real = protfasta.read_fasta_stream
    counter = {"n": 0}

    def counting(*args, **kwargs):
        for record in real(*args, **kwargs):
            counter["n"] += 1
            yield record

    monkeypatch.setattr(protfasta, "read_fasta_stream", counting)

    gen = meta.predict_disorder_stream(FASTA, version="3", device="cpu", chunk_size=20)
    first_five = [next(gen) for _ in range(5)]
    assert len(first_five) == 5
    # only ~one chunk should have been read from disk, not all 500 records
    assert counter["n"] <= 40, f"read {counter['n']} records to produce 5 predictions -- not streaming"
    gen.close()


# --------------------------------------------------------------------------- #
# FASTA handling passes through to read_fasta_stream
# --------------------------------------------------------------------------- #

def test_stream_duplicate_sequences(tmp_path):
    """Distinct records that share a sequence are both streamed, with identical
    scores (metapredict de-duplicates within a chunk but returns every header)."""
    seq = "MKAPSNGFLPSSNEGEKKPINSQLWHACAGPLVSLPKKGSLVVYFPQGHSEQVAKKISEH"
    fasta = tmp_path / "dup.fasta"
    fasta.write_text(f">a\n{seq}\n>b\n{seq}\n>c\n{seq[::-1]}\n")

    out = dict(meta.predict_disorder_stream(str(fasta), version="3", device="cpu", round_values=False))
    assert set(out) == {"a", "b", "c"}
    # a and b are the same sequence -> identical scores
    assert np.allclose(out["a"][1], out["b"][1])
    # c is a different sequence
    assert not np.allclose(out["a"][1][:len(out["c"][1])], out["c"][1], atol=1e-2)


def test_stream_invalid_sequence_action(tmp_path):
    """invalid_sequence_action is forwarded to read_fasta_stream."""
    fasta = tmp_path / "invalid.fasta"
    fasta.write_text(">x\nMKAPXBZSNGFLPSSNEGEKKPINSQLW\n")  # X, B, Z are non-standard

    # 'convert' cleans the sequence and streams normally
    out = dict(meta.predict_disorder_stream(str(fasta), version="3", device="cpu",
                                            invalid_sequence_action="convert"))
    assert "x" in out and len(out["x"][1]) == len("MKAPXBZSNGFLPSSNEGEKKPINSQLW")

    # 'fail' rejects the non-standard residues (raised mid-iteration by protfasta)
    with pytest.raises(Exception):
        list(meta.predict_disorder_stream(str(fasta), version="3", device="cpu",
                                          invalid_sequence_action="fail"))


def test_stream_matches_predict_disorder_on_small_file(tmp_path):
    """End-to-end cross-check on a freshly written file: stream == predict_disorder."""
    seqs = {k: _SEQS[k] for k in list(_SEQS)[:30]}
    fasta = tmp_path / "small.fasta"
    protfasta.write_fasta(seqs, str(fasta))

    batch = meta.predict_disorder(seqs, version="2", device="cpu", round_values=False,
                                  show_progress_bar=False)
    streamed = dict(meta.predict_disorder_stream(str(fasta), version="2", device="cpu",
                                                 round_values=False, chunk_size=8))
    assert list(streamed.keys()) == list(batch.keys())
    for h in batch:
        assert np.allclose(streamed[h][1], batch[h][1], atol=TOL)


# --------------------------------------------------------------------------- #
# Eager validation / error paths
# --------------------------------------------------------------------------- #

def test_stream_requires_read_fasta_stream(monkeypatch):
    """A clear error is raised (eagerly) if protfasta has no read_fasta_stream."""
    monkeypatch.delattr(protfasta, "read_fasta_stream", raising=False)
    with pytest.raises(MetapredictError):
        meta.predict_disorder_stream(FASTA, version="3")


@pytest.mark.parametrize("bad", [0, -1, 3.5, "x", None, True])
def test_stream_invalid_chunk_size(bad):
    """chunk_size must be a positive integer; validated eagerly at call time."""
    with pytest.raises(MetapredictError):
        meta.predict_disorder_stream(FASTA, version="3", chunk_size=bad)


# --------------------------------------------------------------------------- #
# Flat-memory streaming options (expect_unique_header / duplicate actions)
# --------------------------------------------------------------------------- #

def _tiny_fasta(tmp_path, n=5, name="tiny.fasta"):
    f = tmp_path / name
    f.write_text("".join(f">s{i}\nMKKAADESEQ\n" for i in range(n)))
    return str(f)


def test_stream_flat_matches_default():
    """expect_unique_header=False (flat memory) yields identical predictions."""
    flat = dict(meta.predict_disorder_stream(FASTA, version="3", device="cpu",
                                             round_values=False, chunk_size=137,
                                             expect_unique_header=False))
    assert list(flat.keys()) == list(_REF["3"].keys())
    for h in _REF["3"]:
        assert np.allclose(flat[h][1], _REF["3"][h][1], atol=TOL)


def test_stream_flat_by_default_no_warning(tmp_path):
    """Default streaming is memory-flat and emits no memory warning."""
    import warnings
    f = _tiny_fasta(tmp_path)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        list(meta.predict_disorder_stream(f, version="3", device="cpu", chunk_size=2))
    assert not [w for w in caught if "O(number of records)" in str(w.message)]


def test_stream_warns_when_check_enabled(tmp_path):
    """Opting into duplicate-header detection warns that memory now grows."""
    f = _tiny_fasta(tmp_path)
    with pytest.warns(UserWarning, match=r"O\(number of records\)"):
        list(meta.predict_disorder_stream(f, version="3", device="cpu",
                                          chunk_size=2, expect_unique_header=True))


def test_stream_silence_warnings(tmp_path):
    """silence_warnings=True suppresses the memory warning."""
    import warnings
    f = _tiny_fasta(tmp_path)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        list(meta.predict_disorder_stream(f, version="3", device="cpu",
                                          chunk_size=2, silence_warnings=True))
    assert not [w for w in caught if "O(number of records)" in str(w.message)]


def test_stream_unique_header_promotion(tmp_path):
    """expect_unique_header=True with the default duplicate_record_action='ignore'
    is transparently reconciled (protfasta forbids that pair) instead of raising."""
    f = _tiny_fasta(tmp_path)
    out = dict(meta.predict_disorder_stream(f, version="3", device="cpu", chunk_size=2,
                                            expect_unique_header=True,
                                            duplicate_record_action="ignore"))
    assert len(out) == 5


def test_stream_duplicate_header_detection(tmp_path):
    """Default (flat) streaming does not track headers; expect_unique_header=True raises.

    (chunk_size=1 keeps the two same-header records in separate chunks; within a
    single chunk metapredict's header-keyed dict would otherwise collapse them.)
    """
    f = tmp_path / "dup.fasta"
    f.write_text(">h\nMKKQ\n>h\nMKKQ\n")
    # default is flat -> duplicate headers are not detected, both records stream
    out = list(meta.predict_disorder_stream(str(f), version="3", device="cpu", chunk_size=1))
    assert len(out) == 2
    # opt in to detection -> raises on the duplicate header
    with pytest.raises(Exception):
        list(meta.predict_disorder_stream(str(f), version="3", device="cpu",
                                          chunk_size=1, expect_unique_header=True))
