"""Verification module for inspecting simulated transactions and audit ledger integrity.
Explains cryptographic guarantees and highlights real-world financial limitations.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional

import database
from blockchain_ledger import (
    verify_single_block_hash,
    verify_ledger_integrity,
    calculate_block_hash
)
from config import GENESIS_PREV_HASH

def get_cryptographic_limitation_notice() -> str:
    """Return explicit academic disclaimer regarding cryptographic hashing vs bank settlement."""
    return (
        "CRITICAL LIMITATION: A locally computed SHA-256 hash verifies mathematical integrity "
        "and sequential immutability within this software ledger. It DOES NOT prove that real money "
        "moved, nor does it replace bank authorization, NPCI switch settlement, or digital signatures "
        "from authorized payment service providers."
    )

def verify_single_transaction_by_id(
    tx_id: str,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Verify an individual transaction's data integrity and link against the database."""
    verification_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    clean_tx = str(tx_id).strip()
    if not clean_tx:
        return {
            "is_verified": False,
            "tx_id": clean_tx,
            "verification_timestamp": verification_time,
            "error_reason": "Empty transaction ID provided.",
            "explanation": "Cannot verify a transaction without a valid non-empty identifier.",
            "record": None,
            "hash_match": False,
            "link_match": False,
            "limitation_notice": get_cryptographic_limitation_notice()
        }

    record = database.get_record_by_tx_id(clean_tx, db_path=db_path)
    if record is None:
        return {
            "is_verified": False,
            "tx_id": clean_tx,
            "verification_timestamp": verification_time,
            "error_reason": "Transaction ID not found in ledger.",
            "explanation": f"The record with ID '{clean_tx}' does not exist in the database.",
            "record": None,
            "hash_match": False,
            "link_match": False,
            "limitation_notice": get_cryptographic_limitation_notice()
        }

    # Verify Hash of this block
    is_hash_valid, computed_hash = verify_single_block_hash(record)
    
    # Verify link with preceding block
    block_index = record["block_index"]
    link_match = False
    expected_prev = GENESIS_PREV_HASH.lower()

    if block_index == 1:
        link_match = (record["prev_hash"].lower() == expected_prev)
    else:
        # Fetch previous record
        all_records = database.get_all_records(db_path=db_path)
        matching_prev = [r for r in all_records if r["block_index"] == block_index - 1]
        if matching_prev:
            expected_prev = matching_prev[0]["current_hash"].lower()
            link_match = (record["prev_hash"].lower() == expected_prev)
        else:
            link_match = False

    is_verified = is_hash_valid and link_match
    
    # Formulate detailed explanation
    if is_verified:
        explanation = (
            f"Transaction '{clean_tx}' (Block #{block_index}) is cryptographically VALID. "
            f"Payload attributes match the stored SHA-256 hash, and previous link correctly binds to "
            f"preceding hash ({expected_prev[:16]}...)."
        )
        error_reason = None
    else:
        reasons = []
        if not is_hash_valid:
            reasons.append(
                f"Data payload mismatch: Stored hash '{record['current_hash'][:16]}...' does not match "
                f"recomputed hash '{computed_hash[:16]}...'."
            )
        if not link_match:
            reasons.append(
                f"Previous block linkage mismatch: Expected prev_hash '{expected_prev[:16]}...', "
                f"found '{record['prev_hash'][:16]}...'."
            )
        explanation = "Verification FAILED: " + " | ".join(reasons)
        error_reason = "; ".join(reasons)

    return {
        "is_verified": is_verified,
        "tx_id": clean_tx,
        "block_index": block_index,
        "verification_timestamp": verification_time,
        "error_reason": error_reason,
        "explanation": explanation,
        "stored_hash": record["current_hash"],
        "computed_hash": computed_hash,
        "stored_prev_hash": record["prev_hash"],
        "expected_prev_hash": expected_prev,
        "hash_match": is_hash_valid,
        "link_match": link_match,
        "record": record,
        "limitation_notice": get_cryptographic_limitation_notice()
    }

