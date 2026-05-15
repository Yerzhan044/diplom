"""Input validation for transactions."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, validator


class TransactionValidator:
    """Validates transaction input data."""

    # Valid MCC codes for gambling
    GAMBLING_MCC = {"7995", "7996", "7994", "6211", "6212"}

    # High-risk countries
    HIGH_RISK_COUNTRIES = {
        "NG", "KP", "IR", "SY", "VN", "PK", "AO", "BZ", "MM", "CI"
    }

    # Valid ISO currency codes (subset)
    VALID_CURRENCIES = {
        "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "KZT"
    }

    # Valid ISO country codes (subset)
    VALID_COUNTRIES = {
        "US", "GB", "DE", "FR", "JP", "AU", "CA", "CH", "CN", "KZ",
        "NG", "KP", "IR", "SY", "VN", "PK", "AO", "BZ", "MM", "CI"
    }

    @staticmethod
    def validate_transaction(tx_dict: dict[str, Any]) -> dict[str, str]:
        """Validate transaction data and return errors."""
        errors = []

        # Transaction ID validation
        tx_id = tx_dict.get("transaction_id", "")
        if not tx_id or len(str(tx_id)) > 50:
            errors.append("transaction_id: must be 1-50 characters")

        # Card ID validation
        card_id = tx_dict.get("card_id", "")
        if not card_id or len(str(card_id)) > 50:
            errors.append("card_id: must be 1-50 characters")

        # Amount validation
        try:
            amount = float(tx_dict.get("amount", -1))
            if amount <= 0 or amount > 999999:
                errors.append("amount: must be between 0.01 and 999999")
        except (TypeError, ValueError):
            errors.append("amount: must be a valid number")

        # Currency validation
        currency = str(tx_dict.get("currency", "USD")).upper()
        if currency not in TransactionValidator.VALID_CURRENCIES:
            errors.append(
                f"currency: must be one of {TransactionValidator.VALID_CURRENCIES}"
            )

        # Country validation
        country = str(tx_dict.get("country", "")).upper()
        if not country or country not in TransactionValidator.VALID_COUNTRIES:
            errors.append(
                f"country: must be valid ISO 3166-1 code"
            )

        # MCC validation
        mcc = str(tx_dict.get("mcc", "0000"))
        if not mcc.isdigit() or len(mcc) != 4:
            errors.append("mcc: must be 4-digit code")

        # Timestamp validation
        try:
            timestamp_str = tx_dict.get("timestamp", "")
            datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, TypeError, AttributeError):
            errors.append("timestamp: must be ISO 8601 format (e.g., 2026-05-09T14:30:00+00:00)")

        # IP address basic validation
        ip = str(tx_dict.get("ip_address", "0.0.0.0"))
        ip_parts = ip.split(".")
        if len(ip_parts) != 4:
            errors.append("ip_address: must be valid IPv4 address")
        else:
            try:
                for part in ip_parts:
                    num = int(part)
                    if num < 0 or num > 255:
                        errors.append("ip_address: must be valid IPv4 address")
                        break
            except ValueError:
                errors.append("ip_address: must be valid IPv4 address")

        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def get_validation_summary(validation_result: dict) -> str:
        """Get human-readable validation summary."""
        if validation_result["valid"]:
            return "✓ Transaction data is valid"
        return "✗ Validation errors:\n  - " + "\n  - ".join(
            validation_result["errors"]
        )
