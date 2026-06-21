"""Generate notebooks/model_evaluation.ipynb as a proper .ipynb JSON file."""
import json, os, textwrap
from pathlib import Path

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11.0"
        }
    },
    "cells": []
}

def md(source):
    nb["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [textwrap.dedent(source)]
    })

def code(source):
    nb["cells"].append({
        "cell_type": "code",
        "metadata": {},
        "source": [textwrap.dedent(source)],
        "outputs": [],
        "execution_count": None
    })

# ===== CELL 1: Title =====
md("""
# Model Evaluation — M.I.N.D CDSS
## 12 Modelos (4 Objetivos × 3 Algoritmos) — Avaliação Temporal

**Objetivos:** `diagnosis` (multiclasse, 20 classes), `relapse` (binário), `suicide_risk` (binário), `therapeutic_response` (binário)

**Algoritmos:** Logistic Regression, Random Forest, XGBoost

**Split Temporal:** Dados ordenados por `consultation_date`; treino = 80% mais antigos, teste = 20% mais recentes.
Isto evita data leakage e reflete o cenário clínico real (modelo treinado no passado prevê o futuro).

> ⚠️ **Aviso Importante:** Todos os modelos foram treinados em **dados sintéticos** gerados por
> `scripts/seed_clinical_data.py`. As métricas abaixo são **ilustrativas de capacidade metodológica**,
> não de performance clínica real. Consulte a seção de Limitações ao final.
""")

# ===== CELL 2: Imports =====
code("""
import os, sys, json, warnings, tempfile
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import joblib

from sklearn.metrics import (
    roc_curve, auc, precision_recall_curve, average_precision_score,
    f1_score, precision_score, recall_score, accuracy_score,
    classification_report, confusion_matrix, ConfusionMatrixDisplay,
    brier_score_loss, roc_auc_score
)
from sklearn.preprocessing import LabelEncoder, label_binarize
from sklearn.calibration import calibration_curve
from sklearn.model_selection import train_test_split

import mlflow
from mlflow.tracking import MlflowClient

warnings.filterwarnings('ignore')
sns.set_style('whitegrid')
mpl.rcParams['figure.dpi'] = 120
mpl.rcParams['figure.figsize'] = (10, 6)

print('OK — imports carregados')
""")

# ===== CELL 3: Config =====
code("""
# ── Paths ──────────────────────────────────────────────
PROJECT_ROOT = Path.cwd()
MLFLOW_URI = f"sqlite:///{PROJECT_ROOT / 'mlflow.db'}"

# ── DB connection ──────────────────────────────────────
from app.core.config import settings
from sqlalchemy import create_engine, text

# ── ML pipeline modules ────────────────────────────────
from app.ml.training.feature_engineering import build_feature_matrix
from app.ml.training.label_builder import LABEL_BUILDERS, TARGET_COLUMNS, KNOWN_DISORDERS
from app.ml.training.estimators import ESTIMATORS

# ── MLflow ─────────────────────────────────────────────
mlflow.set_tracking_uri(MLFLOW_URI)
client = MlflowClient()

OBJECTIVES = ['diagnosis', 'relapse', 'suicide_risk', 'therapeutic_response']
ALGORITHMS = ['logistic_regression', 'random_forest', 'xgboost']
ALGO_LABELS = {'logistic_regression': 'Logistic Regression',
               'random_forest': 'Random Forest',
               'xgboost': 'XGBoost'}
ALGO_COLORS = {'logistic_regression': '#4C72B0',
               'random_forest': '#DD8452',
               'xgboost': '#55A868'}

TRAIN_SPLIT_DATE = None  # will be set after loading data

print('Config OK')
print(f'MLflow: {MLFLOW_URI}')
""")

# ===== CELL 4: Load feature matrix =====
code("""
print('Conectando ao banco de dados...')
engine = create_engine(settings.database_url)

# Test connection
with engine.connect() as conn:
    result = conn.execute(text('SELECT count(*) FROM clinical.clinical_consultation'))
    n_consults = result.scalar()
    print(f'Consultas disponíveis: {n_consults}')

# Extract feature matrix (already sorted by patient_uuid, consultation_date)
df, feature_cols = build_feature_matrix(engine)
print(f'Feature matrix: {df.shape[0]} rows × {df.shape[1]} cols')
print(f'Feature columns used: {len(feature_cols)}')
print(f'Date range: {df["consultation_date"].min()} to {df["consultation_date"].max()}')

# ── Temporal split ─────────────────────────────────────
df_sorted = df.sort_values('consultation_date').reset_index(drop=True)
split_idx = int(len(df_sorted) * 0.8)
split_date = df_sorted.loc[split_idx, 'consultation_date']

df_train = df_sorted[df_sorted['consultation_date'] <= split_date].copy()
df_test  = df_sorted[df_sorted['consultation_date'] >  split_date].copy()

TRAIN_SPLIT_DATE = split_date

print(f'\\nSplit temporal: treino até {split_date.date()} ({len(df_train)} amostras), '
      f'teste após ({len(df_test)} amostras)')
print(f'  Proporção: treino={len(df_train)/len(df_sorted):.1%}, '
      f'teste={len(df_test)/len(df_sorted):.1%}')
""")

