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