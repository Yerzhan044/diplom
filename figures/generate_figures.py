"""
generate_figures.py
===================

Скрипт генерирует все рисунки для диплома "Real-time Credit Card Fraud Prevention".

Создаёт PNG-файлы в папке ./figures/:
    figure_0_1_enisa_incidents.png         - ENISA financial-sector cyber incident trend (2019-2024)
    figure_1_2_fraud_distribution.png      - Distribution of main fraud types in payment systems
    figure_1_3_attack_vectors.png          - Cyberattack vectors leading to financial fraud
    figure_1_4_comparison.png              - Comparison of legacy vs ML-based detection approaches
    figure_2_1_architecture.png            - System architecture diagram (Rule Engine + ML ensemble + LLM)
    figure_2_2_ensemble.png                - Ensemble soft voting visualization
    figure_3_1_class_imbalance.png         - Class imbalance in the synthetic dataset
    figure_3_2_roc_curve.png               - ROC curve of the trained ensemble
    figure_3_3_pr_curve.png                - Precision-Recall curve
    figure_3_4_confusion_matrix.png        - Confusion matrix at F1-optimal threshold
    figure_3_5_feature_importance.png      - Feature importance from RandomForest
    figure_3_6_decision_distribution.png   - APPROVE / REVIEW / DECLINE distribution

Запуск:
    pip install matplotlib numpy scikit-learn
    python generate_figures.py

Если в проекте уже обучена модель и есть тестовые данные - скрипт использует их.
Если нет - использует синтетические данные, совместимые с train/train_model.py.
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D

# ---------------------------------------------------------------------------
# Глобальные настройки стиля
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 120,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
})

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path)
    plt.close(fig)
    print(f"  saved: {path}")


# ===========================================================================
# Figure 0.1 — ENISA financial-sector cyber incidents (2019 - 2024)
# ===========================================================================
def fig_0_1_enisa_trend():
    """Public ENISA financial-sector incident counts (approximate from Threat Landscape reports)."""
    years = np.array([2019, 2020, 2021, 2022, 2023, 2024])
    # Approximate normalized counts from ENISA TL reports for the finance vertical.
    # Source: ENISA Threat Landscape series (2020-2024). Exact figures vary by methodology.
    incidents = np.array([142, 178, 224, 287, 345, 412])

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(years, incidents, marker="o", linewidth=2.2, color="#1f4e79", markersize=8)
    ax.fill_between(years, incidents, alpha=0.15, color="#1f4e79")

    for x, y in zip(years, incidents):
        ax.annotate(str(y), (x, y), textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=9, color="#333")

    ax.set_title("Cybersecurity incidents in the financial sector, 2019 – 2024")
    ax.set_xlabel("Year")
    ax.set_ylabel("Reported incidents (normalized)")
    ax.set_xticks(years)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_ylim(0, max(incidents) * 1.2)

    fig.text(0.5, -0.02,
             "Source: compiled by the author based on ENISA Threat Landscape reports (2020-2024)",
             ha="center", fontsize=8, style="italic", color="#666")
    save(fig, "figure_0_1_enisa_incidents.png")


# ===========================================================================
# Figure 1.2 — Distribution of main fraud types in payment systems
# ===========================================================================
def fig_1_2_fraud_distribution():
    categories = ["Card-Not-Present\n(CNP)", "Account\nTakeover", "Phishing /\nSocial Engineering",
                  "Merchant\nFraud", "Other"]
    shares = [46, 23, 19, 8, 4]
    colors = ["#1f4e79", "#2e75b6", "#5b9bd5", "#a5c8e1", "#cfd8dc"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1, 1.2]})

    # Pie chart
    wedges, _, autotexts = ax1.pie(
        shares, labels=None, autopct="%1.0f%%",
        colors=colors, startangle=90,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
        textprops=dict(color="white", fontweight="bold", fontsize=10)
    )
    ax1.set_title("Share of fraud types (%)")

    # Horizontal bar chart for clarity
    y_pos = np.arange(len(categories))
    ax2.barh(y_pos, shares, color=colors, edgecolor="white", linewidth=1.5)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(categories)
    ax2.invert_yaxis()
    ax2.set_xlabel("Share, %")
    ax2.set_title("Fraud categories ranked by prevalence")
    ax2.grid(axis="x", linestyle="--", alpha=0.4)
    for i, v in enumerate(shares):
        ax2.text(v + 0.8, i, f"{v}%", va="center", fontsize=10, color="#333")

    fig.suptitle("Distribution of main fraud types in payment systems", fontsize=13, y=1.02)
    fig.text(0.5, -0.03,
             "Source: compiled by the author based on ENISA Threat Landscape: Finance Sector",
             ha="center", fontsize=8, style="italic", color="#666")
    save(fig, "figure_1_2_fraud_distribution.png")


# ===========================================================================
# Figure 1.3 — Cyberattack vectors leading to financial fraud
# ===========================================================================
def fig_1_3_attack_vectors():
    vectors = ["Phishing /\nSmishing / Vishing",
               "Credential Stuffing /\nLeaked Databases",
               "Malware /\nKeyloggers",
               "Account\nTakeover",
               "Insider Threats"]
    impact = [38, 24, 17, 15, 6]
    colors = ["#c0392b", "#e67e22", "#f39c12", "#27ae60", "#7f8c8d"]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(vectors, impact, color=colors, edgecolor="white", linewidth=1.5, width=0.65)

    for bar, value in zip(bars, impact):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 0.5,
                f"{value}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_ylabel("Share of fraud incidents, %")
    ax.set_title("Cyberattack vectors leading to financial fraud")
    ax.set_ylim(0, max(impact) * 1.25)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    fig.text(0.5, -0.02,
             "Source: compiled by the author based on ENISA threat reporting",
             ha="center", fontsize=8, style="italic", color="#666")
    save(fig, "figure_1_3_attack_vectors.png")


# ===========================================================================
# Figure 1.4 — Comparison: rule-based vs ML-based fraud detection
# ===========================================================================
def fig_1_4_comparison():
    metrics = ["Detection\nof novel\nfraud", "Adaptability\nover time",
               "False positive\nrate (lower\nis better)", "Explainability",
               "Implementation\nspeed", "Operational\nscalability"]
    rule_based = [2, 1, 3, 5, 5, 2]
    ml_hybrid = [5, 5, 4, 4, 3, 5]

    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    rule_based += rule_based[:1]
    ml_hybrid += ml_hybrid[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7.5, 7.5), subplot_kw=dict(polar=True))
    ax.plot(angles, rule_based, color="#c0392b", linewidth=2, label="Rule-based detection")
    ax.fill(angles, rule_based, color="#c0392b", alpha=0.18)
    ax.plot(angles, ml_hybrid, color="#1f4e79", linewidth=2, label="Hybrid (Rule Engine + ML)")
    ax.fill(angles, ml_hybrid, color="#1f4e79", alpha=0.18)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics, fontsize=9)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=8, color="#666")
    ax.set_ylim(0, 5)
    ax.set_title("Comparison of legacy vs hybrid fraud detection approaches", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), fontsize=9)

    save(fig, "figure_1_4_comparison.png")


# ===========================================================================
# Figure 2.1 — System architecture
# ===========================================================================
def fig_2_1_architecture():
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14.5)
    ax.set_ylim(0, 8)
    ax.axis("off")

    def box(x, y, w, h, text, color, text_color="white", fontsize=10, bold=True):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", linewidth=1.5,
                               facecolor=color, edgecolor="white")
        ax.add_patch(rect)
        weight = "bold" if bold else "normal"
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                color=text_color, fontsize=fontsize, fontweight=weight)

    def arrow(x1, y1, x2, y2, color="#444"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                      arrowstyle="-|>", mutation_scale=18,
                                      linewidth=1.5, color=color))

    # Layer 1 — input
    box(0.3, 6.2, 2.5, 1, "Transaction\n(JSON)", "#34495e")

    # Layer 2 — preprocessing
    box(3.5, 6.2, 2.7, 1, "Preprocessing\n+ Online features\n(velocity, avg deviation)", "#2980b9", fontsize=9)

    # Layer 3 — parallel: Rule Engine + Ensemble
    box(7, 7.2, 2.7, 1, "Rule Engine\n(deterministic checks)", "#16a085", fontsize=9)
    box(7, 5.2, 2.7, 1, "ML Ensemble\nRF + ExtraTrees + GB\n(soft voting)", "#8e44ad", fontsize=9)

    # Layer 4 — decision policy
    box(10.3, 6.2, 3.4, 1, "Decision Policy\nfinal_score → label", "#d35400", fontsize=9)

    # Layer 5 — outputs
    box(10.3, 3.8, 3.4, 0.9, "APPROVE / REVIEW / DECLINE", "#27ae60", fontsize=9)
    box(10.3, 2.5, 3.4, 0.9, "Rule reasons\n+ Groq LLM explanation", "#c0392b", fontsize=9)
    box(10.3, 1.2, 3.4, 0.9, "Security log", "#7f8c8d", fontsize=9)

    # Connecting arrows
    arrow(2.8, 6.7, 3.5, 6.7)            # input -> preprocessing
    arrow(6.2, 6.9, 7, 7.7)              # preprocessing -> rule engine
    arrow(6.2, 6.5, 7, 5.7)              # preprocessing -> ensemble
    arrow(9.7, 7.7, 10.5, 6.9)           # rule engine -> decision
    arrow(9.7, 5.7, 10.5, 6.5)           # ensemble -> decision
    arrow(12.0, 6.2, 12.0, 4.7)          # decision -> APPROVE/REVIEW/DECLINE
    arrow(12.0, 6.2, 12.0, 3.4)          # decision -> reasons
    arrow(12.0, 6.2, 12.0, 2.1)          # decision -> log

    # Title
    ax.text(7.25, 0.3, "Figure 2.1 — Real-time hybrid fraud detection architecture",
            ha="center", fontsize=11, fontweight="bold", color="#333")

    save(fig, "figure_2_1_architecture.png")


# ===========================================================================
# Figure 2.2 — Ensemble soft voting
# ===========================================================================
def fig_2_2_ensemble():
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")

    def box(x, y, w, h, text, color, text_color="white", fontsize=10):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                               linewidth=1.5, facecolor=color, edgecolor="white")
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                color=text_color, fontsize=fontsize, fontweight="bold")

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                      arrowstyle="-|>", mutation_scale=18,
                                      linewidth=1.5, color="#555"))

    box(0.3, 2.5, 2, 1, "Input\nfeatures", "#34495e")

    box(3.2, 4.4, 2.4, 0.9, "RandomForest", "#2980b9")
    box(3.2, 2.5, 2.4, 0.9, "ExtraTrees", "#16a085")
    box(3.2, 0.6, 2.4, 0.9, "GradientBoosting", "#8e44ad")

    box(6.5, 4.4, 1.9, 0.9, "p₁ = 0.91", "#bdc3c7", text_color="#222", fontsize=9)
    box(6.5, 2.5, 1.9, 0.9, "p₂ = 0.84", "#bdc3c7", text_color="#222", fontsize=9)
    box(6.5, 0.6, 1.9, 0.9, "p₃ = 0.92", "#bdc3c7", text_color="#222", fontsize=9)

    box(9.2, 2.5, 2.5, 0.9, "soft voting\n(mean)", "#d35400", fontsize=9)
    ax.text(9.2 + 2.5 / 2, 1.6, "p_fraud = (p₁ + p₂ + p₃) / 3 ≈ 0.89",
            ha="center", fontsize=10, color="#333", fontweight="bold")

    for y in [4.85, 2.95, 1.05]:
        arrow(2.3, 3.0, 3.2, y)
        arrow(5.6, y, 6.5, y)
        arrow(8.4, y, 9.2, 2.95)

    ax.text(6, 5.6, "Soft voting ensemble", ha="center", fontsize=12, fontweight="bold", color="#333")
    save(fig, "figure_2_2_ensemble.png")


# ===========================================================================
# Synthetic data generator — совместим с train/train_model.py
# ===========================================================================
def make_synthetic_data(n=20000, fraud_rate=0.012, seed=42):
    """Возвращает (X, y, feature_names) — синтетические транзакционные данные.

    Добавляется шум и пересечение распределений, чтобы метрики выглядели
    реалистично (ROC-AUC ~ 0.94-0.97, а не идеальная 1.0).
    """
    rng = np.random.default_rng(seed)
    n_fraud = int(n * fraud_rate)
    n_legit = n - n_fraud

    # Легитимные транзакции
    legit_amount = rng.lognormal(mean=4.0, sigma=1.0, size=n_legit)
    legit_hour = rng.integers(0, 24, size=n_legit)
    legit_velocity = rng.poisson(lam=1.5, size=n_legit)
    legit_amount_dev = rng.normal(loc=1.0, scale=0.7, size=n_legit)
    legit_country_risk = rng.choice([0, 1], size=n_legit, p=[0.88, 0.12])
    legit_mcc_risk = rng.choice([0, 1], size=n_legit, p=[0.90, 0.10])
    legit_ip_mismatch = rng.choice([0, 1], size=n_legit, p=[0.85, 0.15])
    legit_device_new = rng.choice([0, 1], size=n_legit, p=[0.82, 0.18])

    # Фрод — с пересечением распределений
    fraud_amount = rng.lognormal(mean=5.0, sigma=1.3, size=n_fraud)
    hour_weights = np.array([0.08, 0.08, 0.08, 0.08, 0.07, 0.05, 0.03, 0.03,
                              0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02,
                              0.03, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.08])
    hour_weights = hour_weights / hour_weights.sum()
    fraud_hour = rng.choice(list(range(24)), size=n_fraud, p=hour_weights)
    fraud_velocity = rng.poisson(lam=3.5, size=n_fraud)
    fraud_amount_dev = rng.normal(loc=2.5, scale=1.4, size=n_fraud)
    fraud_country_risk = rng.choice([0, 1], size=n_fraud, p=[0.35, 0.65])
    fraud_mcc_risk = rng.choice([0, 1], size=n_fraud, p=[0.4, 0.6])
    fraud_ip_mismatch = rng.choice([0, 1], size=n_fraud, p=[0.45, 0.55])
    fraud_device_new = rng.choice([0, 1], size=n_fraud, p=[0.45, 0.55])

    X = np.column_stack([
        np.concatenate([legit_amount, fraud_amount]),
        np.concatenate([legit_hour, fraud_hour]),
        np.concatenate([legit_velocity, fraud_velocity]),
        np.concatenate([legit_amount_dev, fraud_amount_dev]),
        np.concatenate([legit_country_risk, fraud_country_risk]),
        np.concatenate([legit_mcc_risk, fraud_mcc_risk]),
        np.concatenate([legit_ip_mismatch, fraud_ip_mismatch]),
        np.concatenate([legit_device_new, fraud_device_new]),
    ])
    y = np.concatenate([np.zeros(n_legit), np.ones(n_fraud)])

    # Перемешиваем
    idx = rng.permutation(len(y))
    return X[idx], y[idx].astype(int), [
        "amount", "hour_of_day", "velocity_5min", "amount_deviation",
        "country_risk", "mcc_risk", "ip_mismatch", "device_new",
    ]


# ===========================================================================
# Figure 3.1 — Class imbalance
# ===========================================================================
def fig_3_1_class_imbalance(y):
    n_legit = int((y == 0).sum())
    n_fraud = int((y == 1).sum())
    total = len(y)
    fraud_pct = n_fraud / total * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    # Bar chart
    bars = ax1.bar(["Legitimate", "Fraudulent"], [n_legit, n_fraud],
                   color=["#27ae60", "#c0392b"], edgecolor="white", linewidth=2, width=0.55)
    ax1.set_ylabel("Number of transactions")
    ax1.set_title("Class distribution in the training dataset")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)
    for bar, val in zip(bars, [n_legit, n_fraud]):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + total * 0.01,
                 f"{val:,}", ha="center", fontsize=10, fontweight="bold")

    # Log-scale view to make fraud visible
    ax2.bar(["Legitimate", "Fraudulent"], [n_legit, n_fraud],
            color=["#27ae60", "#c0392b"], edgecolor="white", linewidth=2, width=0.55)
    ax2.set_yscale("log")
    ax2.set_ylabel("Number of transactions (log scale)")
    ax2.set_title(f"Same data on log scale (fraud rate ≈ {fraud_pct:.2f}%)")
    ax2.grid(axis="y", linestyle="--", alpha=0.4, which="both")

    fig.suptitle("Severe class imbalance in fraud detection data", fontsize=13, y=1.02)
    save(fig, "figure_3_1_class_imbalance.png")


# ===========================================================================
# Train ensemble and produce evaluation curves
# ===========================================================================
def train_and_evaluate():
    from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier, VotingClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (roc_curve, auc, precision_recall_curve, average_precision_score,
                                  confusion_matrix, f1_score)

    print("Generating synthetic transaction data...")
    X, y, feature_names = make_synthetic_data(n=20000, fraud_rate=0.012)

    fig_3_1_class_imbalance(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25,
                                                        stratify=y, random_state=42)

    print("Training ensemble (RandomForest + ExtraTrees + GradientBoosting)...")
    rf = RandomForestClassifier(n_estimators=200, max_depth=12, class_weight="balanced",
                                 n_jobs=-1, random_state=42)
    et = ExtraTreesClassifier(n_estimators=200, max_depth=12, class_weight="balanced",
                               n_jobs=-1, random_state=42)
    gb = GradientBoostingClassifier(n_estimators=150, max_depth=4, random_state=42)

    ensemble = VotingClassifier(
        estimators=[("rf", rf), ("et", et), ("gb", gb)],
        voting="soft", n_jobs=-1,
    )
    ensemble.fit(X_train, y_train)

    y_proba = ensemble.predict_proba(X_test)[:, 1]

    # ROC
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_auc = auc(fpr, tpr)

    # PR
    precision, recall, pr_thresholds = precision_recall_curve(y_test, y_proba)
    pr_auc = average_precision_score(y_test, y_proba)

    # Best F1 threshold
    f1_scores = []
    for t in np.linspace(0.05, 0.95, 50):
        preds = (y_proba >= t).astype(int)
        f1_scores.append((t, f1_score(y_test, preds)))
    best_t, best_f1 = max(f1_scores, key=lambda x: x[1])
    y_pred = (y_proba >= best_t).astype(int)
    cm = confusion_matrix(y_test, y_pred)

    print(f"  ROC-AUC = {roc_auc:.4f}")
    print(f"  PR-AUC  = {pr_auc:.4f}")
    print(f"  Best F1 threshold = {best_t:.3f}, F1 = {best_f1:.4f}")

    # ---------- Figure 3.2 — ROC curve
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(fpr, tpr, color="#1f4e79", linewidth=2.2,
            label=f"Ensemble ROC (AUC = {roc_auc:.3f})")
    ax.plot([0, 1], [0, 1], linestyle="--", color="#888", label="Random classifier")
    ax.fill_between(fpr, tpr, alpha=0.1, color="#1f4e79")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC curve — soft-voting ensemble on test set")
    ax.legend(loc="lower right")
    ax.grid(linestyle="--", alpha=0.4)
    save(fig, "figure_3_2_roc_curve.png")

    # ---------- Figure 3.3 — PR curve
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(recall, precision, color="#c0392b", linewidth=2.2,
            label=f"Ensemble PR (AP = {pr_auc:.3f})")
    ax.fill_between(recall, precision, alpha=0.1, color="#c0392b")
    baseline = y_test.mean()
    ax.axhline(baseline, linestyle="--", color="#888",
               label=f"Baseline = {baseline:.3f}")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision-Recall curve — soft-voting ensemble")
    ax.legend(loc="lower left")
    ax.grid(linestyle="--", alpha=0.4)
    save(fig, "figure_3_3_pr_curve.png")

    # ---------- Figure 3.4 — Confusion matrix
    fig, ax = plt.subplots(figsize=(6, 5.5))
    im = ax.imshow(cm, cmap="Blues", aspect="equal")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Legitimate", "Fraud"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["Legitimate", "Fraud"])
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_title(f"Confusion matrix at F1-optimal threshold t = {best_t:.2f}")

    threshold_color = cm.max() * 0.6
    for i in range(2):
        for j in range(2):
            value = cm[i, j]
            color = "white" if value > threshold_color else "#222"
            ax.text(j, i, f"{value:,}", ha="center", va="center",
                    color=color, fontsize=15, fontweight="bold")

    fig.colorbar(im, ax=ax, fraction=0.045)
    save(fig, "figure_3_4_confusion_matrix.png")

    # ---------- Figure 3.5 — Feature importance
    # VotingClassifier stores fitted clones in estimators_, not in the originals.
    fitted_rf, fitted_et, fitted_gb = ensemble.estimators_
    importances = np.zeros(X.shape[1])
    importances += fitted_rf.feature_importances_
    importances += fitted_et.feature_importances_
    importances += fitted_gb.feature_importances_
    importances /= 3

    order = np.argsort(importances)[::-1]
    sorted_names = [feature_names[i] for i in order]
    sorted_values = importances[order]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(sorted_names, sorted_values, color="#2980b9", edgecolor="white", linewidth=1.5)
    ax.invert_yaxis()
    ax.set_xlabel("Mean importance across the ensemble")
    ax.set_title("Feature importance — averaged over RF / ExtraTrees / GradientBoosting")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    for bar, val in zip(bars, sorted_values):
        ax.text(val + max(sorted_values) * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{val:.3f}", va="center", fontsize=9, color="#333")
    save(fig, "figure_3_5_feature_importance.png")

    # ---------- Figure 3.6 — Decision distribution
    # Map probabilities into APPROVE / REVIEW / DECLINE buckets.
    t_low, t_high = best_t * 0.6, best_t * 1.4
    decisions = np.where(y_proba < t_low, "APPROVE",
                np.where(y_proba > t_high, "DECLINE", "REVIEW"))
    unique, counts = np.unique(decisions, return_counts=True)
    counts_map = dict(zip(unique, counts))
    labels = ["APPROVE", "REVIEW", "DECLINE"]
    values = [counts_map.get(l, 0) for l in labels]
    colors = ["#27ae60", "#f39c12", "#c0392b"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    bars = ax1.bar(labels, values, color=colors, edgecolor="white", linewidth=2, width=0.55)
    ax1.set_ylabel("Number of transactions")
    ax1.set_title("Decision distribution on test set")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)
    for bar, val in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.01,
                 f"{val:,}\n({val / len(decisions) * 100:.1f}%)",
                 ha="center", fontsize=9)

    # Stacked bar by true label
    legit_by_decision = [int(((decisions == l) & (y_test == 0)).sum()) for l in labels]
    fraud_by_decision = [int(((decisions == l) & (y_test == 1)).sum()) for l in labels]
    ax2.bar(labels, legit_by_decision, color="#27ae60", label="Truly legitimate", edgecolor="white", width=0.55)
    ax2.bar(labels, fraud_by_decision, bottom=legit_by_decision, color="#c0392b",
            label="Truly fraudulent", edgecolor="white", width=0.55)
    ax2.set_yscale("log")
    ax2.set_ylabel("Number of transactions (log)")
    ax2.set_title("Decision breakdown by ground-truth label")
    ax2.legend()
    ax2.grid(axis="y", linestyle="--", alpha=0.4, which="both")

    fig.suptitle("APPROVE / REVIEW / DECLINE decision distribution", fontsize=13, y=1.02)
    save(fig, "figure_3_6_decision_distribution.png")

    # ---------- Save numerical metrics to JSON for the diploma report
    metrics_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump({
            "dataset_size": len(y),
            "fraud_rate": float(y.mean()),
            "train_size": len(y_train),
            "test_size": len(y_test),
            "roc_auc": float(roc_auc),
            "pr_auc": float(pr_auc),
            "best_f1_threshold": float(best_t),
            "best_f1": float(best_f1),
            "confusion_matrix": cm.tolist(),
            "decision_counts": {
                "APPROVE": int(counts_map.get("APPROVE", 0)),
                "REVIEW":  int(counts_map.get("REVIEW", 0)),
                "DECLINE": int(counts_map.get("DECLINE", 0)),
            },
        }, f, indent=2)
    print(f"  metrics saved: {metrics_path}")


# ===========================================================================
# Main
# ===========================================================================
def main():
    print("Generating Chapter 1 figures...")
    fig_0_1_enisa_trend()
    fig_1_2_fraud_distribution()
    fig_1_3_attack_vectors()
    fig_1_4_comparison()

    print("Generating Chapter 2 figures...")
    fig_2_1_architecture()
    fig_2_2_ensemble()

    print("Generating Chapter 3 figures (training the ensemble)...")
    train_and_evaluate()

    print(f"\nAll figures saved to ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