# ===== CELL 5: Evaluation function definitions =====
code("""
# ═══════════════════════════════════════════════════════
#  HELPERS — Evaluation & Plotting
# ═══════════════════════════════════════════════════════

def load_production_model(objective, algorithm):
    \"\"\"Load the production model artifact from MLflow registry.\"\"\"
    from app.ml.registry.model_registry import ModelRegistry
    registry = ModelRegistry(engine)
    mv = registry.get_production_model(objective, algorithm)
    if mv is None:
        print(f'  ⚠ Sem production model para {objective}_{algorithm}')
        return None, None, None
    local_path = mlflow.artifacts.download_artifacts(
        run_id=mv.mlflow_run_id,
        artifact_path=mv.artifact_path
    )
    artifact = joblib.load(local_path)
    model = artifact['model']
    le = artifact.get('label_encoder')
    feats = artifact.get('feature_cols', [])
    return model, le, feats


def prepare_data(df, objective, feature_cols):
    \"\"\"Build labels and prepare X/y for evaluation.\"\"\"
    label_builder = LABEL_BUILDERS[objective]
    target_col = TARGET_COLUMNS[objective]

    df_labeled = label_builder(df)
    df_labeled = df_labeled.dropna(subset=[target_col])

    # Align feature columns to what the model expects
    available = [c for c in feature_cols if c in df_labeled.columns]
    X = df_labeled[available].fillna(0).values
    y_raw = df_labeled[target_col].values

    return X, y_raw, df_labeled


def evaluate_binary(y_true, y_pred, y_proba, model_name):
    \"\"\"Compute binary metrics.\"\"\"
    f1 = f1_score(y_true, y_pred, zero_division=0)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    acc = accuracy_score(y_true, y_pred)
    try:
        roc_auc = roc_auc_score(y_true, y_proba)
    except Exception:
        roc_auc = float('nan')
    try:
        brier = brier_score_loss(y_true, y_proba)
    except Exception:
        brier = float('nan')
    return {'accuracy': round(acc, 4), 'precision': round(prec, 4),
            'recall': round(rec, 4), 'f1': round(f1, 4),
            'roc_auc': round(roc_auc, 4), 'brier': round(brier, 4)}


def evaluate_multiclass(y_true, y_pred, y_proba, classes):
    \"\"\"Compute multiclass metrics.\"\"\"
    f1_macro = f1_score(y_true, y_pred, average='macro', zero_division=0)
    f1_weighted = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    acc = accuracy_score(y_true, y_pred)

    # One-vs-rest ROC AUC
    n_classes = len(classes)
    y_true_bin = label_binarize(y_true, classes=range(n_classes))
    roc_aucs = {}
    for i in range(n_classes):
        try:
            roc_aucs[classes[i]] = round(roc_auc_score(y_true_bin[:, i], y_proba[:, i]), 4)
        except Exception:
            roc_aucs[classes[i]] = float('nan')

    return {'accuracy': round(acc, 4), 'f1_macro': round(f1_macro, 4),
            'f1_weighted': round(f1_weighted, 4), 'roc_auc_per_class': roc_aucs}


def plot_roc_curve(y_true, y_proba_dict, ax, title='ROC Curve'):
    \"\"\"Plot ROC curves for one or more models (binary).\"\"\"
    for label, y_proba in y_proba_dict.items():
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, lw=2, label=f'{label} (AUC={roc_auc:.3f})',
                color=ALGO_COLORS.get(label.split(' ')[0].lower()[:8], None))
    ax.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title(title)
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)


def plot_pr_curve(y_true, y_proba_dict, ax, title='Precision-Recall Curve'):
    \"\"\"Plot PR curves for one or more models (binary).\"\"\"
    for label, y_proba in y_proba_dict.items():
        precision, recall, _ = precision_recall_curve(y_true, y_proba)
        ap = average_precision_score(y_true, y_proba)
        ax.plot(recall, precision, lw=2, label=f'{label} (AP={ap:.3f})',
                color=ALGO_COLORS.get(label.split(' ')[0].lower()[:8], None))
    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_title(title)
    ax.legend(loc='lower left')
    ax.grid(True, alpha=0.3)


def plot_calibration(y_true, y_proba_dict, ax, title='Calibration Plot'):
    \"\"\"Plot calibration curves.\"\"\"
    for label, y_proba in y_proba_dict.items():
        prob_true, prob_pred = calibration_curve(y_true, y_proba, n_bins=10, strategy='uniform')
        ax.plot(prob_pred, prob_true, 'o-', lw=2, label=label,
                color=ALGO_COLORS.get(label.split(' ')[0].lower()[:8], None))
    ax.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5, label='Perfeita calibração')
    ax.set_xlabel('Probabilidade prevista média')
    ax.set_ylabel('Fração de positivos observados')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_title(title)
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)


def plot_multiclass_roc(y_true, y_proba_dict, classes, ax, title='ROC Curve (One-vs-Rest)'):
    \"\"\"Plot multiclass ROC for one model.\"\"\"
    y_true_bin = label_binarize(y_true, classes=range(len(classes)))
    for model_label, y_proba in y_proba_dict.items():
        for i, cls_name in enumerate(classes):
            fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_proba[:, i])
            roc_auc = auc(fpr, tpr)
            ax.plot(fpr, tpr, lw=1.5, label=f'{cls_name} (AUC={roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title(title)
    ax.legend(loc='lower right', fontsize=8)
    ax.grid(True, alpha=0.3)


def plot_confusion_matrix(y_true, y_pred, ax, title='Confusion Matrix', labels=None):
    \"\"\"Plot confusion matrix.\"\"\"
    cm = confusion_matrix(y_true, y_pred)
    disp = ConfusionMatrixDisplay(cm, display_labels=labels)
    disp.plot(ax=ax, cmap='Blues', colorbar=False, values_format='d')
    ax.set_title(title)


print('Helper functions defined OK')
""")

