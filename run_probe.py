"""Post-hoc probe (minimal): does the validation score predict the test score?

Scores a handful of already-generated prompts (from candidate_log.csv, which
already carries their 50-example validation scores) on the 200-example held-out
test set. Resumable: every finished prompt is written immediately.

Run repeatedly; it stops after each prompt, so an interrupted session loses at
most one prompt.
"""
import json
import os
import sys
import time
import traceback
from pathlib import Path

ROOT = Path("/Users/bhargav/Downloads/SC")
os.chdir(ROOT)
os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import pandas as pd

NB = json.loads((ROOT / "GAAPO_improved.ipynb").read_text())
OUT = ROOT / "content/gaapo_outputs_v2/probe"
OUT.mkdir(parents=True, exist_ok=True)
CSV = OUT / "probe_runs.csv"

N_TOP = 7          # prompts from the top of the validation ranking
PER_RUN = 1        # score this many prompts per invocation, then exit


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main():
    ns = {"__name__": "__main__", "__file__": str(ROOT / "run_probe.py")}
    for idx, cell in enumerate(NB["cells"]):
        if idx > 21:
            break
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell["source"])
        if src.lstrip().startswith("%pip"):
            continue
        try:
            exec(compile(src, f"cell_{idx}", "exec"), ns)
        except Exception:
            log(f"cell {idx}: FAILED")
            print(traceback.format_exc(), flush=True)
            return 1
        if idx == 5:
            ns.update(RUN_SMOKE_TEST=False, RUN_MAIN_EXPERIMENT=False,
                      RUN_ABLATION=False, RUN_SELECTION_COMPARISON=False,
                      RUN_ADAPTIVE_STUDY=False)
            ns["MAX_CONCURRENT_REQUESTS"] = 8

    target = ns["target_client"]
    test_df = ns["test_df"]

    log_df = pd.read_csv(ROOT / "content/gaapo_outputs_v2/candidate_log.csv")
    log_df = log_df.drop_duplicates("prompt", keep="first").reset_index(drop=True)
    log_df = log_df.sort_values("validation_score", ascending=False).reset_index(drop=True)
    indices = list(range(min(N_TOP, len(log_df))))
    indices += [40, 70]   # two prompts from lower in the ranking, to span the range

    rows = []
    done = set()
    if CSV.exists():
        old = pd.read_csv(CSV)
        rows = old.to_dict("records")
        done = set(int(x) for x in old.prompt_id)

    todo = [i for i in indices if i not in done][:PER_RUN]
    log(f"{len(done)} done, {len(indices) - len(done)} left, scoring {len(todo)} now")
    if not todo:
        return summarise()

    for i in todo:
        r = log_df.iloc[i]
        t0 = time.time()
        res = ns["evaluate_on_examples"](str(r["prompt"]), test_df, target)
        correct = [int(p == g) for p, g in zip(res.predictions, res.golds)]
        rows.append({
            "prompt_id": i,
            "generation": int(r["generation"]),
            "strategy": str(r["strategy"]),
            "validation_score": float(r["validation_score"]),
            "validation_rank": i + 1,
            "test_score": float(res.score),
            "test_macro_f1": float(res.macro_f1),
            "pred_labels_mean": float(np.mean([len(p) for p in res.predictions])),
            "gold_labels_mean": float(np.mean([len(g) for g in res.golds])),
            "prompt": str(r["prompt"]),
            "test_correct": json.dumps(correct),
        })
        pd.DataFrame(rows).to_csv(CSV, index=False)
        log(f"prompt {i}: val={r['validation_score']:.2f} test={res.score:.3f} "
            f"({time.time() - t0:.0f}s)")

    return summarise(rows)


def summarise(rows=None):
    if rows is None:
        rows = pd.read_csv(CSV).to_dict("records")
    df = pd.DataFrame(rows)
    if len(df) < 3:
        log(f"only {len(df)} prompt(s); summary deferred")
        return 0

    from scipy.stats import kendalltau, pearsonr, spearmanr

    v = df.validation_score.values
    t = df.test_score.values
    rho, rho_p = spearmanr(v, t)
    tau, tau_p = kendalltau(v, t)
    pr, pr_p = pearsonr(v, t)

    leader = int(np.argmax(v))
    se = np.sqrt(v * (1 - v) / 50)
    within = np.flatnonzero(v >= v[leader] - 1.96 * se.max())

    summary = {
        "n_prompts": int(len(df)),
        "spearman_rho": float(rho),
        "spearman_p": float(rho_p),
        "kendall_tau": float(tau),
        "kendall_p": float(tau_p),
        "pearson_r": float(pr),
        "pearson_p": float(pr_p),
        "mean_val_minus_test": float((v - t).mean()),
        "median_val_minus_test": float(np.median(v - t)),
        "leader_by_validation": {
            "validation": float(v[leader]),
            "test": float(t[leader]),
            "n_prompts_with_higher_test": int((t > t[leader]).sum()),
            "best_test": float(t.max()),
            "strategy": str(df.strategy.iloc[leader]),
            "generation": int(df.generation.iloc[leader]),
        },
        "prompt_with_best_test": {
            "validation": float(v[int(np.argmax(t))]),
            "validation_rank": int(df.validation_rank.iloc[int(np.argmax(t))]),
            "test": float(t.max()),
            "strategy": str(df.strategy.iloc[int(np.argmax(t))]),
        },
        "n_within_noise_of_leader": int(len(within)),
        "within_noise_test_range": [float(t[within].min()), float(t[within].max())],
        "within_noise_validation_range": [float(v[within].min()), float(v[within].max())],
    }
    with open(OUT / "probe_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    log(json.dumps(summary, indent=2))
    df.drop(columns=["test_correct"]).to_json(OUT / "probe_runs.json", orient="records",
                                              indent=2)
    np.save(OUT / "test_correct.npy",
            np.array([json.loads(s) for s in df.test_correct]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
