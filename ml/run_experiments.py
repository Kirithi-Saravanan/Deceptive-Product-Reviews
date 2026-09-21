"""
Phase 3B experiment runner — ReviewGuard AI
===========================================
Methodology
-----------
1.  Train all candidate models on the training split only.
2.  For every probability-capable candidate sweep thresholds [0.30 … 0.70] on
    the *validation* split and record per-threshold metrics.
    LinearSVC candidates (decision_function only) are evaluated once at their
    default hard boundary.
3.  Per candidate, pick the threshold that maximises validation Macro F1
    (ties broken by validation deceptive-class F1).  That score is the
    candidate's representative score for the final comparison.
4.  Select the overall winner by the same primary/secondary criteria.
5.  Lock: model, TF-IDF config, class-prior config, threshold.
6.  Load test.csv ONCE, evaluate the locked configuration, report all metrics.
7.  Retrain locked config on Train+Validation and export production artefacts.

The test set is never loaded or referenced until Step 6.
"""

import os
import sys
import json
import time
import joblib

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from model_pipeline import build_text_pipeline, build_combined_pipeline, get_classifier


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

THRESHOLD_SWEEP = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]


# ---------------------------------------------------------------------------
# Candidate definitions
# ---------------------------------------------------------------------------

def build_candidates(X_train, X_val):
    """
    Returns a list of candidate dicts.  Each dict describes one experiment
    configuration; it does NOT train anything yet.

    Probability-based candidates support predict_proba and will be threshold-
    swept.  LinearSVC candidates use their hard decision boundary.
    """
    candidates = [
        # ── Logistic Regression ──────────────────────────────────────────
        {
            'name': 'Word TF-IDF + LogisticRegression',
            'tfidf_config': {'analyzer': 'word', 'ngram_range': (1, 2),
                             'max_features': 5000, 'min_df': 5, 'sublinear_tf': True},
            'class_prior_config': None,
            'pipeline_func': build_text_pipeline,
            'pipeline_kwargs': {'classifier': get_classifier('LogisticRegression'),
                                'vectorizer_type': 'word'},
            'X_train': X_train['review_text'],
            'X_val':   X_val['review_text'],
        },

        # ── MultinomialNB variants (all required) ─────────────────────────
        {
            'name': 'Word TF-IDF + MultinomialNB (default prior)',
            'tfidf_config': {'analyzer': 'word', 'ngram_range': (1, 2),
                             'max_features': 5000, 'min_df': 5, 'sublinear_tf': True},
            'class_prior_config': {'fit_prior': True, 'class_prior': None},
            'pipeline_func': build_text_pipeline,
            'pipeline_kwargs': {'classifier': get_classifier('MultinomialNB',
                                                             fit_prior=True,
                                                             class_prior=None),
                                'vectorizer_type': 'word'},
            'X_train': X_train['review_text'],
            'X_val':   X_val['review_text'],
        },
        {
            'name': 'Word TF-IDF + MultinomialNB (uniform prior)',
            'tfidf_config': {'analyzer': 'word', 'ngram_range': (1, 2),
                             'max_features': 5000, 'min_df': 5, 'sublinear_tf': True},
            'class_prior_config': {'fit_prior': False, 'class_prior': None},
            'pipeline_func': build_text_pipeline,
            'pipeline_kwargs': {'classifier': get_classifier('MultinomialNB',
                                                             fit_prior=False,
                                                             class_prior=None),
                                'vectorizer_type': 'word'},
            'X_train': X_train['review_text'],
            'X_val':   X_val['review_text'],
        },
        {
            'name': 'Word TF-IDF + MultinomialNB (prior=[0.3, 0.7])',
            'tfidf_config': {'analyzer': 'word', 'ngram_range': (1, 2),
                             'max_features': 5000, 'min_df': 5, 'sublinear_tf': True},
            'class_prior_config': {'fit_prior': False, 'class_prior': [0.3, 0.7]},
            'pipeline_func': build_text_pipeline,
            'pipeline_kwargs': {'classifier': get_classifier('MultinomialNB',
                                                             fit_prior=False,
                                                             class_prior=[0.3, 0.7]),
                                'vectorizer_type': 'word'},
            'X_train': X_train['review_text'],
            'X_val':   X_val['review_text'],
        },
        {
            'name': 'Word TF-IDF + MultinomialNB (prior=[0.4, 0.6])',
            'tfidf_config': {'analyzer': 'word', 'ngram_range': (1, 2),
                             'max_features': 5000, 'min_df': 5, 'sublinear_tf': True},
            'class_prior_config': {'fit_prior': False, 'class_prior': [0.4, 0.6]},
            'pipeline_func': build_text_pipeline,
            'pipeline_kwargs': {'classifier': get_classifier('MultinomialNB',
                                                             fit_prior=False,
                                                             class_prior=[0.4, 0.6]),
                                'vectorizer_type': 'word'},
            'X_train': X_train['review_text'],
            'X_val':   X_val['review_text'],
        },

        # ── ComplementNB (additional only — does not replace MNB) ─────────
        {
            'name': 'Word TF-IDF + ComplementNB',
            'tfidf_config': {'analyzer': 'word', 'ngram_range': (1, 2),
                             'max_features': 5000, 'min_df': 5, 'sublinear_tf': True},
            'class_prior_config': None,
            'pipeline_func': build_text_pipeline,
            'pipeline_kwargs': {'classifier': get_classifier('ComplementNB'),
                                'vectorizer_type': 'word'},
            'X_train': X_train['review_text'],
            'X_val':   X_val['review_text'],
        },

        # ── LinearSVC (hard boundary — no threshold sweep) ────────────────
        {
            'name': 'Word TF-IDF + LinearSVC',
            'tfidf_config': {'analyzer': 'word', 'ngram_range': (1, 2),
                             'max_features': 5000, 'min_df': 5, 'sublinear_tf': True},
            'class_prior_config': None,
            'pipeline_func': build_text_pipeline,
            'pipeline_kwargs': {'classifier': get_classifier('LinearSVC'),
                                'vectorizer_type': 'word'},
            'X_train': X_train['review_text'],
            'X_val':   X_val['review_text'],
        },
        {
            'name': 'Char TF-IDF + LinearSVC',
            'tfidf_config': {'analyzer': 'char', 'ngram_range': (3, 5),
                             'max_features': 5000, 'min_df': 5, 'sublinear_tf': True},
            'class_prior_config': None,
            'pipeline_func': build_text_pipeline,
            'pipeline_kwargs': {'classifier': get_classifier('LinearSVC'),
                                'vectorizer_type': 'char',
                                'ngram_range': (3, 5)},
            'X_train': X_train['review_text'],
            'X_val':   X_val['review_text'],
        },

        # ── Combined features (DataFrame input) ───────────────────────────
        {
            'name': 'Combined Features + LogisticRegression',
            'tfidf_config': {'analyzer': 'word', 'ngram_range': (1, 2),
                             'max_features': 5000, 'min_df': 5, 'sublinear_tf': True},
            'class_prior_config': None,
            'pipeline_func': build_combined_pipeline,
            'pipeline_kwargs': {'classifier': get_classifier('LogisticRegression')},
            'X_train': X_train,
            'X_val':   X_val,
        },
    ]
    return candidates