# ===== CELL 6: Diagnosis — Evaluation =====
code("""
# ═══════════════════════════════════════════════════════
#  OBJETIVO 1: DIAGNOSIS (multiclasse, 20 classes)
# ═══════════════════════════════════════════════════════

print('═' * 60)
print('OBJETIVO: diagnosis')
print('═' * 60)

diagnosis_models = {}
diagnosis_results = {}

for algo in ALGORITHMS:
    print(f'\\n--- {ALGO_LABELS[algo]} ---')
    model, le, feats = load_production_model('diagnosis', algo)
    if model is None:
        print(f'  ⚠ Pulando — modelo não encontrado')
        continue

    # Use training data features; align test data
    X_test, y_raw_test, _ = prepare_data(df_test, 'diagnosis', feats)
    y_test = le.transform(y_raw_test)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    # Align label encoder with model output
    classes = le.classes_.tolist()

    metrics = evaluate_multiclass(y_test, y_pred, y_proba, classes)
    diagnosis_models[algo] = {
        'model': model, 'le': le, 'feats': feats,
        'X_test': X_test, 'y_test': y_test, 'y_pred': y_pred, 'y_proba': y_proba,
        'y_raw': y_raw_test, 'classes': classes, 'metrics': metrics
    }
    diagnosis_results[algo] = metrics
    print(f'  accuracy={metrics["accuracy"]}, f1_macro={metrics["f1_macro"]}, '
          f'f1_weighted={metrics["f1_weighted"]}')

# ── Summary table ──
print('\\n\\n📊 Diagnosis — Summary per algorithm:')
summary_rows = []
for algo, m in diagnosis_results.items():
    roc_aucs = m.get('roc_auc_per_class', {})
    mean_auc = np.mean([v for v in roc_aucs.values() if not np.isnan(v)]) if roc_aucs else float('nan')
    summary_rows.append({
        'Algorithm': ALGO_LABELS[algo],
        'Accuracy': m['accuracy'],
        'F1 (macro)': m['f1_macro'],
        'F1 (weighted)': m['f1_weighted'],
        'Mean AUC (OvR)': round(mean_auc, 4)
    })
print(pd.DataFrame(summary_rows).to_string(index=False))
""")

