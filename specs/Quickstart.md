# SSM-TWEET — Quickstart Guide
**Deterministic • Structural • Non-Semantic • No ML**

---

## **1. Requirements**

You only need:

- Python **3.8+**
- Standard library only
- No ML, no NLP, no GPU

Check Python:

``python --version``

---

## **2. Folder Structure**

Your folder should look like:

```
/TWEET
    run_demo.py
    envelopes.json
    quero_graph_demo.py
    heatmap_alignment_quero.py
    thread_generator.py
    README.md
    Quickstart.md   ← this file  
```

Everything runs from this directory.

---

## **3. Run the Minimal Demo**

Run the deterministic replay:

``python run_demo.py``

You will see:

- deterministic replay  
- alignment output (**a_out**)  
- quero output (**q_out**)  
- tamper-evident hash chain  
- per-thread summaries  

Replay is identical every time.

---

## **4. Modify the Demo**

Edit **envelopes.json** to test behaviors:

- change `a_raw`
- adjust `weight`
- reorder `sequence_number`
- add/remove `thread_id`

Add a reset event:

``"zeta_zero": true``

Replay:

``python run_demo.py``

Always deterministic.

---

## **5. Generate Quero + Alignment Graphs**

Plot symbolic drift:

``python quero_graph_demo.py``

Outputs:

- alignment lane  
- quero lane  

Use a custom file:

``python quero_graph_demo.py --file envelopes.json``

---

## **6. Generate Heatmap (Alignment + Quero)**

``python heatmap_alignment_quero.py``

Produces:

- Row 0 → alignment  
- Row 1 → quero  

---

## **7. Generate Synthetic Threads**

Random drift dataset:

``python thread_generator.py --mode synthetic --count 200 --save synth_200.json``

Conversational branches:

``python thread_generator.py --mode conversational --branches 4 --depth 30 --save convo_4x30.json``

Stress test:

``python thread_generator.py --mode stress --count 2000 --save stress_2000.json``

These files can be visualised using any graph tool.

---

## **8. Visualise Generated Data**

``python quero_graph_demo.py --file synth_200.json``
``python heatmap_alignment_quero.py --file stress_2000.json``

---

## **9. No Semantics. No ML. Pure Structure.**

Engine uses only:

- `clamp`
- `atanh`
- weighted fusion (`w * u`)
- `tanh`
- quero deltas
- declared envelopes
- U/W accumulation (`U += w*u`, `a_out = tanh(U/W)`)

Guarantees:

- platform-neutral behavior  
- deterministic replay  
- transparent posture lanes  
- drift-aware multi-thread memory  

---

## **10. Files Included**

| File | Purpose |
|------|---------|
| `run_demo.py` | Deterministic replay engine |
| `envelopes.json` | Sample dataset |
| `thread_generator.py` | Synthetic / stress generation |
| `quero_graph_demo.py` | Alignment/Quero plots |
| `heatmap_alignment_quero.py` | Heatmap visualisation |
| `README.md` | High-level summary |
| `Quickstart.md` | This guide |

---

## **11. Next Steps**

You can now:

- build envelopes  
- test structural drift  
- simulate branches  
- apply ZETA-0  
- integrate into messaging systems  

Everything is deterministic and reproducible.