# ---------------------------------------------------------------------------
# Per-threshold metric computation (validation set only)
# ---------------------------------------------------------------------------

def _metrics_at_threshold(y_true, y_prob, threshold: float) -> dict:
    """
    Apply a probability threshold, return a full metric dict.
    y_prob is the probability of the positive (deceptive) class.
    """
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        'accuracy':         accuracy_score(y_true, y_pred),
        'prec_deceptive':   precision_score(y_true, y_pred, zero_division=0),
        'recall_deceptive': recall_score(y_true, y_pred, zero_division=0),
        'f1_deceptive':     f1_score(y_true, y_pred, zero_division=0),
        'prec_genuine':     precision_score(y_true, y_pred, pos_label=0, zero_division=0),
        'recall_genuine':   recall_score(y_true, y_pred, pos_label=0, zero_division=0),
        'f1_genuine':       f1_score(y_true, y_pred, pos_label=0, zero_division=0),
        'f1_macro':         f1_score(y_true, y_pred, average='macro', zero_division=0),
        'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp),
    }


def run_threshold_sweep(pipeline, X_val, y_val, candidate_name: str) -> list:
    """
    Sweep THRESHOLD_SWEEP values on the validation set.
    Returns a list of row-dicts (one per threshold) suitable for a DataFrame.
    Also returns the best threshold and its f1_macro / f1_deceptive.
    """
    y_prob = pipeline.predict_proba(X_val)[:, 1]  # P(deceptive)
    rows = []
    for thr in THRESHOLD_SWEEP:
        m = _metrics_at_threshold(y_val, y_prob, thr)
        rows.append({'candidate': candidate_name, 'threshold': thr, **m})
    return rows