# ===== CELL 7: Diagnosis — Plots =====
code("""
# ── Diagnosis — Plots ──
if diagnosis_models:
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Diagnosis — Multiclass Evaluation', fontsize=14, fontweight='bold')

    # Use the first available model for the confusion matrix
    first_algo = list(diagnosis_models.keys())[0]
    dm = diagnosis_models[first_algo]

    # Confusion Matrix (top-5 classes for readability)
    y_true = dm['y_test']
    y_pred = dm['y_pred']
    classes = dm['classes']

    # Only show classes that appear in test set
    present = sorted(set(y_true) | set(y_pred))
    present_labels = [classes[i] for i in present]

    # If too many classes, show top 8 most frequent
    if len(present_labels) > 8:
        class_counts = pd.Series(y_true).value_counts().head(8).index.tolist()
        mask = np.isin(y_true, class_counts) & np.isin(y_pred, class_counts)
        cm_subset = confusion_matrix(
            np.array(y_true)[mask], np.array(y_pred)[mask],
            labels=class_counts
        )
        disp = ConfusionMatrixDisplay(cm_subset, display_labels=[classes[i][:20] for i in class_counts])
        disp.plot(ax=axes[0, 0], cmap='Blues', colorbar=False, values_format='d')
        axes[0, 0].set_title(f'Confusion Matrix ({first_algo}) — Top-8 classes')
    else:
        plot_confusion_matrix(y_true, y_pred, axes[0, 0],
                              title=f'Confusion Matrix ({first_algo})',
                              labels=[c[:25] for c in present_labels])

    # ROC curves (OvR) for the first model
    y_true_bin = label_binarize(dm['y_test'], classes=range(len(classes)))
    for i, cls_name in enumerate(classes[:8]):  # Plot first 8 classes
        if i < len(classes):
            fpr, tpr, _ = roc_curve(y_true_bin[:, i], dm['y_proba'][:, i])
            roc_auc = auc(fpr, tpr)
            axes[0, 1].plot(fpr, tpr, lw=1.5, label=f'{cls_name[:20]} (AUC={roc_auc:.3f})')
    axes[0, 1].plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5)
    axes[0, 1].set_xlim([0.0, 1.0])
    axes[0, 1].set_ylim([0.0, 1.05])
    axes[0, 1].set_xlabel('False Positive Rate')
    axes[0, 1].set_ylabel('True Positive Rate')
    axes[0, 1].set_title(f'ROC Curves OvR ({first_algo}) — Top-8 classes')
    axes[0, 1].legend(loc='lower right', fontsize=7)
    axes[0, 1].grid(True, alpha=0.3)

    # F1 per class (top-10) bar chart for all algorithms
    f1_data = {}
    for algo, dm in diagnosis_models.items():
        report = classification_report(dm['y_test'], dm['y_pred'],
                                       output_dict=True, zero_division=0)
        f1_data[ALGO_LABELS[algo]] = {
            classes[int(k)]: v['f1-score']
            for k, v in report.items() if k.isdigit()
        }

    # Get top-10 classes by support
    all_classes_sorted = sorted(
        set().union(*[set(d.keys()) for d in f1_data.values()]),
        key=lambda c: -sum(d.get(c, 0) for d in f1_data.values())
    )[:10]

    x = np.arange(len(all_classes_sorted))
    width = 0.25
    for i, (algo_label, f1_scores) in enumerate(f1_data.items()):
        vals = [f1_scores.get(c, 0) for c in all_classes_sorted]
        axes[1, 0].bar(x + i * width, vals, width, label=algo_label,
                       color=list(ALGO_COLORS.values())[i], alpha=0.8)
    axes[1, 0].set_xlabel('Classe')
    axes[1, 0].set_ylabel('F1-Score')
    axes[1, 0].set_title('F1 per Class — Top-10 classes (comparação)')
    axes[1, 0].set_xticks(x + width)
    axes[1, 0].set_xticklabels([c[:18] for c in all_classes_sorted], rotation=45, ha='right', fontsize=8)
    axes[1, 0].legend(fontsize=8)
    axes[1, 0].set_ylim([0, 1.05])
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    # Metrics comparison bar chart
    metrics_df = pd.DataFrame(diagnosis_results).T
    metrics_to_plot = ['accuracy', 'f1_macro', 'f1_weighted']
    x2 = np.arange(len(metrics_to_plot))
    width2 = 0.25
    for i, algo in enumerate(ALGORITHMS):
        if algo in diagnosis_results:
            vals = [diagnosis_results[algo][m] for m in metrics_to_plot]
            axes[1, 1].bar(x2 + i * width2, vals, width2, label=ALGO_LABELS[algo],
                           color=list(ALGO_COLORS.values())[i], alpha=0.8)
    axes[1, 1].set_xlabel('Métrica')
    axes[1, 1].set_ylabel('Score')
    axes[1, 1].set_title('Métricas Agregadas — Comparação entre Algoritmos')
    axes[1, 1].set_xticks(x2 + width2)
    axes[1, 1].set_xticklabels(metrics_to_plot)
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].set_ylim([0, 1.05])
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.show()
else:
    print('Nenhum modelo de diagnosis disponível para plotagem.')
""")

