"""Tests for input validators."""

import pytest
from app.validators import TransactionValidator


class TestTransactionValidator:
    """Test transaction input validation."""

    def test_valid_transaction(self):
        """Test validation of valid transaction."""
        valid_tx = {
            "transaction_id": "tx_001",
            "card_id": "card_123",
            "merchant_id": "m_456",
            "amount": 150.50,
            "currency": "USD",
            "country": "US",
            "mcc": "5411",
            "device_id": "d_789",
            "ip_address": "192.168.1.1",
            "timestamp": "2026-05-09T14:30:00+00:00",
        }
        result = TransactionValidator.validate_transaction(valid_tx)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_invalid_amount_negative(self):
        """Test validation of negative amount."""
        invalid_tx = {
            "transaction_id": "tx_001",
            "amount": -100.0,
            "currency": "USD",
            "country": "US",
            "mcc": "5411",
            "timestamp": "2026-05-09T14:30:00+00:00",
        }
        result = TransactionValidator.validate_transaction(invalid_tx)
        assert result["valid"] is False
        assert any("amount" in error for error in result["errors"])

    def test_invalid_amount_too_large(self):
        """Test validation of amount exceeding max."""
        invalid_tx = {
            "transaction_id": "tx_001",
            "amount": 1000000.0,
            "currency": "USD",
            "country": "US",
            "mcc": "5411",
            "timestamp": "2026-05-09T14:30:00+00:00",
        }
        result = TransactionValidator.validate_transaction(invalid_tx)
        assert result["valid"] is False
        assert any("amount" in error for error in result["errors"])

    def test_invalid_country(self):
        """Test validation of invalid country code."""
        invalid_tx = {
            "transaction_id": "tx_001",
            "amount": 150.0,
            "currency": "USD",
            "country": "XX",
            "mcc": "5411",
            "timestamp": "2026-05-09T14:30:00+00:00",
        }
        result = TransactionValidator.validate_transaction(invalid_tx)
        assert result["valid"] is False
        assert any("country" in error for error in result["errors"])

    def test_invalid_mcc(self):
        """Test validation of invalid MCC code."""
        invalid_tx = {
            "transaction_id": "tx_001",
            "amount": 150.0,
            "currency": "USD",
            "country": "US",
            "mcc": "invalid",
            "timestamp": "2026-05-09T14:30:00+00:00",
        }
        result = TransactionValidator.validate_transaction(invalid_tx)
        assert result["valid"] is False
        assert any("mcc" in error for error in result["errors"])

    def test_invalid_timestamp(self):
        """Test validation of invalid timestamp."""
        invalid_tx = {
            "transaction_id": "tx_001",
            "amount": 150.0,
            "currency": "USD",
            "country": "US",
            "mcc": "5411",
            "timestamp": "invalid-date",
        }
        result = TransactionValidator.validate_transaction(invalid_tx)
        assert result["valid"] is False
        assert any("timestamp" in error for error in result["errors"])

    def test_invalid_ip_address(self):
        """Test validation of invalid IP address."""
        invalid_tx = {
            "transaction_id": "tx_001",
            "amount": 150.0,
            "currency": "USD",
            "country": "US",
            "mcc": "5411",
            "timestamp": "2026-05-09T14:30:00+00:00",
            "ip_address": "999.999.999.999",
        }
        result = TransactionValidator.validate_transaction(invalid_tx)
        assert result["valid"] is False
        assert any("ip_address" in error for error in result["errors"])

    def test_validation_summary_valid(self):
        """Test validation summary for valid transaction."""
        valid_tx = {
            "transaction_id": "tx_001",
            "amount": 150.0,
            "currency": "USD",
            "country": "US",
            "mcc": "5411",
            "timestamp": "2026-05-09T14:30:00+00:00",
        }
        result = TransactionValidator.validate_transaction(valid_tx)
        summary = TransactionValidator.get_validation_summary(result)
        assert "valid" in summary.lower()

    def test_validation_summary_invalid(self):
        """Test validation summary for invalid transaction."""
        invalid_tx = {
            "amount": -100.0,
            "timestamp": "invalid",
        }
        result = TransactionValidator.validate_transaction(invalid_tx)
        summary = TransactionValidator.get_validation_summary(result)
        assert "error" in summary.lower()
