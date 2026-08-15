"""T-probe round 5: turning location-bias decomposition (RESEARCH_NOTES A20).

Materialized from the 2026-08-15 one-off run that produced
results/tprobe/tprobe5_locbias.json (provenance gap flagged by handoff agent).

Decomposes the oracle turning signal into location/dataset bias: XZ-only vs
seq-ID-only vs XZ+seqID vs dheading-only vs full, under (A) the pre-registered
seq-held-out split and (B) a within-seq sample-hash split (CAVEAT: tprobe3
samples carry no tid, so split B leaks frames of the same track across the
split — its XZ/full numbers are optimistic; the seqid row is unaffected since
the feature is constant per sequence and measures per-seq base rate only).

Run: python diagnostics/tprobe5_locbias.py
"""
import json, os, sys

import numpy as np

sys.path.insert(0, "/home/seanachan/GMC-Link")
import diagnostics.tprobe3_oracle as t3
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score

OUT = "/home/seanachan/GMC-Link/results/tprobe/tprobe5_locbias.json"
PROBE_TEST_SEQS = {"0001", "0006", "0010", "0016"}


def main():
    samples = t3.extract()
    X = np.stack([s["X"] for s in samples])
    y = np.array([s["e_turning"] for s in samples]).astype(int)
    seqs = sorted({s["seq"] for s in samples})
    seq_oh = np.zeros((len(samples), len(seqs)), np.float32)
    for i, s in enumerate(samples):
        seq_oh[i, seqs.index(s["seq"])] = 1.0

    def run(Xa, tr, te):
        if len(set(y[tr])) < 2 or len(set(y[te])) < 2:
            return None
        sc = StandardScaler().fit(Xa[tr])
        clf = LogisticRegression(max_iter=2000, class_weight="balanced",
                                 random_state=0).fit(sc.transform(Xa[tr]), y[tr])
        return round(float(f1_score(y[te], clf.predict(sc.transform(Xa[te])),
                                    average="macro")), 4)

    ARMS = {
        "XZ_only": X[:, :, [0, 1]].reshape(len(samples), -1),
        "seqid_only": seq_oh,
        "XZ+seqid": np.concatenate(
            [X[:, :, [0, 1]].reshape(len(samples), -1), seq_oh], axis=1),
        "dheading_only": X[:, :, [8, 9, 10]].reshape(len(samples), -1),
        "full": X.reshape(len(samples), -1),
    }
    trA = [i for i, s in enumerate(samples) if s["seq"] not in PROBE_TEST_SEQS]
    teA = [i for i, s in enumerate(samples) if s["seq"] in PROBE_TEST_SEQS]
    # NB: the original one-off used Python's salted hash() — split B was not
    # reproducible run-to-run. Deterministic here on; within-seq numbers may
    # differ slightly from the recorded 2026-08-15 values (seqid row robust).
    import hashlib
    tidkey = [int(hashlib.md5(f"{s['seq']}:{i}".encode()).hexdigest(), 16) % 10
              for i, s in enumerate(samples)]
    trB = [i for i, k in enumerate(tidkey) if k >= 3]
    teB = [i for i, k in enumerate(tidkey) if k < 3]

    res = {}
    for name, Xa in ARMS.items():
        res[name] = {"seq_heldout": run(Xa, trA, teA),
                     "within_seq": run(Xa, trB, teB)}
        print(f"{name:>14}: {res[name]}")
    json.dump(res, open(OUT, "w"), indent=2)
    print(f"saved -> {OUT}")


if __name__ == "__main__":
    main()