# ===== CELL 8: Relapse — Evaluation =====
code("""
# ═══════════════════════════════════════════════════════
#  OBJETIVO 2: RELAPSE (binário)
# ═══════════════════════════════════════════════════════

print('═' * 60)
print('OBJETIVO: relapse')
print('═' * 60)

relapse_models = {}
relapse_results = {}

for algo in ALGORITHMS:
    print(f'\\n--- {ALGO_LABELS[algo]} ---')
    model, le, feats = load_production_model('relapse', algo)
    if model is None:
        print(f'  ⚠ Pulando — modelo não encontrado')
        continue

    X_test, y_raw_test, _ = prepare_data(df_test, 'relapse', feats)
    y_test = le.transform(y_raw_test)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = evaluate_binary(y_test, y_pred, y_proba, algo)
    relapse_models[algo] = {
        'model': model, 'le': le, 'feats': feats,
        'X_test': X_test, 'y_test': y_test, 'y_pred': y_pred, 'y_proba': y_proba,
        'y_raw': y_raw_test, 'metrics': metrics
    }
    relapse_results[algo] = metrics
    print(f'  {metrics}')

# ── Summary table ──
print('\\n\\n📊 Relapse — Summary per algorithm:')
print(pd.DataFrame(relapse_results).T.to_string())
""")

# ===== CELL 9: Relapse — Plots =====
code("""
# ── Relapse — Plots ──
if relapse_models:
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Relapse — Binary Classification Evaluation', fontsize=14, fontweight='bold')

    # ROC Curves
    roc_probas = {ALGO_LABELS[algo]: dm['y_proba'] for algo, dm in relapse_models.items()}
    plot_roc_curve(relapse_models[list(relapse_models.keys())[0]]['y_test'],
                   roc_probas, axes[0, 0], 'ROC Curve — Comparação')

    # PR Curves
    plot_pr_curve(relapse_models[list(relapse_models.keys())[0]]['y_test'],
                  roc_probas, axes[0, 1], 'Precision-Recall Curve — Comparação')

    # Calibration
    plot_calibration(relapse_models[list(relapse_models.keys())[0]]['y_test'],
                     roc_probas, axes[0, 2], 'Calibration Plot — Comparação')

    # Confusion Matrices (one per algorithm)
    for i, (algo, dm) in enumerate(relapse_models.items()):
        if i < 3:
            classes = dm['le'].classes_.tolist()
            plot_confusion_matrix(dm['y_test'], dm['y_pred'], axes[1, i],
                                  title=f'Confusion Matrix — {ALGO_LABELS[algo]}',
                                  labels=classes)

    plt.tight_layout()
    plt.show()

    # ── Metrics comparison bar chart ──
    fig, ax = plt.subplots(figsize=(10, 5))
    metrics_df = pd.DataFrame(relapse_results).T
    metrics_to_plot = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
    x = np.arange(len(metrics_to_plot))
    width = 0.25
    for i, algo in enumerate(ALGORITHMS):
        if algo in relapse_results:
            vals = [relapse_results[algo][m] for m in metrics_to_plot]
            ax.bar(x + i * width, vals, width, label=ALGO_LABELS[algo],
                   color=list(ALGO_COLORS.values())[i], alpha=0.8)
    ax.set_xlabel('Métrica')
    ax.set_ylabel('Score')
    ax.set_title('Relapse — Métricas por Algoritmo')
    ax.set_xticks(x + width)
    ax.set_xticklabels(metrics_to_plot)
    ax.legend()
    ax.set_ylim([0, 1.05])
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.show()

    # ── Brier Score comparison ──
    print('\\n📊 Brier Score (menor = melhor calibração):')
    for algo, m in relapse_results.items():
        print(f'  {ALGO_LABELS[algo]:25s}  Brier={m["brier"]:.4f}')
else:
    print('Nenhum modelo de relapse disponível para plotagem.')
""")

# ===== CELL 10: Suicide Risk — Evaluation =====
code("""
# ═══════════════════════════════════════════════════════
#  OBJETIVO 3: SUICIDE_RISK (binário)
# ═══════════════════════════════════════════════════════

print('═' * 60)
print('OBJETIVO: suicide_risk')
print('═' * 60)

suicide_models = {}
suicide_results = {}

for algo in ALGORITHMS:
    print(f'\\n--- {ALGO_LABELS[algo]} ---')
    model, le, feats = load_production_model('suicide_risk', algo)
    if model is None:
        print(f'  ⚠ Pulando — modelo não encontrado')
        continue

    X_test, y_raw_test, _ = prepare_data(df_test, 'suicide_risk', feats)
    y_test = le.transform(y_raw_test)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = evaluate_binary(y_test, y_pred, y_proba, algo)
    suicide_models[algo] = {
        'model': model, 'le': le, 'feats': feats,
        'X_test': X_test, 'y_test': y_test, 'y_pred': y_pred, 'y_proba': y_proba,
        'y_raw': y_raw_test, 'metrics': metrics
    }
    suicide_results[algo] = metrics
    print(f'  {metrics}')

# ── Summary table ──
print('\\n\\n📊 Suicide Risk — Summary per algorithm:')
print(pd.DataFrame(suicide_results).T.to_string())
""")

