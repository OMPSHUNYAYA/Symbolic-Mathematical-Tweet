import json
import math
import hashlib

# ------------------------------------------------------------
# SSM-TWEET : ADVANCED POC (FULL STRUCTURAL + THREAD + Q-LANE)
# Deterministic | Structural | Non-semantic | No ML
#
# Demonstrates:
#   • Strict ordering (replay determinism)
#   • Clamp-first safety
#   • Alignment kernel (U/W → tanh)
#   • Quero lane (q_raw → clamp → q_out)
#   • Multi-thread structural fusion
#   • Optional ZETA-0 stability events
#   • Tamper-visible hash chaining
#
# Canonical envelope example (Overlay Mode):
# {
#   "sequence_number": 1,
#   "a_raw": 0.32,
#   "weight": 1.0,
#   "thread_id": "main"
# }
#
# Expected partial output:
# seq=1 | thr=main | a_raw=+0.100 | w=1.0 | a_out=+0.100000
# ------------------------------------------------------------

EPS_A = 1e-6
EPS_W = 1e-9
CLAMP_MIN = -1 + EPS_A
CLAMP_MAX = +1 - EPS_A

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def compute_hash(payload: str) -> str:
    """12-char truncated SHA256 for structural tamper visibility."""
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]

# ------------------------------------------------------------
# NEW: Quero lane update helper
# ------------------------------------------------------------
def update_quero(previous_q, a_c, prev_a_c):
    """
    Structural coherence metric:
    q_raw = posture_delta (smooth if small, shock if large)
    q_out = clamp(q_raw)
    """
    delta = a_c - prev_a_c
    q_raw = delta
    q_c = clamp(q_raw, CLAMP_MIN, CLAMP_MAX)
    return q_c


# ------------------------------------------------------------
# UPDATED: Alignment + Quero + ZETA-0 engine
# ------------------------------------------------------------
def alignment_kernel(envelopes):
    """
    Core SSM-Tweet structural engine.
    Returns:
        global_trace : evolving global alignment + Quero
        threads      : dict of per-thread posture + Quero
        hash_chain   : tamper-visible structural hashes
    """

    # ---------- GLOBAL containers ----------
    U_global = 0.0
    W_global = 0.0
    prev_a_global = 0.0
    prev_q_global = 0.0
    global_trace = []

    # ---------- THREAD containers ----------
    threads = {}  # thread_id -> {U, W, prev_a, prev_q, trace}

    # ---------- HASH chain ----------
    prev_hash = "0" * 12
    hash_chain = []

    for env in envelopes:
        seq = env["sequence_number"]

        # Manifest-safe defaults
        a_raw = env.get("a_raw", 0.0)
        w = env.get("weight", 1.0)
        thread = env.get("thread_id", "main")

        # ZETA-0 detection (optional)
        is_z0 = (a_raw == 0.0 and w == 0.0)

        # Clamp posture
        a_c = clamp(a_raw, CLAMP_MIN, CLAMP_MAX)
        u = math.atanh(a_c)

        # ---------- THREAD INIT ----------
        if thread not in threads:
            threads[thread] = {
                "U": 0.0,
                "W": 0.0,
                "prev_a": 0.0,
                "prev_q": 0.0,
                "trace": []
            }

        # ---------- ZETA-0 update ----------
        if is_z0:
            # Neutral posture, weight only increases stability
            threads[thread]["W"] += abs(w)
            W_global += abs(w)
        else:
            # ALIGNMENT updates
            threads[thread]["U"] += w * u
            threads[thread]["W"] += w
            U_global += w * u
            W_global += w

        # ---------- THREAD a_out ----------
        a_out_thread = math.tanh(
            threads[thread]["U"] / max(threads[thread]["W"], EPS_W)
        )

        # ---------- GLOBAL a_out ----------
        a_out_global = math.tanh(U_global / max(W_global, EPS_W))

        # ---------- THREAD Quero lane ----------
        q_thread = update_quero(
            previous_q=threads[thread]["prev_q"],
            a_c=a_out_thread,
            prev_a_c=threads[thread]["prev_a"]
        )

        # ---------- GLOBAL Quero lane ----------
        q_global = update_quero(
            previous_q=prev_q_global,
            a_c=a_out_global,
            prev_a_c=prev_a_global
        )

        # ---------- Save traces ----------
        global_trace.append({
            "seq": seq,
            "thread": thread,
            "a_raw": a_raw,
            "w": w,
            "a_out": round(a_out_global, 6),
            "q_out": round(q_global, 6)
        })

        threads[thread]["trace"].append({
            "seq": seq,
            "a_raw": a_raw,
            "w": w,
            "a_out": round(a_out_thread, 6),
            "q_out": round(q_thread, 6)
        })

        # Update previous values
        prev_a_global = a_out_global
        prev_q_global = q_global

        threads[thread]["prev_a"] = a_out_thread
        threads[thread]["prev_q"] = q_thread

        # ---------- HASH CHAIN ----------
        payload = f"{seq}|{a_raw}|{w}|{thread}|{prev_hash}"
        new_hash = compute_hash(payload)
        hash_chain.append({"seq": seq, "hash": new_hash})
        prev_hash = new_hash

    return global_trace, threads, hash_chain


