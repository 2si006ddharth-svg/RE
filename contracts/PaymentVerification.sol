// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title PaymentVerification
 * @dev Academic prototype smart contract for anchoring simulated payment hashes
 * on an EVM-compatible local development blockchain (e.g., Hardhat or Ganache).
 *
 * NOTE: This is an educational demonstration. It anchors cryptographic digests
 * of simulated transactions. It does NOT process real money or connect to real banks.
 */
contract PaymentVerification {
    
    // Struct to store anchored payment records
    struct PaymentRecord {
        string txId;
        bytes32 txHash;
        uint256 amountInPaisa; // stored in paisa (1 INR = 100 paisa)
        string paymentMethod;
        uint256 blockTimestamp;
        address recordedBy;
        bool exists;
    }

    // Mapping from transaction ID to on-chain record
    mapping(string => PaymentRecord) private payments;

    // Ordered list of all recorded transaction IDs
    string[] public allTxIds;

    // Events
    event PaymentAnchored(
        string indexed txId,
        bytes32 indexed txHash,
        uint256 amountInPaisa,
        string paymentMethod,
        uint256 timestamp,
        address indexed recordedBy
    );

    /**
     * @notice Anchor a verified payment transaction hash on the blockchain.
     * @param _txId The unique simulated transaction identifier.
     * @param _txHash The SHA-256 hash digest of the transaction block.
     * @param _amountInPaisa The payment amount in paisa (e.g., 500 INR = 50000 paisa).
     * @param _paymentMethod The simulated payment method.
     */
    function anchorPayment(
        string calldata _txId,
        bytes32 _txHash,
        uint256 _amountInPaisa,
        string calldata _paymentMethod
    ) external {
        require(bytes(_txId).length > 0, "Transaction ID cannot be empty");
        require(!payments[_txId].exists, "Transaction ID already anchored on-chain");
        require(_amountInPaisa > 0, "Amount must be greater than zero");

        payments[_txId] = PaymentRecord({
            txId: _txId,
            txHash: _txHash,
            amountInPaisa: _amountInPaisa,
            paymentMethod: _paymentMethod,
            blockTimestamp: block.timestamp,
            recordedBy: msg.sender,
            exists: true
        });

        allTxIds.push(_txId);

        emit PaymentAnchored(
            _txId,
            _txHash,
            _amountInPaisa,
            _paymentMethod,
            block.timestamp,
            msg.sender
        );
    }

    /**
     * @notice Verify whether a given transaction ID and hash match on-chain records.
     * @param _txId The transaction ID to verify.
     * @param _expectedHash The expected SHA-256 digest to compare against.
     * @return isMatch True if the hash matches the on-chain anchor.
     * @return timestamp The on-chain block timestamp when anchored.
     */
    function verifyPayment(
        string calldata _txId,
        bytes32 _expectedHash
    ) external view returns (bool isMatch, uint256 timestamp) {
        PaymentRecord memory record = payments[_txId];
        if (!record.exists) {
            return (false, 0);
        }
        return (record.txHash == _expectedHash, record.blockTimestamp);
    }

    /**
     * @notice Get total count of anchored transactions.
     */
    function getTotalAnchoredPayments() external view returns (uint256) {
        return allTxIds.length;
    }
}
