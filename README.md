# GAAPO case study — deliverables

Soft Computing case study: reproducing Sécheresse et al. (2025), *GAAPO: genetic algorithm
applied to prompt optimization* (Frontiers in AI 8:1613007), correcting its reference
implementation, and testing the part of the method the paper leaves unjustified.

## Read these

| File | What it is |
|---|---|
| `GAAPO_case_study.pdf` | The report: audit, corrected run, probe, ablation, extension (16 pages) |
| `GAAPO_case_study.docx` | Same report, editable |
| `GAAPO_case_study_slides.pptx` | 13-slide presentation with speaker notes |
| `GAAPO_improved.ipynb` | The corrected, runnable implementation — the code deliverable |

The report exists in three forms: `content/gaapo_outputs_v2/case_study.md` (source),
`case_study.typ` (generated), and the `.pdf` / `.docx` built from it.

## What was done

1. **Audit** — 24 defects corrected against the paper, 6 of which change *what* is measured
   (duplicate merging, mismatched baseline evaluation set, broken successive halving, non-UCB-E
   bandit, unvalidated prompts, contaminated ablation).
2. **Corrected run** — ETHOS multilabel, 50/50/200 split, `qwen2.5:7b` writing prompts for
   `qwen2.5:3b`. Seed 0.09 → best evolved prompt 0.24 on held-out test (0.46 on validation).
3. **Probe (post-hoc)** — nine saved candidates re-scored on the test set: validation ranking
   does not carry over (Spearman ρ = 0.28, n.s.); seven prompts tie with the leader on
   validation and span 0.24–0.33 on test.
4. **Ablation** — first leave-one-out test of the five operators. Removing random mutation costs
   10.5 test points; OPRO's contribution is unresolved.
5. **Extension** — the fixed 40/20/20/10/10 weights replaced by a credit-driven controller, with
   fixed / uniform / random-allocation controls at equal budget. Null result, with a diagnosed
   mechanism (credit ±0.2 against τ = 0.5 ⇒ at most 1.5:1 odds) and a measured explanation
   (the selection signal itself is too noisy at this scale).

## Rebuilding

```bash
# report (needs pandoc + the typst Python package)
cd content/gaapo_outputs_v2
pandoc case_study.md -f markdown -t typst -o case_study.typ
../../.venv/bin/python -c "import typst; typst.compile('case_study_pdf.typ', output='GAAPO_case_study.pdf')"
pandoc case_study.md -o case_study.docx --resource-path=.:figures

# presentation (from the repository root)
cd ../..
.venv/bin/python build_slides.py        # reads probe/probe_summary.json
.venv/bin/python preview_slides.py      # PNG previews in /tmp/slide_preview
```

## Artifacts

`content/gaapo_outputs_v2/`

- `candidate_log.csv` — every candidate evaluation from the main run (116 rows, 102 distinct prompts)
- `run_manifest.json` — versions, models, seeds, split hashes, request counts
- `ablation/` — per-run table, per-example test predictions, paired tests
- `adaptive/` — four arms × three repeats, weight trajectories, McNemar and bootstrap tables
- `probe/` — the nine re-scored candidates, per-example outcomes, summary statistics
- `figures/` — report and slide figures

Scripts at the repository root: `run_sweep.py` (main run + ablation), `run_adaptive.py`
(extension), `run_probe.py` (section 4.1 probe, resumable, one prompt per invocation),
`plot_probe.py`, `plot_slide_chart.py`, `build_slides.py`, `preview_slides.py` (rough PNG preview
of the deck, for checking layout without PowerPoint).

## Disclosed gap

The paper's §3.7 selection-method comparison (full evaluation vs successive halving vs bandit) is
implemented in `GAAPO_improved.ipynb` section 13 behind `RUN_SELECTION_COMPARISON` but was **not
run** — three further full runs did not fit the compute budget. This is stated in the report,
§9.
