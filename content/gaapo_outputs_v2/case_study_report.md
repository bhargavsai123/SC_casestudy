# GAAPO case study — reproducibility audit and adaptive operator selection

_generated 2026-10-20T21:57:14+00:00_

- optimizer: `qwen2.5:7b`
- target: `qwen2.5:3b`
- seed: 42
- split: 50 train / 50 val / 200 test

## 1. Reproducibility audit

- stored main run: 116 logged candidates over 9 generations
- best validation in that run: **0.460** (generation 7, `apo`)

# GAAPO experiment report

_generated 2026-10-20T14:04:56+00:00 with optimizer `qwen2.5:7b` / target `qwen2.5:3b`_

## Headline

- baseline prompt (full validation): **0.100**
- best evolved prompt (full validation): **0.460** (generation 7, strategy `apo`)
- best evolved prompt (held-out test, n=200): **0.240** (macro-F1 0.600)
- baseline prompt (held-out test): **0.090**
- test delta: **+0.150**

Note on the test set: it is used here only to report generalisation. Configurations were compared on validation; the test number is not used for selection.

## Run configuration

```json
{
  "apo_error_source": "train",
  "strategy_allocation": "quota",
  "crossover_cleanup": true,
  "lenient_parsing": true,
  "max_generation_attempts": 3,
  "main": {
    "population": 20,
    "generations": 8,
    "eval_mode": "all"
  },
  "ablation": {
    "population": 10,
    "generations": 6,
    "eval_mode": "all",
    "repeats": 3,
    "single_strategy_baselines": false
  }
}
```

## Best prompt

```
[
    "Message: {input}. Consider the message for potential hate speech categories and ensure the prediction is accurate and concise, including only categories that apply:",
    "1. Does the message promote or incite violence? ['violence']",
    "2. Is the target of the message directed vs. generalized? ['directed_vs_generalized']",
    "3. Does the message involve gender? ['gender']",
    "4. Does the message involve race? ['race']",
    "5. Does the message involve national origin? ['national_origin']",
    "6. Does the message involve disability? ['disability']",
    "7. Does the message involve religion? ['religion']",
    "8. Does the message involve sexual orientation? ['sexual_orientation']",
    "Output the final result as a JSON array of category names."
]
```

## Validation score by generation

|   best_validation_score |
|------------------------:|
|                    0.1  |
|                    0.14 |
|                    0.3  |
|                    0.36 |
|                    0.34 |
|                    0.36 |
|                    0.42 |
|                    0.46 |
|                    0.46 |


## Validation score by strategy

|   n_candidates |   mean_val |   max_val |
|---------------:|-----------:|----------:|
|              8 |      0.285 |      0.38 |
|             15 |      0.27  |      0.46 |
|             49 |      0.233 |      0.44 |
|             13 |      0.203 |      0.36 |
|             16 |      0.184 |      0.32 |
|              1 |      0.1   |      0.1  |
|              1 |      0.1   |      0.1  |


## Parsing breakdown (candidate evaluations)

|                |   count |
|:---------------|--------:|
| json           |   37153 |
| keyword        |    1721 |
| json_substring |     637 |
| empty          |      25 |


## Leave-one-out ablation (mean +/- std over 3 repeat(s), paired seeds)

| config                  |   best_val_mean |   best_val_std |   test_mean |   test_std |   n_repeats |   delta_val_vs_full |   delta_test_vs_full |   paired_delta_test_mean |   paired_delta_test_std |
|:------------------------|----------------:|---------------:|------------:|-----------:|------------:|--------------------:|---------------------:|-------------------------:|------------------------:|
| full_hybrid             |           0.247 |          0.058 |       0.232 |      0.016 |           3 |                0    |                0     |                    0     |                   0     |
| without_opro            |           0.267 |          0.031 |       0.208 |      0.079 |           3 |                0.02 |               -0.023 |                   -0.023 |                   0.09  |
| without_apo             |           0.227 |          0.031 |       0.142 |      0.028 |           3 |               -0.02 |               -0.09  |                   -0.09  |                   0.043 |
| without_random_mutation |           0.187 |          0.061 |       0.127 |      0.053 |           3 |               -0.06 |               -0.105 |                   -0.105 |                   0.058 |


## Artifacts