def _hard_boundary_metrics(pipeline, X_val, y_val, candidate_name: str) -> list:
    """
    For models without predict_proba (e.g. LinearSVC).
    Returns a single row with threshold='default'.
    """
    y_pred = pipeline.predict(X_val)
    tn, fp, fn, tp = confusion_matrix(y_val, y_pred, labels=[0, 1]).ravel()
    row = {
        'candidate':        candidate_name,
        'threshold':        'default',
        'accuracy':         accuracy_score(y_val, y_pred),
        'prec_deceptive':   precision_score(y_val, y_pred, zero_division=0),
        'recall_deceptive': recall_score(y_val, y_pred, zero_division=0),
        'f1_deceptive':     f1_score(y_val, y_pred, zero_division=0),
        'prec_genuine':     precision_score(y_val, y_pred, pos_label=0, zero_division=0),
        'recall_genuine':   recall_score(y_val, y_pred, pos_label=0, zero_division=0),
        'f1_genuine':       f1_score(y_val, y_pred, pos_label=0, zero_division=0),
        'f1_macro':         f1_score(y_val, y_pred, average='macro', zero_division=0),
        'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp),
    }
    return [row]


# ---------------------------------------------------------------------------
# Final model selection from sweep results
# ---------------------------------------------------------------------------

def select_best_candidate(all_sweep_rows: list, trained_candidates: list) -> dict:
    """
    For each candidate find its best validation Macro F1 across thresholds.
    Select the overall winner:  primary = best f1_macro, secondary = f1_deceptive.

    Returns a dict describing the locked configuration.
    """
    df = pd.DataFrame(all_sweep_rows)

    # Per-candidate best row (numeric thresholds only; 'default' is already
    # the unique row for LinearSVC candidates so it is included naturally).
    best_rows = []
    for cname, grp in df.groupby('candidate'):
        # Sort: primary f1_macro desc, secondary f1_deceptive desc
        best = grp.sort_values(
            ['f1_macro', 'f1_deceptive'], ascending=[False, False]
        ).iloc[0]
        best_rows.append(best)

    best_df = pd.DataFrame(best_rows).sort_values(
        ['f1_macro', 'f1_deceptive'], ascending=[False, False]
    )

    winner_row  = best_df.iloc[0]
    winner_name = winner_row['candidate']
    winner_thr  = winner_row['threshold']

    # Locate the matching trained candidate dict
    winner_candidate = next(c for c in trained_candidates if c['name'] == winner_name)

    print(f"\n{'='*60}")
    print(f"  CONFIGURATION LOCKED")
    print(f"{'='*60}")
    print(f"  Model     : {winner_name}")
    print(f"  Threshold : {winner_thr}")
    print(f"  Val Macro F1   : {winner_row['f1_macro']:.4f}")
    print(f"  Val Decept F1  : {winner_row['f1_deceptive']:.4f}")
    print(f"{'='*60}\n")

    return {
        'candidate':    winner_candidate,
        'threshold':    winner_thr,
        'val_metrics':  winner_row.to_dict(),
    }


# ---------------------------------------------------------------------------
# Final test evaluation (called exactly once, after config is locked)
# ---------------------------------------------------------------------------

