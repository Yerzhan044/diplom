# Thesis Alignment (for diploma paper)

## Topic

Real-time Credit Card Fraud Prevention

## Research Goal

Develop and implement a real-time credit card fraud detection system based on ensemble machine learning methods with explainable decision support.

## Research Object and Subject

- Object: cybersecurity assurance process in payment systems during transaction processing.
- Subject: machine learning algorithms and decision logic for fraud detection.

## Implemented Tasks Mapping

1. Analytical review of payment fraud landscape:
   - Covered in Chapter 1 text in diploma paper.
2. Analysis of limitations of traditional detection:
   - Motivated by hybrid architecture and real-time constraints.
3. Real-time architecture design:
   - `docs/architecture.md`, `app/main.py`, `app/state.py`.
4. Supervised ML implementation:
   - `train/train_model.py`.
5. Ensemble-based fraud detection mechanism:
   - Soft-voting ensemble in `train/train_model.py`.
6. Explainability:
   - Human-readable rule reasons in `app/rules.py` and API response.
7. Experimental evaluation:
   - ROC-AUC, PR-AUC, classification report from training script.

## Scientific Novelty Statement (project-level)

- Hybridization of explainable business rules and ensemble ML probability in one real-time scoring pipeline.
- Practical handling of online behavioral signals (velocity and amount deviation) for streaming transaction decisions.

## Practical Significance

- Can be used as an MVP blueprint for transaction monitoring modernization.
- Supports reduction of financial losses and faster suspicious transaction triage.

## Chapter-to-Code Traceability

- Chapter 2 (Architecture): `docs/architecture.md`
- Chapter 3 (Implementation): `app/main.py`, `app/model.py`, `app/rules.py`, `app/state.py`
- Chapter 3 (Experiments): `train/train_model.py`, `simulator/generate_stream.py`

## What to add before final defense

1. Add confusion matrix and threshold sensitivity plots.
2. Add ablation table: Rules-only vs Single model vs Ensemble vs Hybrid.
3. Add business metrics: false decline rate and recall at manual-review budget.