- `candidate_log.csv`, `best_prompt.json`, `run_manifest.json`
- `figures/score_by_generation.png`, `figures/score_by_strategy.png`, `figures/improvement_vs_parent.png`, `figures/parse_methods.png`
- `ablation/ablation_runs.csv`, `ablation/ablation_summary.csv`

_Reminder: these numbers come from a local re-implementation with different models and a smaller budget than the paper. They are not comparable with the published tables, and no result in this file should be quoted as reproducing them._

## 2. Adaptive operator selection

Four allocation policies at equal LLM budget: fixed (paper weights), uniform, random (Dirichlet redrawn each generation), and adaptive (EWMA credit + softmax + exploration floor).

| arm      |   best_val_mean |   best_val_std |   test_mean |   test_std |   entropy_mean |   best_gen_mean |   n |   delta_val_vs_fixed |   delta_test_vs_fixed |
|:---------|----------------:|---------------:|------------:|-----------:|---------------:|----------------:|----:|---------------------:|----------------------:|
| adaptive |           0.347 |          0.042 |       0.293 |      0.049 |          0.963 |           5.667 |   3 |                0     |                 0.002 |
| fixed    |           0.347 |          0.042 |       0.292 |      0.028 |          0.914 |           5     |   3 |                0     |                 0     |
| uniform  |           0.333 |          0.042 |       0.262 |      0.043 |          1     |           5.333 |   3 |               -0.013 |                -0.03  |
| random   |           0.327 |          0.031 |       0.228 |      0.051 |          0.776 |           3     |   3 |               -0.02  |                -0.063 |

### Paired per-example comparison on the held-out test set

|   repeat | contrast            |   acc_adaptive |   acc_control |   diff |   ci_low |   ci_high |   b_adaptive_only |   c_control_only |   p_raw |   p_holm |
|---------:|:--------------------|---------------:|--------------:|-------:|---------:|----------:|------------------:|-----------------:|--------:|---------:|
|        0 | adaptive_vs_fixed   |           0.35 |         0.305 |  0.045 |   -0.01  |     0.1   |                21 |               12 |  0.1628 |   0.7579 |
|        0 | adaptive_vs_uniform |           0.35 |         0.27  |  0.08  |    0.015 |     0.145 |                31 |               15 |  0.0259 |   0.2072 |
|        0 | adaptive_vs_random  |           0.35 |         0.285 |  0.065 |    0.01  |     0.12  |                22 |                9 |  0.0294 |   0.2072 |
|        1 | adaptive_vs_fixed   |           0.27 |         0.31  | -0.04  |   -0.09  |     0.005 |                 8 |               16 |  0.1516 |   0.7579 |
|        1 | adaptive_vs_uniform |           0.27 |         0.3   | -0.03  |   -0.075 |     0.015 |                 7 |               13 |  0.2632 |   0.7579 |
|        1 | adaptive_vs_random  |           0.27 |         0.215 |  0.055 |    0.005 |     0.105 |                19 |                8 |  0.0522 |   0.3134 |
|        2 | adaptive_vs_fixed   |           0.26 |         0.26  |  0     |    0     |     0     |                 0 |                0 |  1      |   1      |
|        2 | adaptive_vs_uniform |           0.26 |         0.215 |  0.045 |   -0.01  |     0.1   |                21 |               12 |  0.1628 |   0.7579 |
|        2 | adaptive_vs_random  |           0.26 |         0.185 |  0.075 |    0.025 |     0.13  |                22 |                7 |  0.0081 |   0.0732 |

`b` = adaptive correct and control wrong; `c` = control correct and adaptive wrong; `p_holm` is the Holm-adjusted exact McNemar p-value; the CI is a paired bootstrap over the 200 test examples.

### Figures

- `figures/adaptive_weights.png` — learned weights over generations
- `figures/adaptive_entropy.png` — allocation diversity per arm
- `figures/adaptive_best_so_far.png` — sample efficiency

## 3. Limitations

- Small local models, 50-example validation: the credit signal is noisy and the study is underpowered for small effects.
- Three repeats are a stability check, not a power source; the primary inference is the paired per-example test.
- The test set is used for reporting, not for selecting the arm. Do not pick the best arm by test score and call it a finding.
- Absolute scores are not comparable with the published paper (different models, smaller budget).
