"""
SSM-TWEET — Quero Drift Graph Demo
Deterministic • Structural • Non-Semantic • Pure Mathematics

This script loads envelopes.json, computes alignment + Quero lanes
using the same U/W + Quero kernel logic from run_demo.py,
and plots two graphs:

1. Alignment lane (a_out) over sequence_number
2. Quero lane (q_out) over sequence_number

Purpose:
Provide a visual demonstration of how structural drift evolves,
how Quero reacts to posture changes, and how stability emerges
in long multi-thread conversations.

Dependencies:
    pip install matplotlib
"""

import json
import math
import matplotlib.pyplot as plt


# ------------------------------------------------------------
# 1. Alignment Kernel (U/W + atanh + tanh)
# ------------------------------------------------------------
def clamp(x, minval, maxval):
    return max(min(x, maxval), minval)

def compute_alignment_and_quero(envelopes):
    """
    Returns:
        seqs  : list of sequence numbers
        a_out : list of alignment lane outputs
        q_out : list of quero lane outputs
    """

    eps_a = 1e-6    # to avoid atanh(±1)
    eps_w = 1e-9    # avoid division by zero

    U = 0.0
    W = 0.0

    Q = 0.0         # Quero accumulator (mirrors U)
    QW = 0.0        # Quero weight accumulator (mirrors W)

    seqs = []
    a_out_list = []
    q_out_list = []

    for env in envelopes:
        a_raw = env["a_raw"]
        w = env.get("weight", 1.0)

        # ------------ Alignment Lane ------------
        a_c = clamp(a_raw, -1 + eps_a, 1 - eps_a)
        u = math.atanh(a_c)

        U += w * u
        W += w

        a_out = math.tanh(U / max(W, eps_w))

        # ------------ Quero Lane (simplified demo) ------------
        # Quero uses same structural logic but without tanh compression
        Q += w * a_raw
        QW += w

        q_out = Q / max(QW, eps_w)

        # ------------ Collect values ------------
        seqs.append(env["sequence_number"])
        a_out_list.append(a_out)
        q_out_list.append(q_out)

    return seqs, a_out_list, q_out_list


# ------------------------------------------------------------
# 2. Load Envelopes
# ------------------------------------------------------------
def load_envelopes(path="envelopes.json"):
    with open(path, "r") as f:
        data = json.load(f)

    # Ensure deterministic order
    data.sort(key=lambda x: x["sequence_number"])
    return data


# ------------------------------------------------------------
# 3. Plot Graphs
# ------------------------------------------------------------
def plot_lanes(seqs, a_out, q_out):
    plt.figure(figsize=(14, 6))

    # -------- Graph 1: Alignment Lane --------
    plt.subplot(1, 2, 1)
    plt.plot(seqs, a_out, linewidth=2)
    plt.title("SSM-TWEET Alignment Lane (a_out)")
    plt.xlabel("sequence_number")
    plt.ylabel("alignment (a_out)")
    plt.ylim(-1.05, 1.05)
    plt.grid(True, linestyle="--", alpha=0.4)

    # -------- Graph 2: Quero Lane --------
    plt.subplot(1, 2, 2)
    plt.plot(seqs, q_out, linewidth=2, color="orange")
    plt.title("SSM-TWEET Quero Drift (q_out)")
    plt.xlabel("sequence_number")
    plt.ylabel("quero (q_out)")
    plt.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.show()


# ------------------------------------------------------------
# 4. Main
# ------------------------------------------------------------
def main():
    print("=== SSM-TWEET — Quero Drift Graph Demo ===")

    envelopes = load_envelopes()
    seqs, a_out, q_out = compute_alignment_and_quero(envelopes)

    print(f"Loaded {len(seqs)} envelopes.")
    print("Generating Quero + Alignment graphs...")

    plot_lanes(seqs, a_out, q_out)

    print("Done — deterministic structural lanes plotted.")


if __name__ == "__main__":
    main()