# ===== CELL 11: Suicide Risk — Plots =====
code("""
# ── Suicide Risk — Plots ──
if suicide_models:
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Suicide Risk — Binary Classification Evaluation', fontsize=14, fontweight='bold')

    roc_probas = {ALGO_LABELS[algo]: dm['y_proba'] for algo, dm in suicide_models.items()}
    y_test = suicide_models[list(suicide_models.keys())[0]]['y_test']

    plot_roc_curve(y_test, roc_probas, axes[0, 0], 'ROC Curve — Comparação')
    plot_pr_curve(y_test, roc_probas, axes[0, 1], 'Precision-Recall Curve — Comparação')
    plot_calibration(y_test, roc_probas, axes[0, 2], 'Calibration Plot — Comparação')

    for i, (algo, dm) in enumerate(suicide_models.items()):
        if i < 3:
            classes = dm['le'].classes_.tolist()
            plot_confusion_matrix(dm['y_test'], dm['y_pred'], axes[1, i],
                                  title=f'Confusion Matrix — {ALGO_LABELS[algo]}',
                                  labels=classes)

    plt.tight_layout()
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 5))
    metrics_df = pd.DataFrame(suicide_results).T
    metrics_to_plot = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
    x = np.arange(len(metrics_to_plot))
    width = 0.25
    for i, algo in enumerate(ALGORITHMS):
        if algo in suicide_results:
            vals = [suicide_results[algo][m] for m in metrics_to_plot]
            ax.bar(x + i * width, vals, width, label=ALGO_LABELS[algo],
                   color=list(ALGO_COLORS.values())[i], alpha=0.8)
    ax.set_xlabel('Métrica')
    ax.set_ylabel('Score')
    ax.set_title('Suicide Risk — Métricas por Algoritmo')
    ax.set_xticks(x + width)
    ax.set_xticklabels(metrics_to_plot)
    ax.legend()
    ax.set_ylim([0, 1.05])
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.show()
else:
    print('Nenhum modelo de suicide_risk disponível para plotagem.')
""")

# ===== CELL 12: Therapeutic Response — Evaluation =====
code("""
# ═══════════════════════════════════════════════════════
#  OBJETIVO 4: THERAPEUTIC_RESPONSE (binário)
# ═══════════════════════════════════════════════════════

print('═' * 60)
print('OBJETIVO: therapeutic_response')
print('═' * 60)

therapy_models = {}
therapy_results = {}

for algo in ALGORITHMS:
    print(f'\\n--- {ALGO_LABELS[algo]} ---')
    model, le, feats = load_production_model('therapeutic_response', algo)
    if model is None:
        print(f'  ⚠ Pulando — modelo não encontrado')
        continue

    X_test, y_raw_test, _ = prepare_data(df_test, 'therapeutic_response', feats)
    y_test = le.transform(y_raw_test)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = evaluate_binary(y_test, y_pred, y_proba, algo)
    therapy_models[algo] = {
        'model': model, 'le': le, 'feats': feats,
        'X_test': X_test, 'y_test': y_test, 'y_pred': y_pred, 'y_proba': y_proba,
        'y_raw': y_raw_test, 'metrics': metrics
    }
    therapy_results[algo] = metrics
    print(f'  {metrics}')

# ── Summary table ──
print('\\n\\n📊 Therapeutic Response — Summary per algorithm:')
print(pd.DataFrame(therapy_results).T.to_string())
""")

# ===== CELL 13: Therapeutic Response — Plots =====
code("""
# ── Therapeutic Response — Plots ──
if therapy_models:
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Therapeutic Response — Binary Classification Evaluation', fontsize=14, fontweight='bold')

    roc_probas = {ALGO_LABELS[algo]: dm['y_proba'] for algo, dm in therapy_models.items()}
    y_test = therapy_models[list(therapy_models.keys())[0]]['y_test']

    plot_roc_curve(y_test, roc_probas, axes[0, 0], 'ROC Curve — Comparação')
    plot_pr_curve(y_test, roc_probas, axes[0, 1], 'Precision-Recall Curve — Comparação')
    plot_calibration(y_test, roc_probas, axes[0, 2], 'Calibration Plot — Comparação')

    for i, (algo, dm) in enumerate(therapy_models.items()):
        if i < 3:
            classes = dm['le'].classes_.tolist()
            plot_confusion_matrix(dm['y_test'], dm['y_pred'], axes[1, i],
                                  title=f'Confusion Matrix — {ALGO_LABELS[algo]}',
                                  labels=classes)

    plt.tight_layout()
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 5))
    metrics_df = pd.DataFrame(therapy_results).T
    metrics_to_plot = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
    x = np.arange(len(metrics_to_plot))
    width = 0.25
    for i, algo in enumerate(ALGORITHMS):
        if algo in therapy_results:
            vals = [therapy_results[algo][m] for m in metrics_to_plot]
            ax.bar(x + i * width, vals, width, label=ALGO_LABELS[algo],
                   color=list(ALGO_COLORS.values())[i], alpha=0.8)
    ax.set_xlabel('Métrica')
    ax.set_ylabel('Score')
    ax.set_title('Therapeutic Response — Métricas por Algoritmo')
    ax.set_xticks(x + width)
    ax.set_xticklabels(metrics_to_plot)
    ax.legend()
    ax.set_ylim([0, 1.05])
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.show()
else:
    print('Nenhum modelo de therapeutic_response disponível para plotagem.')
""")

