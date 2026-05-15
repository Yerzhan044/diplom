from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    IsolationForest,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from app.model import FEATURE_COLUMNS


def build_synthetic_dataset(n_rows: int = 15000, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic imbalanced fraud dataset."""
    rng = np.random.default_rng(seed)

    amount = rng.lognormal(mean=4.1, sigma=0.85, size=n_rows)
    count_1m = rng.poisson(lam=0.8, size=n_rows)
    count_5m = count_1m + rng.poisson(lam=1.5, size=n_rows)
    avg_amount_30 = rng.lognormal(mean=3.9, sigma=0.55, size=n_rows)
    amount_to_avg_ratio = amount / np.maximum(avg_amount_30, 1e-6)

    is_high_risk_country = rng.binomial(n=1, p=0.08, size=n_rows)
    is_night = rng.binomial(n=1, p=0.22, size=n_rows)
    is_gambling_mcc = rng.binomial(n=1, p=0.06, size=n_rows)

    latent = (
        0.0015 * amount
        + 0.38 * count_1m
        + 0.18 * count_5m
        + 0.48 * np.minimum(amount_to_avg_ratio, 8)
        + 1.1 * is_high_risk_country
        + 0.65 * is_night
        + 0.85 * is_gambling_mcc
        - 3.2
    )

    prob = 1.0 / (1.0 + np.exp(-latent))
    y = rng.binomial(n=1, p=np.clip(prob, 0.001, 0.999), size=n_rows)

    df = pd.DataFrame(
        {
            "amount": amount,
            "count_1m": count_1m,
            "count_5m": count_5m,
            "avg_amount_30": avg_amount_30,
            "amount_to_avg_ratio": amount_to_avg_ratio,
            "is_high_risk_country": is_high_risk_country,
            "is_night": is_night,
            "is_gambling_mcc": is_gambling_mcc,
            "target": y,
        }
    )
    return df


def main() -> None:
    print("=" * 70)
    print("TRAINING FRAUD DETECTION ENSEMBLE WITH UNSUPERVISED ANOMALY DETECTION")
    print("=" * 70)

    # Generate dataset
    print("\n1. Generating synthetic dataset...")
    df = build_synthetic_dataset()
    print(f"   Total records: {len(df)}")
    print(f"   Fraud rate: {df['target'].mean():.2%}")

    X = df[FEATURE_COLUMNS]
    y = df["target"]

    # Train-test split
    print("\n2. Splitting data (75% train, 25% test with stratification)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    print(f"   Train size: {len(X_train)}")
    print(f"   Test size: {len(X_test)}")

    # Train supervised ensemble
    print("\n3. Training supervised ensemble models...")

    rf_model = RandomForestClassifier(
        n_estimators=300,
        max_depth=10,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1,
    )
    print("   - RandomForest (300 trees)")

    et_model = ExtraTreesClassifier(
        n_estimators=400,
        max_depth=12,
        min_samples_leaf=8,
        random_state=42,
        n_jobs=-1,
    )
    print("   - ExtraTrees (400 trees)")

    gb_model = GradientBoostingClassifier(
        n_estimators=250,
        learning_rate=0.06,
        max_depth=3,
        random_state=42,
    )
    print("   - GradientBoosting (250 boosting rounds)")

    model = VotingClassifier(
        estimators=[
            ("rf", rf_model),
            ("et", et_model),
            ("gb", gb_model),
        ],
        voting="soft",
        weights=[3, 3, 2],
    )

    model.fit(X_train, y_train)
    print("   ✓ Supervised ensemble trained")

    # Train unsupervised anomaly detector
    print("\n4. Training unsupervised anomaly detection (Isolation Forest)...")
    anomaly_model = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_jobs=-1,
    )
    anomaly_model.fit(X_train)
    print("   ✓ Isolation Forest trained")

    # Evaluate supervised model
    print("\n5. Evaluating supervised model on test set...")
    test_proba = model.predict_proba(X_test)[:, 1]
    test_pred = (test_proba >= 0.5).astype(int)

    roc_auc = roc_auc_score(y_test, test_proba)
    pr_auc = average_precision_score(y_test, test_proba)

    precision, recall, thresholds = precision_recall_curve(y_test, test_proba)
    f1_scores = (2 * precision * recall) / np.maximum(precision + recall, 1e-9)
    best_idx = int(np.argmax(f1_scores[:-1]))
    best_threshold = float(thresholds[best_idx])
    best_f1 = float(f1_scores[best_idx])

    print(f"\n   ROC-AUC:           {roc_auc:.4f}")
    print(f"   PR-AUC:            {pr_auc:.4f}")
    print(f"   Best F1 threshold: {best_threshold:.4f}")
    print(f"   Best F1 score:     {best_f1:.4f}")

    # Detailed classification report
    best_pred = (test_proba >= best_threshold).astype(int)
    print("\n   Classification Report (at best F1 threshold):")
    print(classification_report(y_test, best_pred, digits=4))

    cm = confusion_matrix(y_test, best_pred)
    tn, fp, fn, tp = cm.ravel()
    print(f"   Confusion Matrix:")
    print(f"     TN: {tn}  FP: {fp}")
    print(f"     FN: {fn}  TP: {tp}")

    # Save models
    print("\n6. Saving models...")
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)

    supervised_path = artifacts_dir / "fraud_model.joblib"
    joblib.dump(model, supervised_path)
    print(f"   ✓ Supervised model saved to {supervised_path}")

    anomaly_path = artifacts_dir / "anomaly_model.joblib"
    joblib.dump(anomaly_model, anomaly_path)
    print(f"   ✓ Anomaly model saved to {anomaly_path}")

    # Save training metrics
    metrics = {
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "best_f1_threshold": float(best_threshold),
        "best_f1_score": float(best_f1),
        "test_size": len(X_test),
        "fraud_rate": float(y_test.mean()),
    }
    metrics_path = artifacts_dir / "training_metrics.json"
    import json

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"   ✓ Metrics saved to {metrics_path}")

    print("\n" + "=" * 70)
    print("TRAINING COMPLETE - Models ready for production fraud detection")
    print("=" * 70)


if __name__ == "__main__":
    main()
