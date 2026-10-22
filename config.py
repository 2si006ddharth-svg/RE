"""Configuration constants and settings for the Blockchain Payment Soundbox Simulator.
Academic prototype inspired by digital payment soundboxes.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
AUDIO_DIR = BASE_DIR / "audio_cache"

# Ensure runtime directories exist
DATA_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

# Database Paths
DB_PATH = os.getenv("SOUNDBOX_DB_PATH", str(DATA_DIR / "soundbox_ledger.db"))
CLEAN_DEMO_DB_PATH = str(DATA_DIR / "soundbox_ledger_clean.db")
ORIGINAL_BACKUP_DB_PATH = str(DATA_DIR / "soundbox_ledger_original_corrupted.db")

# Cryptographic Ledger Constants
GENESIS_PREV_HASH = "0" * 64
HASH_ALGORITHM = "SHA-256"

# Currency & Formats
CURRENCY_CODE = "INR"
CURRENCY_SYMBOL = "₹"

# Allowed Simulated Payment Methods
PAYMENT_METHODS = [
    "UPI QR Scan",
    "UPI VPA (Simulated)",
    "Simulated Debit Card",
    "Simulated Credit Card",
    "Simulated NetBanking",
    "Simulated Digital Wallet",
]

# Soundbox Announcement Templates
SOUNDBOX_TEXT_TEMPLATE_EN = "Payment received: {amount} rupees."
SOUNDBOX_FULL_SPEECH_EN = "Payment received. {amount} rupees received successfully on simulated soundbox."
SOUNDBOX_TEXT_TEMPLATE_HI = "पेमेंट प्राप्त हुआ: {amount} रुपये."
SOUNDBOX_FULL_SPEECH_HI = "पेमेंट प्राप्त हुआ। सिम्युलेटेड साउंडबॉक्स पर {amount} रुपये सफलता पूर्वक प्राप्त हुए।"

# Disclaimer
ACADEMIC_DISCLAIMER = (
    "ACADEMIC PROTOTYPE ONLY: This application is a simulated educational prototype. "
    "It is NOT an official Paytm, PhonePe, or NPCI/UPI product and does NOT connect to real bank accounts, "
    "payment gateways, or real money. Locally computed SHA-256 hashes demonstrate ledger integrity and "
    "do NOT represent bank settlement or authorized fiat transfers."
)