def final_test_evaluation(pipeline, X_test, y_test, threshold) -> dict:
    """
    Evaluate the locked pipeline on the held-out test set.
    threshold is a float for probabilistic models or 'default' for LinearSVC.
    """
    if hasattr(pipeline, 'predict_proba') and threshold != 'default':
        y_prob = pipeline.predict_proba(X_test)[:, 1]
        y_pred = (y_prob >= float(threshold)).astype(int)
        roc_auc = float(roc_auc_score(y_test, y_prob))
    else:
        y_pred  = pipeline.predict(X_test)
        y_prob  = None
        try:
            y_score = pipeline.decision_function(X_test)
            roc_auc = float(roc_auc_score(y_test, y_score))
        except Exception:
            roc_auc = None

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    return {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'deceptive': {
            'precision': float(precision_score(y_test, y_pred, zero_division=0)),
            'recall':    float(recall_score(y_test, y_pred, zero_division=0)),
            'f1':        float(f1_score(y_test, y_pred, zero_division=0)),
        },
        'genuine': {
            'precision': float(precision_score(y_test, y_pred, pos_label=0, zero_division=0)),
            'recall':    float(recall_score(y_test, y_pred, pos_label=0, zero_division=0)),
            'f1':        float(f1_score(y_test, y_pred, pos_label=0, zero_division=0)),
        },
        'f1_macro':           float(f1_score(y_test, y_pred, average='macro', zero_division=0)),
        'roc_auc':            roc_auc,
        'false_positive_rate': float(fpr),
        'false_negative_rate': float(fnr),
        'confusion_matrix':   [[int(tn), int(fp)], [int(fn), int(tp)]],
    }


# ---------------------------------------------------------------------------
# Production model export (Train + Val, NO test data)
# ---------------------------------------------------------------------------

