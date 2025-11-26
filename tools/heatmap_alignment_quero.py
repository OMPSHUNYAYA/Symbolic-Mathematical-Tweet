import json
import math
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------------
# SSM-TWEET Heatmap Demo — Alignment + Quero Intensity Map
# Uses envelopes.json (or user-specified file)
# -------------------------------------------------------------

EPS_A = 1e-6
EPS_W = 1e-9
CLAMP_MIN = -1 + EPS_A
CLAMP_MAX = +1 - EPS_A

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def compute_alignment_and_quero(envelopes):
    """Returns arrays: seq[], a_out[], q_out[] for heatmap."""
    U = 0.0
    W = 0.0
    Q = 0.0

    seq_list = []
    a_out_list = []
    q_out_list = []

    prev_u = None

    for env in envelopes:
        seq = env["sequence_number"]
        a_raw = env["a_raw"]
        w = env["weight"]

        # clamp + transform
        a_c = clamp(a_raw, CLAMP_MIN, CLAMP_MAX)
        u = math.atanh(a_c)

        # alignment U/W
        U += w * u
        W += w
        a_out = math.tanh(U / max(W, EPS_W))

        # Quero lane (simple structural version)
        if prev_u is None:
            q_raw = a_out
        else:
            delta = (u - prev_u)
            q_raw = q_out_list[-1] + 0.08 * delta

        q_c = clamp(q_raw, CLAMP_MIN, CLAMP_MAX)

        seq_list.append(seq)
        a_out_list.append(a_out)
        q_out_list.append(q_c)

        prev_u = u

    return np.array(seq_list), np.array(a_out_list), np.array(q_out_list)


def main():
    print("\n=== SSM-TWEET — Heatmap Demo ===")

    with open("envelopes.json", "r") as f:
        envelopes = json.load(f)

    seq, a_out, q_out = compute_alignment_and_quero(envelopes)

    # Build a 2xN matrix where row0=a_out, row1=q_out
    heat_data = np.vstack([a_out, q_out])

    plt.figure(figsize=(14, 4))
    plt.imshow(
        heat_data,
        aspect="auto",
        cmap="coolwarm",
        interpolation="nearest",
        extent=[min(seq), max(seq), 0, 2]
    )

    plt.colorbar(label="Value intensity (-1 to +1)")
    plt.title("SSM-TWEET Heatmap — Alignment (row 0) + Quero (row 1)")
    plt.xlabel("sequence_number")
    plt.ylabel("lane index (0 = alignment, 1 = quero)")

    # Optional: gridlines
    plt.hlines([1], xmin=min(seq), xmax=max(seq), colors="black", linewidth=1)

    print("Rendering heatmap...")
    plt.tight_layout()
    plt.show()
    print("Done — heatmap plotted.\n")

if __name__ == "__main__":
    main()