# ------------------------------------------------------------
# Envelope loader
# ------------------------------------------------------------
def load_envelopes():
    """Loads and sorts envelopes by declared sequence_number."""
    with open("envelopes.json", "r") as f:
        data = json.load(f)
    return sorted(data, key=lambda x: x["sequence_number"])


# ------------------------------------------------------------
# Ordering integrity checker
# ------------------------------------------------------------
def check_replay_consistency(envelopes):
    seqs = [env["sequence_number"] for env in envelopes]
    if seqs != sorted(seqs):
        print("\n*** WARNING: Replay inconsistency detected ***")
        print("Envelopes arrived out of order; engine sorted deterministically.\n")
    else:
        print("Replay integrity: OK (strictly ordered)")


# ------------------------------------------------------------
# Scoreboard printer
# ------------------------------------------------------------
def print_scoreboard(global_trace, threads):
    final_global = global_trace[-1]["a_out"]
    final_q_global = global_trace[-1]["q_out"]

    print("\n--- SCOREBOARD SUMMARY ----------------------------------")
    print(f"Total envelopes processed  : {len(global_trace)}")
    print(f"Total threads detected     : {len(threads)}")
    print(f"Final GLOBAL a_out         : {final_global:+.6f}")
    print(f"Final GLOBAL q_out         : {final_q_global:+.6f}")

    for tname, tdata in threads.items():
        last_a = tdata["trace"][-1]["a_out"]
        last_q = tdata["trace"][-1]["q_out"]
        print(f"Thread '{tname}' final a_out : {last_a:+.6f} | q_out: {last_q:+.6f}")
    print("----------------------------------------------------------\n")


# ------------------------------------------------------------
# MAIN EXECUTION
# ------------------------------------------------------------
def main():
    print("\n=== ADVANCED SSM-TWEET POC (STRUCTURAL + Q-LANE DEMO) ===")

    envelopes = load_envelopes()
    print(f"\nLoaded {len(envelopes)} envelopes")

    check_replay_consistency(envelopes)

    global_trace, threads, hash_chain = alignment_kernel(envelopes)

    print("\n--- GLOBAL ALIGNMENT + QUERO TRACE -----------------------")
    for r in global_trace:
        print(
            f"seq={r['seq']:<4} | "
            f"thr={r['thread']:<6} | "
            f"a_raw={r['a_raw']:+.3f} | "
            f"w={r['w']:.1f} | "
            f"a_out={r['a_out']:+.6f} | "
            f"q_out={r['q_out']:+.6f}"
        )

    print_scoreboard(global_trace, threads)

    print("--- HASH CHAIN (Structural Integrity) --------------------")
    for h in hash_chain:
        print(f"seq={h['seq']:<4} | hash={h['hash']}")
    print("----------------------------------------------------------")

    print("\nReplay complete — deterministic, multi-thread structural lanes generated.")
    print("No semantics. No categories. No ML. Pure structural mathematics.\n")


if __name__ == "__main__":
    main()
