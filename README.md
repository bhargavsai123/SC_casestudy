# GAAPO case study — deliverables (cleaned)

Soft Computing case study: reproducing Sécheresse et al. (2025), *GAAPO: genetic algorithm
applied to prompt optimization* (Frontiers in AI 8:1613007), correcting its reference
implementation, and testing the part of the method the paper leaves unjustified.

This repository has been cleaned for final submission. Removed: virtual environments,
build artifacts, old output versions, log files, and partial outputs.

## Code (root)

| File | What it is |
|---|---|
| `GAAPO_improved.ipynb` | The corrected, runnable implementation — the code deliverable |
| `run_sweep.py` | Main run + ablation |
| `run_adaptive.py` | Extension (credit-driven controller) |
| `run_probe.py` | Section 4.1 probe, resumable |
| `plot_probe.py` | Probe results plotting |

## Results — `content/gaapo_outputs_v2/`

| File / Directory | What it is |
|---|---|
| `case_study.md` | The report: audit, corrected run, probe, ablation, extension (16 pages) |
| `case_study_report.md` | Markdown report version |
| `case_study.typ` | Typst source (compiles to PDF) |
| `case_study_pdf.typ` | Typst source for PDF |
| `case_study.docx` | Editable report |
| `GAAPO_case_study.pdf` | PDF report |
| `GAAPO_case_study_slides.pptx` | 13-slide presentation with speaker notes |
| `candidate_log.csv` | Every candidate evaluation from the main run (116 rows, 102 distinct prompts) |
| `best_prompt.json` | Best evolved prompt configuration |
| `run_manifest.json` | Versions, models, seeds, split hashes, request counts |
| `ablation/` | Per-run tables, test predictions, paired statistical tests |
| `adaptive/` | Four arms × three repeats, weight trajectories, McNemar and bootstrap tables |
| `probe/` | Nine re-scored candidates, per-example outcomes, summary statistics |
| `figures/` | All report and slide figures (PNG) |

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

## Disclosed gap

The paper's §3.7 selection-method comparison (full evaluation vs successive halving vs bandit) is
implemented in `GAAPO_improved.ipynb` section 13 behind `RUN_SELECTION_COMPARISON` but was **not
run** — three further full runs did not fit the compute budget. This is stated in the report,
§9.