"""Tests for blockchain hash-linked ledger integrity, deterministic hashing, and tampering detection."""

import os
import pytest
import tempfile
import sqlite3

import database
from blockchain_ledger import (
    calculate_block_hash,
    verify_ledger_integrity,
    verify_single_block_hash
)
from payment_simulator import record_simulated_payment
from config import GENESIS_PREV_HASH

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

def test_correct_hash_generation_determinism():
    """Test that hashing identical data always yields the exact same SHA-256 digest."""
    hash1 = calculate_block_hash(
        block_index=1,
        tx_id="TX-FIXED-01",
        sender="Aarav Sharma",
        amount=500.0,
        payment_method="UPI QR Scan",
        timestamp="2026-10-22 10:00:00 UTC",
        prev_hash=GENESIS_PREV_HASH
    )
    hash2 = calculate_block_hash(
        block_index=1,
        tx_id="TX-FIXED-01",
        sender="Aarav Sharma",
        amount=500.00,  # float representation
        payment_method="UPI QR Scan",
        timestamp="2026-10-22 10:00:00 UTC",
        prev_hash=GENESIS_PREV_HASH
    )
    assert hash1 == hash2
    assert len(hash1) == 64
    assert isinstance(hash1, str)

def test_genesis_hash_linkage(temp_db):
    """Test that the first block links strictly to the predefined genesis previous hash."""
    res = record_simulated_payment(
        tx_id="GENESIS-TX-001",
        sender="Alice",
        amount=100.0,
        payment_method="UPI QR Scan",
        db_path=temp_db
    )
    assert res["success"] is True
    record = database.get_last_record(db_path=temp_db)
    assert record["block_index"] == 1
    assert record["prev_hash"] == GENESIS_PREV_HASH

def test_correct_previous_hash_linkage(temp_db):
    """Test that each subsequent block references the previous block's current_hash."""
    # Insert block 1
    res1 = record_simulated_payment("TX-SEQ-1", "Alice", 100.0, "UPI QR Scan", db_path=temp_db)
    # Insert block 2
    res2 = record_simulated_payment("TX-SEQ-2", "Bob", 200.0, "Simulated Debit Card", db_path=temp_db)
    # Insert block 3
    res3 = record_simulated_payment("TX-SEQ-3", "Charlie", 300.0, "UPI VPA (Simulated)", db_path=temp_db)

    records = database.get_all_records(db_path=temp_db)
    assert len(records) == 3

    # Verify Block 2 prev_hash == Block 1 current_hash
    assert records[1]["prev_hash"] == records[0]["current_hash"]
    # Verify Block 3 prev_hash == Block 2 current_hash
    assert records[2]["prev_hash"] == records[1]["current_hash"]

def test_valid_ledger_verification(temp_db):
    """Test that an untampered ledger passes full cryptographic audit."""
    for i in range(1, 5):
        record_simulated_payment(f"TX-AUDIT-{i}", f"User {i}", i * 150.0, "UPI QR Scan", db_path=temp_db)

    records = database.get_all_records(db_path=temp_db)
    report = verify_ledger_integrity(records)

    assert report["is_valid"] is True
    assert report["total_blocks"] == 4
    assert report["valid_blocks"] == 4
    assert len(report["tampered_blocks"]) == 0
    assert len(report["broken_links"]) == 0
    assert len(report["errors"]) == 0

def test_detection_of_modified_transaction_data(temp_db):
    """Test that modifying a transaction payload in the database is detected immediately."""
    for i in range(1, 4):
        record_simulated_payment(f"TX-MOD-{i}", f"User {i}", i * 100.0, "UPI QR Scan", db_path=temp_db)

    # Tamper with Block 2 amount directly in SQLite (simulating an unauthorized edit)
    conn = database.get_connection(temp_db)
    with conn:
        conn.execute("UPDATE ledger_records SET amount = 99999.0 WHERE block_index = 2;")
    conn.close()

    records = database.get_all_records(db_path=temp_db)
    report = verify_ledger_integrity(records)

    assert report["is_valid"] is False
    assert 2 in report["tampered_blocks"]
    assert any("Data Tampering Detected in Block #2" in err for err in report["errors"])

def test_detection_of_broken_hash_links(temp_db):
    """Test that an alteration to a prev_hash pointer is caught as a broken hash link."""
    for i in range(1, 4):
        record_simulated_payment(f"TX-LINK-{i}", f"User {i}", i * 100.0, "UPI QR Scan", db_path=temp_db)

    # Corrupt Block 3's prev_hash pointer
    conn = database.get_connection(temp_db)
    with conn:
        conn.execute("UPDATE ledger_records SET prev_hash = 'badhash123' WHERE block_index = 3;")
    conn.close()

    records = database.get_all_records(db_path=temp_db)
    report = verify_ledger_integrity(records)

    assert report["is_valid"] is False
    assert (2, 3) in report["broken_links"]
    assert any("Broken Hash Link between Block #2 and Block #3" in err for err in report["errors"])

def test_database_persistence_across_reconnect(temp_db):
    """Test that records persist safely across database reconnections and process cycles."""
    # Insert record
    res = record_simulated_payment("TX-PERSIST-1", "Aarav", 850.0, "UPI QR Scan", db_path=temp_db)
    assert res["success"] is True

    # Re-open completely fresh connection to same db file
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ledger_records WHERE tx_id = ?", ("TX-PERSIST-1",))
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row["tx_id"] == "TX-PERSIST-1"
    assert row["amount"] == 850.0
    assert row["sender"] == "Aarav"

def test_concurrent_multi_threaded_payment_simulation(temp_db):
    """Test that concurrent simulation from multiple threads maintains 100% cryptographic integrity without race conditions."""
    import concurrent.futures

    def simulate_tx(i):
        return record_simulated_payment(
            tx_id=f"TX-CONCURRENT-{i}",
            sender=f"Thread-User-{i}",
            amount=100.0 + i,
            payment_method="UPI QR Scan",
            db_path=temp_db
        )

    # Launch 10 concurrent threads simultaneously
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(simulate_tx, range(1, 11)))

    assert all(r["success"] is True for r in results)

    # Verify that all 10 records form a strictly sequential, unbroken cryptographic chain
    records = database.get_all_records(db_path=temp_db)
    assert len(records) == 10

    # Verify sequence indices are strictly 1..10
    indices = [r["block_index"] for r in records]
    assert indices == list(range(1, 11))

    # Verify full cryptographic integrity
    report = verify_ledger_integrity(records)
    assert report["is_valid"] is True
    assert report["valid_blocks"] == 10
    assert report["total_blocks"] == 10
    assert len(report["tampered_blocks"]) == 0
    assert len(report["broken_links"]) == 0
    assert len(report["errors"]) == 0

