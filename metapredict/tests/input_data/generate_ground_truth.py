"""Generate (or regenerate) the ground-truth disorder-prediction baselines.

The 500 sequences used are the first 500 entries of the human reference
proteome (UniProt UP000005640_9606) and are stored next to this script in
``ground_truth_500_seqs.fasta`` so that the baselines can be regenerated from
this repository alone, without the (large, external) full proteome file.

For every metapredict disorder network (V1, V2, V3) and every locally-available
device (CPU, and MPS / CUDA if present) this script writes one file:

    ground_truth_500_v{1,2,3}_{cpu,mps,cuda}.npy  ->  dict {seq_id: float32 scores}

Predictions are made with ``round_values=False`` (full float32 precision) so the
baseline is maximally sensitive: it is intended for confirming that changes to
metapredict (for example, network batch sizes) do not alter predicted scores.

Usage
-----
    python generate_ground_truth.py

Only devices that are actually available are generated; the rest are skipped
with a message (e.g. MPS files can only be produced on Apple-silicon hardware).
"""

import os

import numpy as np
import protfasta
import torch

import metapredict as meta

HERE = os.path.dirname(os.path.abspath(__file__))
FASTA = os.path.join(HERE, "ground_truth_500_seqs.fasta")

VERSIONS = ("1", "2", "3")
DEVICES = ("cpu", "mps", "cuda")


def device_available(device):
    """Return True if the given torch device can be used on this machine."""
    if device == "cpu":
        return True
    if device == "mps":
        return hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
    if device == "cuda":
        return torch.cuda.is_available()
    return False


def main():
    sequences = protfasta.read_fasta(FASTA, invalid_sequence_action="convert")
    print(f"Loaded {len(sequences)} sequences from {os.path.basename(FASTA)}")
    for version in VERSIONS:
        bs = meta.metapredict_networks[f"V{version}"]["parameters"]["batch_size"]
        for device in DEVICES:
            if not device_available(device):
                print(f"  v{version} {device}: skipped (device not available)")
                continue
            preds = meta.predict_disorder(
                sequences,
                version=version,
                device=device,
                normalized=True,
                round_values=False,  # full float precision -> most sensitive baseline
                return_numpy=True,
                show_progress_bar=False,
            )
            # preds maps seq_id -> [sequence, scores]
            scores = {k: np.asarray(v[1], dtype=np.float32) for k, v in preds.items()}
            out = os.path.join(HERE, f"ground_truth_500_v{version}_{device}.npy")
            np.save(out, scores, allow_pickle=True)
            print(f"  v{version} {device} (batch_size={bs}): wrote "
                  f"{os.path.basename(out)} ({len(scores)} seqs)")


if __name__ == "__main__":
    main()
