

## Overview

This framework processes microarray gene expression datasets through three stages:

| Stage | Description |
|-------|-------------|
| **Feature Selection** | Raw / mRMR (`mrmr_k50`, `mrmr_k75`) / Boruta |
| **Benchmark** | Model comparison — NB / KNN / SVM / RF / DT / XGBoost / ANN |
| **Interpretation** | SHAP + tree-based IF-THEN rule extraction |

SHAP is an explainability tool, not a stage: it is applied to the best benchmark
model, to the rule-extraction model, and on demand to any trained model (see
`run_shap`). It and the rule-extraction settings are configured in `configs/interpretation.yaml`.

There is no command-line entry point — `main.py` is an unused stub. Every flow
in this repo is driven from the notebooks under `notebooks/` (see "Quick Start"
below), which can also be run headlessly via `jupyter nbconvert --execute`.

---

## Dataset Format

All datasets use **CuMiDa format** — both original CuMiDa datasets and GEO datasets converted via `src/dataset_builder/builder.py`:

```
samples,  type,    probe_1, probe_2, ...
GSM001,   tumor,   4.32,    2.11,    ...
GSM002,   normal,  3.80,    1.95,    ...
```

Column 0 = sample ID, column 1 = class label, columns 2+ = expression values (float32).

Each dataset's platform (chip/array) is recorded in the `platform:` field of `configs/datasets.yaml`, used by `src/dataset_builder/annotation.py` to resolve probe → gene symbol mappings.

---

## Installation