# ===== CELL 14: Cross-objective leaderboard =====
code("""
# ═══════════════════════════════════════════════════════
#  LEADERBOARD — Cross-Objective & Cross-Algorithm
# ═══════════════════════════════════════════════════════

print('═' * 80)
print('LEADERBOARD — Todos os 12 Modelos')
print('═' * 80)

all_results = []

for obj in OBJECTIVES:
    results_map = {
        'diagnosis': diagnosis_results,
        'relapse': relapse_results,
        'suicide_risk': suicide_results,
        'therapeutic_response': therapy_results,
    }.get(obj, {})

    for algo in ALGORITHMS:
        if algo in results_map:
            m = results_map[algo]
            if obj == 'diagnosis':
                roc_aucs = m.get('roc_auc_per_class', {})
                mean_auc = round(np.mean([v for v in roc_aucs.values()
                                          if not np.isnan(v)]), 4) if roc_aucs else float('nan')
                all_results.append({
                    'Objective': obj,
                    'Algorithm': ALGO_LABELS[algo],
                    'Accuracy': m['accuracy'],
                    'F1': m['f1_macro'],
                    'ROC-AUC': mean_auc if not np.isnan(mean_auc) else '-',
                })
            else:
                all_results.append({
                    'Objective': obj,
                    'Algorithm': ALGO_LABELS[algo],
                    'Accuracy': m['accuracy'],
                    'F1': m['f1'],
                    'ROC-AUC': m['roc_auc'],
                })

leaderboard = pd.DataFrame(all_results)
print(leaderboard.to_string(index=False))

# ── Best model per objective ──
print('\\n\\n🏆 Best Model per Objective (by F1):')
for obj in OBJECTIVES:
    subset = leaderboard[leaderboard['Objective'] == obj]
    if not subset.empty:
        best = subset.loc[subset['F1'].idxmax()]
        print(f'  {obj:25s} → {best["Algorithm"]:25s}  F1={best["F1"]:.4f}  AUC={best["ROC-AUC"]}')

# ── Overall best ──
print('\\n\\n🏆 Global Best (by mean F1 across objectives):')
mean_f1 = leaderboard.groupby('Algorithm')['F1'].mean().sort_values(ascending=False)
for algo, f1 in mean_f1.items():
    print(f'  {algo:25s}  Mean F1={f1:.4f}')
""")

# ===== CELL 15: F1 by class for relapse/suicide/therapy =====
code("""
# ═══════════════════════════════════════════════════════
#  F1 per Class — Binary Objectives
# ═══════════════════════════════════════════════════════

print('F1-Score por Classe (binário):')
print()

for obj_name, models_dict, results_dict in [
    ('relapse', relapse_models, relapse_results),
    ('suicide_risk', suicide_models, suicide_results),
    ('therapeutic_response', therapy_models, therapy_results),
]:
    print(f'\\n── {obj_name} ──')
    for algo, dm in models_dict.items():
        classes = dm['le'].classes_.tolist()
        report = classification_report(dm['y_test'], dm['y_pred'],
                                       target_names=[str(c) for c in classes],
                                       output_dict=True, zero_division=0)
        for cls_name in classes:
            cls_key = str(cls_name)
            f1 = report.get(cls_key, {}).get('f1-score', 0)
            support = report.get(cls_key, {}).get('support', 0)
            print(f'  {ALGO_LABELS[algo]:25s}  Class {cls_name}: F1={f1:.4f}  (support={int(support)})')
""")

