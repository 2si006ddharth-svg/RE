"""Unit and integration tests for payment simulation and soundbox announcement."""

import os
import pytest
import tempfile
from pathlib import Path

import database
from payment_simulator import (
    validate_payment_inputs,
    record_simulated_payment,
    generate_sample_tx_id
)
from soundbox import (
    format_announcement_text,
    format_full_speech_sentence,
    trigger_verified_soundbox_announcement
)

@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for test isolation."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    database.init_db(path)
    yield path
    try:
        os.remove(path)
    except OSError:
        pass

def test_successful_simulated_payment_creation(temp_db):
    """Test that valid input results in a successfully confirmed transaction."""
    tx_id = "TEST-TX-SUCCESS-01"
    sender = "Aarav Sharma"
    amount = 500.0
    payment_method = "UPI QR Scan"

    result = record_simulated_payment(
        tx_id=tx_id,
        sender=sender,
        amount=amount,
        payment_method=payment_method,
        db_path=temp_db
    )

    assert result["success"] is True
    assert result["error_code"] is None
    assert result["record"] is not None
    assert result["record"]["block_index"] == 1
    assert result["record"]["amount"] == 500.0
    assert result["record"]["tx_id"] == tx_id
    assert len(result["record"]["current_hash"]) == 64

    # Verify stored in DB
    stored = database.get_record_by_tx_id(tx_id, db_path=temp_db)
    assert stored is not None
    assert stored["tx_id"] == tx_id

def test_invalid_amount_rejection_negative_and_zero():
    """Test that zero, negative amounts, and invalid types are rejected."""
    # Zero amount
    is_valid, msg, _ = validate_payment_inputs("TX-1", "Aarav", 0, "UPI QR Scan")
    assert is_valid is False
    assert "strictly greater than zero" in msg

    # Negative amount
    is_valid, msg, _ = validate_payment_inputs("TX-2", "Aarav", -150.50, "UPI QR Scan")
    assert is_valid is False
    assert "strictly greater than zero" in msg

    # Non-numeric string
    is_valid, msg, _ = validate_payment_inputs("TX-3", "Aarav", "not_a_number", "UPI QR Scan")
    assert is_valid is False
    assert "valid numeric value" in msg

def test_empty_transaction_id_rejection():
    """Test that empty or whitespace-only transaction IDs are rejected."""
    # Empty string
    is_valid, msg, _ = validate_payment_inputs("", "Aarav", 500.0, "UPI QR Scan")
    assert is_valid is False
    assert "Transaction ID cannot be empty" in msg

    # Whitespace only
    is_valid, msg, _ = validate_payment_inputs("    ", "Aarav", 500.0, "UPI QR Scan")
    assert is_valid is False
    assert "Transaction ID cannot be empty" in msg

    # Empty sender
    is_valid, msg, _ = validate_payment_inputs("TX-123", "", 500.0, "UPI QR Scan")
    assert is_valid is False
    assert "Sender name / identifier is required" in msg

def test_duplicate_transaction_id_rejection(temp_db):
    """Test that attempting to insert a duplicate transaction ID fails."""
    tx_id = "DUPLICATE-TX-999"
    # First payment succeeds
    res1 = record_simulated_payment(
        tx_id=tx_id,
        sender="User A",
        amount=250.0,
        payment_method="UPI QR Scan",
        db_path=temp_db
    )
    assert res1["success"] is True

    # Duplicate payment must be rejected
    res2 = record_simulated_payment(
        tx_id=tx_id,
        sender="User B",
        amount=500.0,
        payment_method="UPI QR Scan",
        db_path=temp_db
    )
    assert res2["success"] is False
    assert res2["error_code"] == "DUPLICATE_TX_ID"
    assert "already exists in ledger" in res2["message"]

def test_soundbox_announcement_formatting():
    """Test formatting of soundbox announcement messages."""
    # Integer amount
    text_500 = format_announcement_text(500.0)
    assert text_500 == "Payment received: 500 rupees."

    speech_500 = format_full_speech_sentence(500.0)
    assert "500 rupees" in speech_500

    # Float amount with cents / paisa
    text_1250_50 = format_announcement_text(1250.50)
    assert text_1250_50 == "Payment received: 1,250.50 rupees."

def test_soundbox_unverified_guard():
    """Test that soundbox refuses to announce an unverified transaction."""
    fake_record = {"amount": 500.0, "tx_id": "FAKE-TX"}
    result = trigger_verified_soundbox_announcement(fake_record, is_verified=False)
    assert result["success"] is False
    assert "Security Guard Triggered" in result["message"]
    assert "Payment validation failed" in result["announcement_text"]

def test_soundbox_hindi_announcement_formatting():
    """Test formatting of Hindi soundbox announcements."""
    hi_text = format_announcement_text(500.0, lang="hi")
    assert "पेमेंट प्राप्त हुआ" in hi_text
    assert "500" in hi_text

    hi_speech = format_full_speech_sentence(500.0, lang="hi")
    assert "सफलता पूर्वक प्राप्त हुए" in hi_speech

