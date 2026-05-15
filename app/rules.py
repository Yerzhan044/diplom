from app.schemas import TransactionIn


HIGH_RISK_COUNTRIES = {"NG", "PK", "VN", "ID", "BR"}
GAMBLING_MCC = {"7995"}


def evaluate_rules(
    tx: TransactionIn, online_features: dict[str, float]
) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    if tx.amount >= 2500:
        score += 0.35
        reasons.append("Очень крупная сумма")
    elif tx.amount >= 1000:
        score += 0.2
        reasons.append("Повышенная сумма")

    if online_features["count_1m"] >= 4:
        score += 0.25
        reasons.append("Высокая частота операций за 1 минуту")

    if online_features["count_5m"] >= 8:
        score += 0.2
        reasons.append("Высокая частота операций за 5 минут")

    if tx.country in HIGH_RISK_COUNTRIES:
        score += 0.15
        reasons.append("Страна повышенного риска")

    if tx.mcc in GAMBLING_MCC:
        score += 0.1
        reasons.append("Рискованный MCC")

    if online_features["amount_to_avg_ratio"] >= 4.0:
        score += 0.2
        reasons.append("Сильное отклонение от среднего чека")

    return min(1.0, score), reasons
