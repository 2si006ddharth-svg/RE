"""Database module for SQLite storage of simulated payments and ledger blocks.
Uses parameterized queries to safeguard data integrity and prevent injection.
"""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from config import DB_PATH

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create and return a configured SQLite connection."""
    target_path = db_path if db_path is not None else DB_PATH
    conn = sqlite3.connect(target_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrency and foreign keys
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db(db_path: Optional[str] = None) -> None:
    """Initialize the ledger_records table and indexes."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ledger_records (
                    block_index INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_id TEXT UNIQUE NOT NULL,
                    sender TEXT NOT NULL,
                    amount REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    prev_hash TEXT NOT NULL,
                    current_hash TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'CONFIRMED',
                    created_at TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_ledger_tx_id 
                ON ledger_records(tx_id);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ledger_timestamp 
                ON ledger_records(timestamp);
            """)
    finally:
        conn.close()

def insert_record(record: Dict[str, Any], db_path: Optional[str] = None) -> int:
    """Insert a new validated and hashed block into the ledger using parameterized SQL.
    Explicitly stores block_index to enforce exact matching between hashed index and stored index.
    """
    conn = get_connection(db_path)
    created_at = datetime.now(timezone.utc).isoformat()
    try:
        with conn:
            if "block_index" in record and record["block_index"] is not None:
                cursor = conn.execute("""
                    INSERT INTO ledger_records (
                        block_index, tx_id, sender, amount, payment_method, 
                        timestamp, prev_hash, current_hash, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    int(record["block_index"]),
                    record["tx_id"],
                    record["sender"],
                    float(record["amount"]),
                    record["payment_method"],
                    record["timestamp"],
                    record["prev_hash"],
                    record["current_hash"],
                    record.get("status", "CONFIRMED"),
                    created_at
                ))
            else:
                cursor = conn.execute("""
                    INSERT INTO ledger_records (
                        tx_id, sender, amount, payment_method, 
                        timestamp, prev_hash, current_hash, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    record["tx_id"],
                    record["sender"],
                    float(record["amount"]),
                    record["payment_method"],
                    record["timestamp"],
                    record["prev_hash"],
                    record["current_hash"],
                    record.get("status", "CONFIRMED"),
                    created_at
                ))
            return cursor.lastrowid
    finally:
        conn.close()

def get_all_records(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all ledger records ordered by block_index ascending."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("""
            SELECT block_index, tx_id, sender, amount, payment_method,
                   timestamp, prev_hash, current_hash, status, created_at
            FROM ledger_records
            ORDER BY block_index ASC;
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_record_by_tx_id(tx_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetch a single transaction record by its unique tx_id."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("""
            SELECT block_index, tx_id, sender, amount, payment_method,
                   timestamp, prev_hash, current_hash, status, created_at
            FROM ledger_records
            WHERE tx_id = ?;
        """, (tx_id.strip(),))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_last_record(db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetch the most recently appended block in the ledger."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("""
            SELECT block_index, tx_id, sender, amount, payment_method,
                   timestamp, prev_hash, current_hash, status, created_at
            FROM ledger_records
            ORDER BY block_index DESC
            LIMIT 1;
        """)
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_ledger_metrics(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Compute aggregate summary metrics of the ledger."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("""
            SELECT 
                COUNT(*) as total_count,
                COALESCE(SUM(amount), 0.0) as total_amount,
                COALESCE(AVG(amount), 0.0) as avg_amount,
                COALESCE(MIN(amount), 0.0) as min_amount,
                COALESCE(MAX(amount), 0.0) as max_amount
            FROM ledger_records;
        """)
        row = cursor.fetchone()
        return dict(row) if row else {
            "total_count": 0,
            "total_amount": 0.0,
            "avg_amount": 0.0,
            "min_amount": 0.0,
            "max_amount": 0.0
        }
    finally:
        conn.close()

def reset_db(db_path: Optional[str] = None) -> None:
    """Safely drops and re-initializes the ledger table."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("DROP TABLE IF EXISTS ledger_records;")
        init_db(db_path)
    finally:
        conn.close()
