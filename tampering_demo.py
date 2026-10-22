"""Isolated Tampering Sandbox.
Provides controlled demonstration of cryptographic tampering without modifying
the production SQLite database.
"""

import copy
from typing import List, Dict, Any, Tuple
from blockchain_ledger import (
    calculate_block_hash,
    verify_ledger_integrity,
    serialize_block_payload
)
from config import GENESIS_PREV_HASH

def create_sample_sandbox_chain() -> List[Dict[str, Any]]:
    """Create a guaranteed-valid, isolated 4-block blockchain chain in memory."""
    chain: List[Dict[str, Any]] = []

    samples = [
        {"tx_id": "DEMO-TX-1001", "sender": "Aarav Sharma (Merchant A)", "amount": 500.0, "payment_method": "UPI QR Scan", "timestamp": "2026-10-22 10:00:00 UTC"},
        {"tx_id": "DEMO-TX-1002", "sender": "Priya Patel (Merchant A)", "amount": 1200.0, "payment_method": "UPI VPA (Simulated)", "timestamp": "2026-10-22 10:05:00 UTC"},
        {"tx_id": "DEMO-TX-1003", "sender": "Rohan Verma (Merchant A)", "amount": 2450.0, "payment_method": "Simulated Debit Card", "timestamp": "2026-10-22 10:10:00 UTC"},
        {"tx_id": "DEMO-TX-1004", "sender": "Ananya Iyer (Merchant A)", "amount": 780.0, "payment_method": "Simulated Digital Wallet", "timestamp": "2026-10-22 10:15:00 UTC"}
    ]

    prev_hash = GENESIS_PREV_HASH
    for idx, item in enumerate(samples, start=1):
        cur_hash = calculate_block_hash(
            block_index=idx,
            tx_id=item["tx_id"],
            sender=item["sender"],
            amount=item["amount"],
            payment_method=item["payment_method"],
            timestamp=item["timestamp"],
            prev_hash=prev_hash
        )
        block = {
            "block_index": idx,
            "tx_id": item["tx_id"],
            "sender": item["sender"],
            "amount": item["amount"],
            "payment_method": item["payment_method"],
            "timestamp": item["timestamp"],
            "prev_hash": prev_hash,
            "current_hash": cur_hash,
            "status": "CONFIRMED"
        }
        chain.append(block)
        prev_hash = cur_hash

    return chain

def apply_simulated_tamper(
    chain: List[Dict[str, Any]],
    target_block_index: int,
    tamper_field: str,
    new_value: Any
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Modify a specific record in an isolated copy of the chain.
    
    Returns:
        (tampered_chain, tamper_metadata)
    """
    tampered_chain = copy.deepcopy(chain)
    target_block = None

    for b in tampered_chain:
        if b["block_index"] == target_block_index:
            target_block = b
            break

    if target_block is None:
        raise ValueError(f"Block #{target_block_index} does not exist in chain.")

    original_value = target_block.get(tamper_field)
    
    # Apply modification
    if tamper_field == "amount":
        target_block["amount"] = float(new_value)
    else:
        target_block[tamper_field] = str(new_value)

    # Compute what the hash would be now
    recomputed_hash = calculate_block_hash(
        block_index=target_block["block_index"],
        tx_id=target_block["tx_id"],
        sender=target_block["sender"],
        amount=target_block["amount"],
        payment_method=target_block["payment_method"],
        timestamp=target_block["timestamp"],
        prev_hash=target_block["prev_hash"]
    )

    metadata = {
        "target_block_index": target_block_index,
        "tamper_field": tamper_field,
        "original_value": original_value,
        "tampered_value": new_value,
        "original_stored_hash": target_block["current_hash"],
        "recomputed_new_hash": recomputed_hash,
        "hash_difference": (target_block["current_hash"] != recomputed_hash)
    }

    return tampered_chain, metadata

def recompute_subsequent_hashes(
    tampered_chain: List[Dict[str, Any]],
    start_block_index: int
) -> List[Dict[str, Any]]:
    """Simulate an attacker attempting to rewrite the chain from start_block_index forward.
    Demonstrates the computational cascading re-hashing effect.
    """
    rewritten_chain = copy.deepcopy(tampered_chain)
    
    for i in range(len(rewritten_chain)):
        b = rewritten_chain[i]
        b_idx = b["block_index"]
        if b_idx < start_block_index:
            continue

        # For start_block_index, recompute its current_hash
        if b_idx == start_block_index:
            b["current_hash"] = calculate_block_hash(
                block_index=b["block_index"],
                tx_id=b["tx_id"],
                sender=b["sender"],
                amount=b["amount"],
                payment_method=b["payment_method"],
                timestamp=b["timestamp"],
                prev_hash=b["prev_hash"]
            )
        else:
            # Update prev_hash to previous block's newly rewritten hash
            prev_b = rewritten_chain[i - 1]
            b["prev_hash"] = prev_b["current_hash"]
            b["current_hash"] = calculate_block_hash(
                block_index=b["block_index"],
                tx_id=b["tx_id"],
                sender=b["sender"],
                amount=b["amount"],
                payment_method=b["payment_method"],
                timestamp=b["timestamp"],
                prev_hash=b["prev_hash"]
            )

    return rewritten_chain