This project uses [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

Key dependencies (see `pyproject.toml`):
```
numpy pandas scikit-learn xgboost
mrmr-selection          # mRMR feature selection
boruta                  # Boruta feature selection
torch lightning         # ANN model
shap                    # SHAP explanations
rich                    # clean console / notebook output
matplotlib seaborn umap-learn
mygene                  # optional: MyGene.info probe mapping
wandb                   # optional: experiment tracking
fastapi uvicorn         # backend API (src/api)
```

---

## Quick Start — Notebooks

There is no CLI — every flow is driven from a notebook. Minimal example (any notebook under `notebooks/`):

```python
import sys
sys.path.insert(0, '..')          # repo root

from src.pipeline import GeneExpressionPipeline

pipe = GeneExpressionPipeline(
    config_root='../configs',
    output_root='../outputs_baseline_full',
    use_wandb=False,
)
pipe.print_summary()

# CV/full-data baseline (auto-SHAP on the best combo) — no k-sweep, single run
pipe.run_benchmark(['GEO-Breast-20711'])

# k-sweep both baselines (see notebooks/02_Benchmark.ipynb §2 for the full cell)
K_VALUES = pipe.config_loader.load_feature_selection_config().get('rare_class_k_values', [2, 3, 4, 5, 6])
pipe.run_benchmark(['GEO-Breast-20711'], k_values=K_VALUES)          # -> outputs_baseline_full/k{N}/
pipe.run_baseline_split(['GEO-Breast-20711'], k_values=K_VALUES)     # -> outputs_baseline_split/k{N}/, all models

# Explain any other trained combo on demand
pipe.run_shap('GEO-Breast-20711', 'mrmr_k50', 'svm')

# Full-dataset tree-based rules (needs the single-run pipe.run_benchmark call above)
pipe.run_rule_extraction(['GEO-Breast-20711'])

# Rule extraction on a train/test split — needs outputs_baseline_split/k{N}/ to exist first
pipe.run_rule_extraction_holdout(['GEO-Breast-20711'], k_values=[3, 4, 5])
```

To run a notebook headlessly from a terminal:
```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/02_Benchmark.ipynb
```

---

## Run Modes

`02_Benchmark.ipynb`: set `RUN_MODE = "single"` (one dataset, `DATASET`) or
`"multiple"` (a list, `DATASETS`, or `None` = all enabled in `datasets.yaml`).
This selects which datasets both the single-run cell and the k-sweep section
operate on.

`run_interpretation_batch(select="best")` picks the highest balanced-accuracy `(fs_method, model, fold)`
from the benchmark results for each dataset; `select="fixed"` applies one explicit target to all.

---

## Feature Selection

Methods run **independently**, each producing its own reduced CSV. In the CV/full-data
baseline (`run_benchmark`) all four run; in the train/test-split baseline and
holdout rule extraction (`run_baseline_split` / `run_rule_extraction_holdout`)
only the last three run (no `raw`):

| Method | Description | Output |
|--------|-------------|--------|
| `raw` | All features (baseline) — CV/full baseline only | source pointer to original CSV (no copy) |
| `mrmr_k50` | mRMR MIQ criterion, top 50 features | `{dataset}_mrmr_k50_K50.csv` |
| `mrmr_k75` | mRMR MIQ criterion, top 75 features | `{dataset}_mrmr_k75_K75.csv` |
| `boruta` | Boruta, `selection_mode: "auto"` — confirmed if ≥50 confirmed features, else confirmed+tentative | `{dataset}_boruta_confirmed.csv` or `_confirmed_tentative.csv` |

Configure the mRMR K values, Boruta's `dynamic_threshold`, and the rare-class
sweep range (`rare_class_k_values`) in `configs/feature_selection.yaml`.

---

## Evaluation Metrics

Each CV fold reports:

| Metric | Description |
|--------|-------------|
| `accuracy` | Overall accuracy |
| `balanced_accuracy` | Accuracy adjusted for class imbalance |
| `f1` | Averaged F1 score (averaging strategy from the `average` param) |
| `f1_macro` | Always macro-averaged F1, regardless of `average` |
| `precision` | Averaged precision |
| `recall` | Averaged recall |
| `roc_auc` | One-vs-Rest AUC |
| `log_loss` | Cross-entropy loss |
| `per_class` | Unaggregated precision/recall/f1 per class (`average=None`) — kept out of flat CSV summaries, written to a separate `per_class_metrics.json` |

Adaptive cross-validation: `n_splits = min(5, smallest_class_count)` — prevents errors when a class has very few samples.

---

## Probe → Gene Annotation

Datasets use probe IDs as feature names (e.g. `1007_s_at`). The `platform:` field in `configs/datasets.yaml` records each dataset's chip platform. Passed to `src/dataset_builder/annotation.py`, it enables automatic GPL SOFT download and probe → gene symbol mapping:

```python
# Automatic GPL download (requires internet) — platform from datasets.yaml
pipe.run_interpretation(
    dataset_name='GEO-Breast-20711',
    fs_method='mrmr_k50',
    model_name='rf',
    platform='HG-U133_Plus_2',
)

# Local annotation file (highest priority)
pipe.run_interpretation(
    ...,
    annotation_path='path/to/GPL570.csv',
)
```

For Agilent datasets, MyGene.info is the recommended fallback annotation source (used automatically when a local annotation file/mapping isn't available).

---

## Outputs per Experiment

Three separate, `k{N}`-nested output roots plus one flat legacy root:

```
outputs_baseline_full/k{N}/{dataset}/{fs_method}/{model}/     <- run_benchmark(k_values=[...])
  cv_results.csv, cv_summary.csv, per_class_metrics.json, params_des.json, models/{model}_fold_N.joblib

outputs_baseline_split/k{N}/{dataset}/                        <- run_baseline_split(k_values=[...])
  split_info.json, feature_selection/{fs_method}/...
  {fs_method}/{model}/{metrics.json, per_class_metrics.json,
    models/{model}.joblib, models/repeats.csv, models/repeats_summary.csv, models/confusion_matrix_test.png}
  visualizations/all_datasets_class_distribution.png, all_datasets_metric_comparison.png

outputs_holdout/k{N}/{dataset}/{fs_method}/{rf,dt}/            <- run_rule_extraction_holdout(k_values=[...])
  models/{cv_results.csv, cv_summary.csv, best_run.json, best_run_train.json, best_run_per_class.json}
  rules/{rules.json, rules.csv, rules_human.txt, rules_summary.json, rules_test_eval.csv}

outputs/{dataset}/{fs_method}/                                 <- run_rule_extraction (no split, no k)
  {rf,dt}/rules/..., compare/crosscheck.json

outputs_live/<job_id>/                                          <- live UI "Huấn luyện lại" jobs
```

`k{N}` = the rare-class threshold (`min_samples_per_class`) that run produced results for — see `configs/feature_selection.yaml -> rare_class_k_values` and `configs/holdout.yaml -> holdout.batch.rare_class_k_values`.

---

## Adding a New Dataset

1. Place the CuMiDa-format CSV in `Dataset/Cumida/` (or `Dataset/GEO_Cumida/` for converted GEO data).
2. Add an entry in `configs/datasets.yaml`:
   ```yaml
   MyDataset:
     enabled: true
     path: "Dataset/Cumida/my_dataset/data.csv"
     type: "cumida"
     platform: "HG-U133_Plus_2"    # for annotation
     description: "My dataset description"
   ```
3. Run `pipe.run_benchmark(['MyDataset'])` (single run) or include it in a k-sweep call.

---

