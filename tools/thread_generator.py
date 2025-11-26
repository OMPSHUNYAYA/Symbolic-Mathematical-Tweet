import json
import random
import argparse

# ------------------------------------------------------------
# SSM-TWEET THREAD GENERATOR (3 MODES)
# Synthetic • Conversational • Stress
# Deterministic structural envelope generator for testing.
#
# Fields generated:
#   sequence_number
#   a_raw ∈ (-1, +1)
#   weight > 0
#   thread_id (multi-thread capable)
#   band="NEUTRAL"
#   manifest_id="T1"
#   optional zeta_zero
#   optional quero_shock (structural coherence event)
#
# Run:
#   python thread_generator.py --mode synthetic --count 200
#   python thread_generator.py --mode conversational --branches 4 --depth 20
#   python thread_generator.py --mode stress --count 2000
#
# ------------------------------------------------------------


# ---------------------- Helpers ------------------------------

def rand_a_raw():
    """Generate a_raw with shaped distribution (mild turbulence)."""
    base = random.uniform(-0.8, 0.8)
    jitter = random.uniform(-0.2, 0.2)
    return max(-0.99, min(0.99, base + 0.5 * jitter))


def rand_weight():
    """Generate weight in a realistic operating range."""
    return round(random.uniform(0.5, 1.8), 2)


def maybe_zeta_zero(prob=0.05):
    """5% chance of a declared zero."""
    return random.random() < prob


def maybe_quero_shock(prob=0.05):
    """5% chance of a Quero structural anomaly event."""
    return random.random() < prob


# ---------------------- Generators ----------------------------


def generate_synthetic(count):
    """Pure synthetic envelopes with multi-thread noise."""
    threads = ["main", "chat", "updates", "system", "audit"]
    envelopes = []

    for seq in range(1, count + 1):
        t = random.choice(threads)
        env = {
            "sequence_number": seq,
            "a_raw": round(rand_a_raw(), 3),
            "weight": rand_weight(),
            "thread_id": t,
            "manifest_id": "T1",
            "band": "NEUTRAL"
        }

        if maybe_zeta_zero():
            env["zeta_zero"] = True

        if maybe_quero_shock():
            env["quero_shock"] = True

        envelopes.append(env)

    return envelopes


def generate_conversational(branches, depth):
    """
    Simulates a realistic conversation:
    - main thread
    - multiple subthreads
    - thread replies
    """
    envelopes = []
    seq = 1

    # root conversation
    for b in range(branches):
        thread_name = f"branch_{b+1}"
        for d in range(depth):
            env = {
                "sequence_number": seq,
                "a_raw": round(rand_a_raw(), 3),
                "weight": rand_weight(),
                "thread_id": thread_name,
                "manifest_id": "T1",
                "band": "NEUTRAL"
            }

            if maybe_zeta_zero(prob=0.03):
                env["zeta_zero"] = True

            if maybe_quero_shock(prob=0.04):
                env["quero_shock"] = True

            envelopes.append(env)
            seq += 1

    return envelopes


def generate_stress(count):
    """Heavy stress-test generator with dense structural variation."""
    envelopes = []

    threads = [f"t{i}" for i in range(1, 8)]
    for seq in range(1, count + 1):
        t = random.choice(threads)
        env = {
            "sequence_number": seq,
            "a_raw": round(rand_a_raw(), 3),
            "weight": round(random.uniform(0.7, 2.2), 2),
            "thread_id": t,
            "manifest_id": "T1",
            "band": "NEUTRAL"
        }

        # more turbulence during stress mode
        if maybe_zeta_zero(prob=0.07):
            env["zeta_zero"] = True

        if maybe_quero_shock(prob=0.1):
            env["quero_shock"] = True

        envelopes.append(env)

    return envelopes


# ---------------------- Main CLI ------------------------------

def main():
    parser = argparse.ArgumentParser(description="SSM-TWEET Thread Generator")
    parser.add_argument("--mode", type=str, required=True,
                        choices=["synthetic", "conversational", "stress"],
                        help="generation mode")
    parser.add_argument("--count", type=int, default=100,
                        help="number of envelopes (synthetic / stress)")
    parser.add_argument("--branches", type=int, default=3,
                        help="number of conversational branches")
    parser.add_argument("--depth", type=int, default=15,
                        help="depth per conversational branch")
    parser.add_argument("--save", type=str, default="generated_envelopes.json",
                        help="output file")

    args = parser.parse_args()

    random.seed(2025)  # deterministic across all machines

    if args.mode == "synthetic":
        env = generate_synthetic(args.count)
    elif args.mode == "conversational":
        env = generate_conversational(args.branches, args.depth)
    elif args.mode == "stress":
        env = generate_stress(args.count)
    else:
        raise ValueError("invalid mode")

    with open(args.save, "w") as f:
        json.dump(env, f, indent=4)

    print(f"\n=== SSM-TWEET Thread Generator ===")
    print(f"Mode       : {args.mode}")
    print(f"Generated  : {len(env)} envelopes")
    print(f"Saved to   : {args.save}")
    print(f"Deterministic seed = 2025\n")


if __name__ == "__main__":
    main()