# ===== CELL 16: Limitations =====
code("""
# ═══════════════════════════════════════════════════════
#  LIMITACOES — Leitura Obrigatoria
# ═══════════════════════════════════════════════════════

print('=' * 80)
print('LIMITACOES - Modelos Treinados em Dados Sinteticos')
print('=' * 80)
print('')

text = '''
1. DADOS SINTETICOS
   Todos os modelos foram treinados exclusivamente em dados gerados artificialmente
   por scripts de seed (scripts/seed_clinical_data.py). As distribuicoes de sintomas,
   correlacoes entre escalas e padroes de diagnostico refletem regras heuristicas
   do gerador, NAO padroes clinicos reais. Metricas como AUC > 0,90 em dados
   sinteticos NAO devem ser interpretadas como performance clinica.

2. CLASS IMBALANCE ARTIFICIAL
   O desbalanceamento de classes observado nos dados sinteticos (ex.: prevalencia
   de depressao major vs. transtorno de sintomas somaticos) segue proporcoes
   arbitrarias definidas pelo gerador, nao a epidemiologia real.

3. TEMPORAL SPLIT VS. DATA LEAKAGE
   Embora o split temporal seja a abordagem correta para series clinicas, os dados
   sinteticos foram gerados em bloco (sem evolucao temporal real de doenca).
   Pacientes podem ter consultas consecutivas no mesmo dia, o que torna o split
   temporal menos informativo do que seria com dados clinicos reais.

4. GENERALIZACAO ZERO
   Modelos treinados em dados sinteticos tem capacidade zero de generalizacao
   para populacoes clinicas reais. As metricas aqui reportadas servem exclusivamente
   para demonstrar a correta implementacao da pipeline de avaliacao (split temporal,
   curvas ROC/PR, calibracao, F1 por classe, comparacao entre algoritmos).

5. CALIBRACAO ENGANAOSA
   Modelos calibrados em dados sinteticos podem apresentar calibration plots
   enganosamente perfeitos devido a ausencia de ruido clinico real (ex.: variabilidade
   entre avaliadores, erros de medida em escalas, comorbidades nao documentadas).

6. HIPERPARAMETROS NAO OTIMIZADOS CLINICAMENTE
   Os hiperparametros atuais (definidos em app/ml/training/estimators.py) foram
   selecionados para demonstracao metodologica, nao otimizados para performance
   clinica. Uma validacao clinica real exigiria tunagem com validacao cruzada
   temporal em dados reais, com custo de erro clinico (falso negativo para suicidio
   e muito mais grave que falso positivo) explicitamente modelado na funcao de custo.

7. STAKEHOLDER VALIDATION REQUIRED
   Antes de qualquer uso clinico, os modelos devem ser:
   a) Re-treinados com dados clinicos reais e anotados por especialistas
   b) Validados em estudo prospectivo com golden standard (entrevista diagnostica
      estruturada como SCID-5-CV)
   c) Submetidos a aprovacao de comite de etica em pesquisa (CEP/CONEP)
   d) Registrados na ANVISA como software medico (RDC 657/2022)
'''

print(text)
""")

# ===== CELL 17: References =====
code("""
# ═══════════════════════════════════════════════════════
#  REFERENCIAS METODOLOGICAS
# ═══════════════════════════════════════════════════════

text = '''
1. Steyerberg, E.W. (2019). Clinical Prediction Models (2nd ed.). Springer.
   - Referencia padrao para desenvolvimento e validacao de modelos de predicao clinica.

2. Harrell, F.E. (2015). Regression Modeling Strategies (2nd ed.). Springer.
   - Estrategias para validacao interna (bootstrapping, cross-validation temporal).

3. Huang, Y., Li, W., Macheret, F., et al. (2020). A tutorial on calibration
   measurements and calibration models for clinical prediction models.
   Journal of the American Medical Informatics Association, 27(4), 621-633.
   - Calibracao como requisito para modelos de apoio a decisao clinica.

4. Saito, T. & Rehmsmeier, M. (2015). The precision-recall plot is more
   informative than the ROC plot when evaluating binary classifiers on
   imbalanced datasets. PLoS ONE, 10(3), e0118432.
   - PR curves sao preferiveis a ROC em dados desbalanceados (comum em
     predicao de suicidio e recaida).

5. Mandrekar, J.N. (2010). Receiver operating characteristic curve in
   diagnostic test assessment. Journal of Thoracic Oncology, 5(9), 1315-1316.
   - Interpretacao clinica de AUC-ROC.

6. FDA (2022). Artificial Intelligence and Machine Learning in Software
   as a Medical Device. https://www.fda.gov/medical-devices/software-medical-device-samd
   - Regulamentacao de modelos de ML como dispositivo medico.

7. ANVISA (2022). RDC No 657/2022 - Software como Dispositivo Medico.
   - Marco regulatorio brasileiro para software medico.

8. APA (2022). DSM-5-TR: Diagnostic and Statistical Manual of Mental
   Disorders (5th ed., Text Revision). American Psychiatric Publishing.
   - Fonte dos criterios diagnosticos usados como ground truth.

9. WHO (2019). ICD-11: International Classification of Diseases
   (11th revision). World Health Organization.
   - Sistema de classificacao diagnostica adotado.
'''

print(text)
""")

# ===== Write =====
output_dir = Path(__file__).parent
output_path = output_dir / 'model_evaluation.ipynb'

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f'Notebook gerado: {output_path}')
print(f'{len(nb["cells"])} células')