def verify_full_ledger_system(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Audit the entire persistent SQLite database."""
    records = database.get_all_records(db_path=db_path)
    audit_report = verify_ledger_integrity(records)
    audit_report["verification_timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    audit_report["limitation_notice"] = get_cryptographic_limitation_notice()
    return audit_report

def generate_diagnostic_report(
    records: Optional[list] = None,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Generate an in-depth cryptographic diagnostic report for the ledger.
    
    Provides detailed inspection for every invalid block:
    - Block Index & Transaction ID
    - Specific Failed Validation Rules
    - Stored vs Expected / Recomputed SHA-256 Hashes
    - Stored vs Expected Previous-Hash Pointers
    - Root-cause classification (Concurrency Race Discrepancy vs Intentional Mutation)
    - Clearly defined, consistent counting rules
    """
    if records is None:
        records = database.get_all_records(db_path=db_path)

    total_blocks = len(records)
    audit = verify_ledger_integrity(records)

    invalid_block_reports = []
    
    for i, block in enumerate(records):
        b_idx = block["block_index"]
        is_hash_valid, recomputed_hash = verify_single_block_hash(block)
        
        # Link check
        if i == 0:
            expected_prev = GENESIS_PREV_HASH.lower()
            link_valid = (block["prev_hash"].lower() == expected_prev)
            preceding_block = None
        else:
            preceding_block = records[i - 1]
            expected_prev = preceding_block["current_hash"].lower()
            link_valid = (block["prev_hash"].lower() == expected_prev)

        if not is_hash_valid or not link_valid:
            failed_rules = []
            if not is_hash_valid:
                failed_rules.append("PAYLOAD_HASH_MISMATCH")
            if not link_valid:
                failed_rules.append("BROKEN_PREV_HASH_LINK")

            # Check for concurrency race condition signature
            concurrency_note = None
            for probe_idx in range(1, b_idx + 1):
                # Test against preceding block hashes in the chain
                for probe_prev in [expected_prev, block["prev_hash"]]:
                    probe_hash = calculate_block_hash(
                        block_index=probe_idx,
                        tx_id=block["tx_id"],
                        sender=block["sender"],
                        amount=block["amount"],
                        payment_method=block["payment_method"],
                        timestamp=block["timestamp"],
                        prev_hash=probe_prev
                    )
                    if probe_hash.lower() == block["current_hash"].lower() and probe_idx != b_idx:
                        concurrency_note = (
                            f"Concurrency Race Condition Detected: Stored hash was calculated assuming "
                            f"block_index={probe_idx} with parent hash '{probe_prev[:16]}...', "
                            f"but was committed as block_index={b_idx} due to non-atomic insert."
                        )
                        break
                if concurrency_note:
                    break

            invalid_block_reports.append({
                "block_index": b_idx,
                "tx_id": block["tx_id"],
                "sender": block["sender"],
                "amount": block["amount"],
                "payment_method": block["payment_method"],
                "timestamp": block["timestamp"],
                "failed_rules": failed_rules,
                "is_hash_valid": is_hash_valid,
                "is_link_valid": link_valid,
                "stored_current_hash": block["current_hash"],
                "recomputed_current_hash": recomputed_hash,
                "stored_prev_hash": block["prev_hash"],
                "expected_prev_hash": expected_prev,
                "preceding_block_index": preceding_block["block_index"] if preceding_block else 0,
                "concurrency_race_detected": concurrency_note is not None,
                "root_cause_explanation": concurrency_note or "Data payload mutation or manual ledger tampering."
            })

    valid_blocks_count = audit["valid_blocks"]
    invalid_blocks_count = total_blocks - valid_blocks_count
    total_errors_count = len(audit["errors"])

    return {
        "report_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "is_valid": audit["is_valid"],
        "counting_rules": {
            "definition_of_valid_block": "A block is valid IF AND ONLY IF both its payload SHA-256 matches AND its prev_hash matches predecessor.",
            "total_blocks": total_blocks,
            "valid_blocks": valid_blocks_count,
            "invalid_blocks": invalid_blocks_count,
            "total_error_violations": total_errors_count,
            "tampered_payload_count": len(audit["tampered_blocks"]),
            "broken_link_count": len(audit["broken_links"])
        },
        "invalid_blocks_count": invalid_blocks_count,
        "invalid_blocks": invalid_block_reports,
        "raw_errors": audit["errors"],
        "limitation_notice": get_cryptographic_limitation_notice()
    }

