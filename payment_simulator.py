"""Payment simulation engine for generating, validating, and recording simulated payments.
Guarantees strict input validation and duplicate prevention.
"""

import uuid
import random
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple

import database
from blockchain_ledger import calculate_block_hash
from config import GENESIS_PREV_HASH, PAYMENT_METHODS

# Re-entrant lock to guarantee atomic read-hash-insert sequencing across concurrent threads
LEDGER_LOCK = threading.RLock()

SAMPLE_SENDERS = [
    "Aarav Sharma (aarav@oksbi)",
    "Priya Patel (priya@icici)",
    "Rohan Verma (rohan@paytm)",
    "Ananya Iyer (ananya@hdfcbank)",
    "Vikram Singh (vikram@axisbank)",
    "Kavita Nair (kavita@barodampay)",
    "Rahul Deshmukh (rahul@ybl)",
    "Meera Joshi (meera@kotak)"
]

def generate_sample_tx_id(prefix: str = "SIM") -> str:
    """Generate a realistic simulated transaction ID."""
    today_str = datetime.now().strftime("%Y%m%d%H%M")
    rand_suffix = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{today_str}-{rand_suffix}"

def validate_payment_inputs(
    tx_id: str,
    sender: str,
    amount: Any,
    payment_method: str
) -> Tuple[bool, Optional[str], Optional[float]]:
    """Validate user inputs strictly according to project specifications.
    
    Returns:
        (is_valid, error_message, parsed_amount)
    """
    # 1. Transaction ID
    if not tx_id or not str(tx_id).strip():
        return False, "Transaction ID cannot be empty or whitespace.", None
    clean_tx_id = str(tx_id).strip()

    # 2. Sender identifier
    if not sender or not str(sender).strip():
        return False, "Sender name / identifier is required.", None

    # 3. Amount validation (must be positive number)
    try:
        parsed_amount = float(amount)
    except (ValueError, TypeError):
        return False, "Payment amount must be a valid numeric value.", None

    if parsed_amount <= 0:
        return False, "Payment amount must be strictly greater than zero (positive).", None

    if parsed_amount > 10_000_000:
        return False, "Payment amount exceeds simulated ceiling of ₹10,000,000.", None

    # 4. Payment method validation
    if payment_method not in PAYMENT_METHODS:
        return False, f"Invalid payment method. Must be one of: {', '.join(PAYMENT_METHODS)}", None

    return True, None, parsed_amount

def record_simulated_payment(
    tx_id: str,
    sender: str,
    amount: float,
    payment_method: str,
    timestamp: Optional[str] = None,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Validate, hash, and record a new simulated payment into the persistent ledger.
    
    Thread-safe and race-condition free: uses LEDGER_LOCK to atomically determine
    the block index and parent hash, compute the SHA-256 digest, and insert into SQLite.
    """
    clean_tx_id = str(tx_id).strip()
    clean_sender = str(sender).strip()

    # Step 1: Input validation (pre-lock check)
    is_valid, err_msg, parsed_amount = validate_payment_inputs(
        clean_tx_id, clean_sender, amount, payment_method
    )
    if not is_valid:
        return {
            "success": False,
            "error_code": "INVALID_INPUT",
            "message": err_msg,
            "record": None
        }

    # Acquire lock for atomic ledger append
    with LEDGER_LOCK:
        # Step 2: Duplicate check
        existing = database.get_record_by_tx_id(clean_tx_id, db_path=db_path)
        if existing is not None:
            return {
                "success": False,
                "error_code": "DUPLICATE_TX_ID",
                "message": f"Rejected: Transaction ID '{clean_tx_id}' already exists in ledger. Duplicates are forbidden.",
                "record": None
            }

        # Step 3: Determine block index and previous hash atomically
        last_block = database.get_last_record(db_path=db_path)
        if last_block is None:
            block_index = 1
            prev_hash = GENESIS_PREV_HASH
        else:
            block_index = last_block["block_index"] + 1
            prev_hash = last_block["current_hash"]

        # Step 4: Timestamp resolution
        if timestamp is None:
            current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        else:
            current_time = str(timestamp).strip()

        # Step 5: Compute deterministic SHA-256 hash
        block_hash = calculate_block_hash(
            block_index=block_index,
            tx_id=clean_tx_id,
            sender=clean_sender,
            amount=parsed_amount,
            payment_method=payment_method,
            timestamp=current_time,
            prev_hash=prev_hash
        )

        # Step 6: Construct and insert record explicitly with block_index
        record = {
            "block_index": block_index,
            "tx_id": clean_tx_id,
            "sender": clean_sender,
            "amount": parsed_amount,
            "payment_method": payment_method,
            "timestamp": current_time,
            "prev_hash": prev_hash,
            "current_hash": block_hash,
            "status": "CONFIRMED"
        }

        try:
            database.insert_record(record, db_path=db_path)
        except Exception as e:
            return {
                "success": False,
                "error_code": "DB_INSERT_ERROR",
                "message": f"Failed to persist block into database: {str(e)}",
                "record": None
            }

        return {
            "success": True,
            "error_code": None,
            "message": f"Simulated transaction successfully confirmed and committed to Block #{block_index}.",
            "record": record
        }

def generate_random_sample_payload() -> Dict[str, Any]:
    """Generate realistic random data for a simulated payment demonstration."""
    sample_amounts = [100.0, 250.0, 500.0, 1200.0, 2450.0, 5000.0, 780.0, 15000.0]
    return {
        "tx_id": generate_sample_tx_id(),
        "sender": random.choice(SAMPLE_SENDERS),
        "amount": random.choice(sample_amounts),
        "payment_method": random.choice(PAYMENT_METHODS),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }

def seed_default_sample_transactions(count: int = 5, db_path: Optional[str] = None) -> int:
    """Pre-populate the database with sequential sample records if empty."""
    with LEDGER_LOCK:
        records_added = 0
        for _ in range(count):
            payload = generate_random_sample_payload()
            res = record_simulated_payment(
                tx_id=payload["tx_id"],
                sender=payload["sender"],
                amount=payload["amount"],
                payment_method=payload["payment_method"],
                timestamp=payload["timestamp"],
                db_path=db_path
            )
            if res["success"]:
                records_added += 1
        return records_added
