"""Tests for optional smart contract Web3 connector."""

from blockchain_contract import LocalBlockchainConnector, WEB3_AVAILABLE

def test_web3_connector_graceful_offline():
    """Test that LocalBlockchainConnector does not throw error when local node is offline."""
    connector = LocalBlockchainConnector(rpc_url="http://127.0.0.1:8545")
    status = connector.get_status()
    
    assert "connected" in status
    assert status["available"] == WEB3_AVAILABLE
    
    # Anchoring should gracefully return failure without crashing
    res = connector.anchor_payment_on_chain("TX-TEST-001", "a" * 64, 500.0, "UPI QR Scan")
    assert res["success"] is False
    assert "not reachable" in res["message"] or "not deployed" in res["message"]
