"""Blockchain-style hash-linked ledger engine.
Provides canonical serialization, SHA-256 cryptographic hashing,
and deterministic verification for sequential blocks.
"""

import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from config import GENESIS_PREV_HASH

def serialize_block_payload(
    block_index: int,
    tx_id: str,
    sender: str,
    amount: float,
    payment_method: str,
    timestamp: str,
    prev_hash: str
) -> bytes:
    """Produce a deterministic, canonical JSON byte representation of a block's data."""
    canonical_dict = {
        "amount": f"{round(float(amount), 2):.2f}",
        "block_index": int(block_index),
        "payment_method": str(payment_method).strip(),
        "prev_hash": str(prev_hash).strip().lower(),
        "sender": str(sender).strip(),
        "timestamp": str(timestamp).strip(),
        "tx_id": str(tx_id).strip(),
    }
    # sort_keys=True and compact separators ensure deterministic serialization
    return json.dumps(canonical_dict, sort_keys=True, separators=(",", ":")).encode("utf-8")

def calculate_block_hash(
    block_index: int,
    tx_id: str,
    sender: str,
    amount: float,
    payment_method: str,
    timestamp: str,
    prev_hash: str
) -> str:
    """Calculate the SHA-256 cryptographic digest of canonical block data."""
    raw_bytes = serialize_block_payload(
        block_index=block_index,
        tx_id=tx_id,
        sender=sender,
        amount=amount,
        payment_method=payment_method,
        timestamp=timestamp,
        prev_hash=prev_hash
    )
    return hashlib.sha256(raw_bytes).hexdigest().lower()

def verify_single_block_hash(block: Dict[str, Any]) -> Tuple[bool, str]:
    """Verify if a block's recorded current_hash matches its recalculated SHA-256 hash.
    
    Returns:
        (is_valid, computed_hash)
    """
    computed = calculate_block_hash(
        block_index=block["block_index"],
        tx_id=block["tx_id"],
        sender=block["sender"],
        amount=block["amount"],
        payment_method=block["payment_method"],
        timestamp=block["timestamp"],
        prev_hash=block["prev_hash"]
    )
    stored = str(block.get("current_hash", "")).strip().lower()
    return (computed == stored, computed)

def verify_ledger_integrity(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Perform a complete cryptographic integrity audit across the full sequence of blocks.
    
    Checks:
    1. First block points to GENESIS_PREV_HASH.
    2. Each block's current_hash matches recalculation from stored payload (data integrity).
    3. Each subsequent block's prev_hash matches the previous block's current_hash (link continuity).
    """
    total = len(records)
    if total == 0:
        return {
            "is_valid": True,
            "total_blocks": 0,
            "valid_blocks": 0,
            "tampered_blocks": [],
            "broken_links": [],
            "errors": [],
            "first_failure_index": None,
            "details": []
        }

    errors: List[str] = []
    tampered_blocks: List[int] = []
    broken_links: List[Tuple[int, int]] = []
    block_audit_details: List[Dict[str, Any]] = []
    first_failure_index: Optional[int] = None

    for i, block in enumerate(records):
        b_idx = block["block_index"]
        is_hash_valid, recomputed_hash = verify_single_block_hash(block)
        link_valid = True
        link_error_msg = None

        # Check genesis link
        if i == 0:
            expected_prev = GENESIS_PREV_HASH.lower()
            if block["prev_hash"].lower() != expected_prev:
                link_valid = False
                err = (
                    f"Genesis Block #{b_idx} (Tx: {block['tx_id']}) has invalid prev_hash: "
                    f"Expected {expected_prev}, found {block['prev_hash']}."
                )
                errors.append(err)
                broken_links.append((0, b_idx))
                if first_failure_index is None:
                    first_failure_index = b_idx
        else:
            prev_block = records[i - 1]
            expected_prev = prev_block["current_hash"].lower()
            if block["prev_hash"].lower() != expected_prev:
                link_valid = False
                err = (
                    f"Broken Hash Link between Block #{prev_block['block_index']} and Block #{b_idx}. "
                    f"Block #{b_idx} references prev_hash '{block['prev_hash'][:16]}...', "
                    f"but preceding Block #{prev_block['block_index']} has current_hash '{expected_prev[:16]}...'."
                )
                errors.append(err)
                broken_links.append((prev_block["block_index"], b_idx))
                if first_failure_index is None:
                    first_failure_index = b_idx

        # Check data payload integrity
        if not is_hash_valid:
            err = (
                f"Data Tampering Detected in Block #{b_idx} (Tx: {block['tx_id']}). "
                f"Stored hash '{block['current_hash'][:16]}...' does not match "
                f"recomputed SHA-256 hash '{recomputed_hash[:16]}...'."
            )
            errors.append(err)
            tampered_blocks.append(b_idx)
            if first_failure_index is None:
                first_failure_index = b_idx

        block_status = is_hash_valid and link_valid
        block_audit_details.append({
            "block_index": b_idx,
            "tx_id": block["tx_id"],
            "sender": block["sender"],
            "amount": block["amount"],
            "stored_hash": block["current_hash"],
            "recomputed_hash": recomputed_hash,
            "prev_hash": block["prev_hash"],
            "is_hash_valid": is_hash_valid,
            "is_link_valid": link_valid,
            "status": "VALID" if block_status else "FAILED"
        })

    is_overall_valid = len(errors) == 0
    valid_count = sum(1 for b in block_audit_details if b["status"] == "VALID")

    return {
        "is_valid": is_overall_valid,
        "total_blocks": total,
        "valid_blocks": valid_count,
        "tampered_blocks": tampered_blocks,
        "broken_links": broken_links,
        "errors": errors,
        "first_failure_index": first_failure_index,
        "details": block_audit_details
    }

def explain_architecture_difference() -> Dict[str, str]:
    """Educational comparison between single-machine hash-linked ledger and decentralized blockchain."""
    return {
        "prototype_ledger": (
            "This software prototype utilizes a cryptographic hash-linked ledger stored in SQLite. "
            "Every block is linked via SHA-256 hashes, ensuring that any retro-active change to "
            "prior transaction amounts, timestamps, or sender names immediately invalidates all subsequent block hashes."
        ),
        "decentralized_blockchain": (
            "In contrast, a true decentralized blockchain (like Ethereum or Bitcoin) combines cryptographic hash links "
            "with a distributed peer-to-peer network, consensus algorithms (Proof of Stake/Work), and economic incentives. "
            "On a single machine, a privileged system administrator could theoretically recalculate all hashes forwards; "
            "whereas a decentralized network prevents this by requiring network-wide consensus."
        ),
        "soundbox_context": (
            "Digital payment soundboxes in production use encrypted network protocols and merchant cloud confirmation "
            "to announce payments. This simulator demonstrates how cryptographically anchored records verify "
            "that the payment event was recorded immutably in the local merchant audit trail."
        )
    }