def export_production_model(winner_candidate: dict, train_df: pd.DataFrame,
                             val_df: pd.DataFrame) -> object:
    """
    Retrain the locked configuration on Train + Validation.
    Returns the fitted production pipeline.
    """
    combined_df = pd.concat([train_df, val_df], ignore_index=True)
    y_combined  = combined_df['target']

    is_combined = 'Combined' in winner_candidate['name']
    X_combined  = combined_df if is_combined else combined_df['review_text']

    prod_pipeline = winner_candidate['pipeline_func'](**winner_candidate['pipeline_kwargs'])
    prod_pipeline.fit(X_combined, y_combined)
    return prod_pipeline


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def run_all_experiments():
    print("Loading Train and Validation splits (test.csv is NOT loaded yet)...")
    train_df = pd.read_csv('ml/data/train.csv')
    val_df   = pd.read_csv('ml/data/validation.csv')

    y_train = train_df['target']
    y_val   = val_df['target']

    candidates = build_candidates(train_df, val_df)

    all_sweep_rows    = []   # Accumulates every threshold × candidate row
    trained_candidates = []  # Candidates enriched with their fitted pipeline

    # ── Step 1 + 2: Train each candidate; sweep thresholds on val ────────
    for cand in candidates:
        print(f"\n[Training] {cand['name']}")
        pipeline = cand['pipeline_func'](**cand['pipeline_kwargs'])

        t0 = time.time()
        pipeline.fit(cand['X_train'], y_train)
        elapsed = time.time() - t0
        print(f"  Trained in {elapsed:.2f}s")

        if hasattr(pipeline, 'predict_proba'):
            rows = run_threshold_sweep(pipeline, cand['X_val'], y_val, cand['name'])
            best_row = max(rows, key=lambda r: (r['f1_macro'], r['f1_deceptive']))
            print(f"  Best val threshold: {best_row['threshold']:.2f} "
                  f"-> Macro F1={best_row['f1_macro']:.4f}, "
                  f"Deceptive F1={best_row['f1_deceptive']:.4f}")
        else:
            rows = _hard_boundary_metrics(pipeline, cand['X_val'], y_val, cand['name'])
            best_row = rows[0]
            print(f"  Hard boundary (no predict_proba) "
                  f"-> Macro F1={best_row['f1_macro']:.4f}, "
                  f"Deceptive F1={best_row['f1_deceptive']:.4f}")

        all_sweep_rows.extend(rows)
        trained_candidates.append({**cand, 'pipeline': pipeline})

    # ── Step 3: Select overall winner by best-threshold val metrics ───────
    locked = select_best_candidate(all_sweep_rows, trained_candidates)
    locked_candidate  = locked['candidate']
    locked_threshold  = locked['threshold']
    locked_val        = locked['val_metrics']

    # Write threshold_analysis.csv (all candidates × all thresholds)
    os.makedirs('ml/results', exist_ok=True)
    sweep_df = pd.DataFrame(all_sweep_rows)
    sweep_df.to_csv('ml/results/threshold_analysis.csv', index=False)
    print("Saved: ml/results/threshold_analysis.csv")

    # ── Step 4: Load test set ONCE — after config is locked ──────────────
    print("\nLoading test set (configuration is locked — this is the only test access)...")
    test_df = pd.read_csv('ml/data/test.csv')
    y_test  = test_df['target']
    is_combined_winner = 'Combined' in locked_candidate['name']
    X_test  = test_df if is_combined_winner else test_df['review_text']

    test_metrics = final_test_evaluation(
        locked_candidate['pipeline'], X_test, y_test, locked_threshold
    )

    print("\n── Final Test Metrics ──────────────────────────────────────────")
    print(f"  Accuracy     : {test_metrics['accuracy']:.4f}")
    print(f"  Macro F1     : {test_metrics['f1_macro']:.4f}")
    print(f"  Deceptive    : P={test_metrics['deceptive']['precision']:.4f} "
          f"R={test_metrics['deceptive']['recall']:.4f} "
          f"F1={test_metrics['deceptive']['f1']:.4f}")
    print(f"  Genuine      : P={test_metrics['genuine']['precision']:.4f} "
          f"R={test_metrics['genuine']['recall']:.4f} "
          f"F1={test_metrics['genuine']['f1']:.4f}")
    if test_metrics['roc_auc'] is not None:
        print(f"  ROC-AUC      : {test_metrics['roc_auc']:.4f}")
    print(f"  FPR          : {test_metrics['false_positive_rate']:.4f}  "
          f"(genuine reviews misclassified as deceptive)")
    print(f"  FNR          : {test_metrics['false_negative_rate']:.4f}  "
          f"(deceptive reviews missed)")
    cm = test_metrics['confusion_matrix']
    print(f"  Confusion    : TN={cm[0][0]}  FP={cm[0][1]}  "
          f"FN={cm[1][0]}  TP={cm[1][1]}")
    print("────────────────────────────────────────────────────────────────")

    with open('ml/results/final_metrics.json', 'w') as f:
        json.dump(test_metrics, f, indent=4)
    print("Saved: ml/results/final_metrics.json")

    # ── Step 5: Export production model (Train + Val, no test) ───────────
    print("\nRetraining locked config on Train + Validation for production...")
    prod_pipeline = export_production_model(locked_candidate, train_df, val_df)

    os.makedirs('ml/models', exist_ok=True)
    joblib.dump(prod_pipeline, 'ml/models/model.joblib')
    print("Saved: ml/models/model.joblib")

    # Build class_prior_config — normalise to JSON-serialisable types
    raw_cp = locked_candidate.get('class_prior_config')
    if raw_cp is not None:
        class_prior_config = {
            'fit_prior':   raw_cp.get('fit_prior', True),
            'class_prior': (list(raw_cp['class_prior'])
                            if raw_cp.get('class_prior') is not None else None),
        }
    else:
        class_prior_config = None

    # Normalise threshold for JSON (float or string 'default')
    json_threshold = float(locked_threshold) if locked_threshold != 'default' else 'default'

    metadata = {
        'selected_model':      locked_candidate['name'],
        'tfidf_config':        {
            k: (list(v) if isinstance(v, tuple) else v)
            for k, v in locked_candidate['tfidf_config'].items()
        },
        'class_prior_config':  class_prior_config,
        'selected_threshold':  json_threshold,
        'validation_metrics': {
            'accuracy':     locked_val.get('accuracy'),
            'f1_macro':     locked_val.get('f1_macro'),
            'f1_deceptive': locked_val.get('f1_deceptive'),
            'f1_genuine':   locked_val.get('f1_genuine'),
            'threshold':    json_threshold,
        },
        'final_test_metrics':  test_metrics,
        'train_size':          len(train_df),
        'val_size':            len(val_df),
        'test_size':           len(test_df),
        'features': ('review_text, review_rating, number_of_helpful, number_of_photos'
                     if is_combined_winner else 'review_text'),
    }

    with open('ml/models/model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)
    print("Saved: ml/models/model_metadata.json")
    print("\nPhase 3B complete.")


if __name__ == '__main__':
    run_all_experiments()

