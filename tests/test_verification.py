"""Tests for transaction and full-ledger verification services."""

import os
import pytest
import tempfile

import database
from payment_simulator import record_simulated_payment
from verification import (
    verify_single_transaction_by_id,
    verify_full_ledger_system,
    get_cryptographic_limitation_notice
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

def test_single_transaction_verification_valid(temp_db):
    """Test verification of an intact recorded transaction."""
    tx_id = "VERIFY-TX-OK-1"
    record_simulated_payment(tx_id, "Priya", 1500.0, "UPI QR Scan", db_path=temp_db)

    result = verify_single_transaction_by_id(tx_id, db_path=temp_db)
    assert result["is_verified"] is True
    assert result["hash_match"] is True
    assert result["link_match"] is True
    assert result["error_reason"] is None
    assert "cryptographically VALID" in result["explanation"]
    assert "CRITICAL LIMITATION" in result["limitation_notice"]

def test_single_transaction_verification_nonexistent(temp_db):
    """Test verification of a transaction ID that was never recorded."""
    result = verify_single_transaction_by_id("DOES-NOT-EXIST-999", db_path=temp_db)
    assert result["is_verified"] is False
    assert result["record"] is None
    assert "not found in ledger" in result["error_reason"]

def test_tampered_transaction_fails_verification(temp_db):
    """Test that if a transaction record is modified in DB, verification reports failure."""
    tx_id = "TAMPER-TARGET-TX"
    record_simulated_payment(tx_id, "Rohan", 2500.0, "UPI QR Scan", db_path=temp_db)

    # Manually modify amount in database without re-hashing
    conn = database.get_connection(temp_db)
    with conn:
        conn.execute("UPDATE ledger_records SET amount = 50000.0 WHERE tx_id = ?", (tx_id,))
    conn.close()

    result = verify_single_transaction_by_id(tx_id, db_path=temp_db)
    assert result["is_verified"] is False
    assert result["hash_match"] is False
    assert "Data payload mismatch" in result["error_reason"]

def test_full_database_verification(temp_db):
    """Test complete ledger audit report on multiple records."""
    record_simulated_payment("TX-1", "Alice", 100.0, "UPI QR Scan", db_path=temp_db)
    record_simulated_payment("TX-2", "Bob", 200.0, "UPI QR Scan", db_path=temp_db)

    audit = verify_full_ledger_system(db_path=temp_db)
    assert audit["is_valid"] is True
    assert audit["total_blocks"] == 2
    assert audit["valid_blocks"] == 2
    assert "CRITICAL LIMITATION" in audit["limitation_notice"]

def test_diagnostic_report_on_valid_ledger(temp_db):
    """Test that generate_diagnostic_report reports valid state on clean ledger."""
    from verification import generate_diagnostic_report
    record_simulated_payment("TX-OK-1", "Alice", 100.0, "UPI QR Scan", db_path=temp_db)
    record_simulated_payment("TX-OK-2", "Bob", 200.0, "UPI QR Scan", db_path=temp_db)

    report = generate_diagnostic_report(db_path=temp_db)
    assert report["is_valid"] is True
    assert report["invalid_blocks_count"] == 0
    assert len(report["invalid_blocks"]) == 0
    assert report["counting_rules"]["total_blocks"] == 2
    assert report["counting_rules"]["valid_blocks"] == 2
    assert report["counting_rules"]["invalid_blocks"] == 0
    assert report["counting_rules"]["total_error_violations"] == 0

def test_diagnostic_report_on_tampered_payload_and_broken_link(temp_db):
    """Test detailed failure capture in generate_diagnostic_report."""
    from verification import generate_diagnostic_report
    record_simulated_payment("TX-FAIL-1", "Alice", 100.0, "UPI QR Scan", db_path=temp_db)
    record_simulated_payment("TX-FAIL-2", "Bob", 200.0, "UPI QR Scan", db_path=temp_db)
    record_simulated_payment("TX-FAIL-3", "Charlie", 300.0, "UPI QR Scan", db_path=temp_db)

    # Tamper with Block 2 amount and Block 3 prev_hash
    conn = database.get_connection(temp_db)
    with conn:
        conn.execute("UPDATE ledger_records SET amount = 9999.0 WHERE block_index = 2;")
        conn.execute("UPDATE ledger_records SET prev_hash = 'corrupted_pointer' WHERE block_index = 3;")
    conn.close()

    report = generate_diagnostic_report(db_path=temp_db)
    assert report["is_valid"] is False
    assert report["counting_rules"]["total_blocks"] == 3
    assert report["counting_rules"]["valid_blocks"] == 1  # Only block 1 is valid
    assert report["counting_rules"]["invalid_blocks"] == 2 # Blocks 2 and 3 invalid
    assert report["invalid_blocks_count"] == 2

    # Check Block 2 report details
    b2_rep = next(b for b in report["invalid_blocks"] if b["block_index"] == 2)
    assert "PAYLOAD_HASH_MISMATCH" in b2_rep["failed_rules"]
    assert b2_rep["stored_current_hash"] != b2_rep["recomputed_current_hash"]

    # Check Block 3 report details
    b3_rep = next(b for b in report["invalid_blocks"] if b["block_index"] == 3)
    assert "BROKEN_PREV_HASH_LINK" in b3_rep["failed_rules"]
    assert b3_rep["stored_prev_hash"] == "corrupted_pointer"

