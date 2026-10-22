"""Optional Web3.py integration for interacting with the local PaymentVerification smart contract.
Works with local testnets (Hardhat / Ganache / Anvil).
Gracefully handles offline states without impacting core simulator functionality.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

try:
    from web3 import Web3
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False

BASE_DIR = Path(__file__).resolve().parent
CONTRACTS_DIR = BASE_DIR / "contracts"
DEPLOYMENT_FILE = CONTRACTS_DIR / "deployment_info.json"

# Minimal ABI for PaymentVerification
MINIMAL_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "_txId", "type": "string"},
            {"internalType": "bytes32", "name": "_txHash", "type": "bytes32"},
            {"internalType": "uint256", "name": "_amountInPaisa", "type": "uint256"},
            {"internalType": "string", "name": "_paymentMethod", "type": "string"}
        ],
        "name": "anchorPayment",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_txId", "type": "string"},
            {"internalType": "bytes32", "name": "_expectedHash", "type": "bytes32"}
        ],
        "name": "verifyPayment",
        "outputs": [
            {"internalType": "bool", "name": "isMatch", "type": "bool"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getTotalAnchoredPayments",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

class LocalBlockchainConnector:
    """Connector to a local development Ethereum node."""

    def __init__(self, rpc_url: str = "http://127.0.0.1:8545"):
        self.rpc_url = rpc_url
        self.w3 = None
        self.is_connected = False
        self.contract = None
        self.contract_address = None

        if WEB3_AVAILABLE:
            try:
                self.w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 2}))
                self.is_connected = self.w3.is_connected()
                if self.is_connected:
                    self._load_contract()
            except Exception:
                self.is_connected = False

    def _load_contract(self):
        """Load contract address and ABI if deployment artifact exists."""
        if DEPLOYMENT_FILE.exists():
            try:
                with open(DEPLOYMENT_FILE, "r") as f:
                    data = json.load(f)
                    self.contract_address = data.get("address")
                    if self.contract_address:
                        self.contract = self.w3.eth.contract(
                            address=Web3.to_checksum_address(self.contract_address),
                            abi=MINIMAL_ABI
                        )
            except Exception:
                self.contract = None

    def get_status(self) -> Dict[str, Any]:
        """Return connectivity status of the local blockchain node."""
        if not WEB3_AVAILABLE:
            return {
                "available": False,
                "connected": False,
                "message": "Web3.py package not installed."
            }
        
        return {
            "available": True,
            "connected": self.is_connected,
            "rpc_url": self.rpc_url,
            "contract_address": self.contract_address,
            "block_number": self.w3.eth.block_number if self.is_connected else None
        }

    def anchor_payment_on_chain(
        self,
        tx_id: str,
        sha256_hex: str,
        amount_inr: float,
        payment_method: str
    ) -> Dict[str, Any]:
        """Anchor a payment record on the local EVM blockchain."""
        if not self.is_connected or not self.contract:
            return {
                "success": False,
                "message": "Local blockchain node not reachable or contract not deployed. Skipped on-chain anchoring."
            }

        try:
            # Convert SHA-256 hex string to bytes32
            tx_hash_bytes32 = bytes.fromhex(sha256_hex)
            amount_paisa = int(round(amount_inr * 100))

            accounts = self.w3.eth.accounts
            if not accounts:
                return {"success": False, "message": "No unlocked accounts available on local node."}

            tx_hash = self.contract.functions.anchorPayment(
                tx_id,
                tx_hash_bytes32,
                amount_paisa,
                payment_method
            ).transact({"from": accounts[0]})

            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return {
                "success": True,
                "tx_hash": receipt.transactionHash.hex(),
                "block_number": receipt.blockNumber,
                "message": f"Anchored on local blockchain block #{receipt.blockNumber}."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error anchoring to contract: {str(e)}"
            }
