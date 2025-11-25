/**
 * MEV SHIELD SMART CONTRACT
 * REF: Flashbots MEV-Share + Ethereum PBS (Proposer-Builder Separation)
 * MEV protection and fair value distribution for institutional traders
 */

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract MEVShield is ReentrancyGuard, Ownable {
    using ECDSA for bytes32;
    
    // Flashbots MEV-Share inspired structures
    struct ProtectedTransaction {
        address from;
        address to;
        uint256 value;
        bytes data;
        uint256 maxPriorityFee;
        uint256 maxFee;
        uint256 deadline;
        bytes32 bundleHash;
        address relayer;
        uint256 timestamp;
        bool executed;
        bool reverted;
    }
    
    struct MEVReward {
        address recipient;
        uint256 amount;
        bytes32 transactionHash;
        uint256 timestamp;
    }
    
    // State variables
    mapping(bytes32 => ProtectedTransaction) public protectedTransactions;
    mapping(address => uint256) public relayerReputation;
    mapping(bytes32 => bool) public usedBundleHashes;
    
    uint256 public constant MIN_REPUTATION = 100;
    uint256 public constant MAX_DEADLINE = 30 minutes;
    uint256 public totalProtectedVolume;
    uint256 public totalMEVRewards;
    
    // Flashbots-inspired events
    event TransactionProtected(
        bytes32 indexed bundleHash,
        address indexed from,
        address indexed to,
        uint256 value,
        uint256 maxPriorityFee,
        uint256 maxFee,
        uint256 deadline
    );
    
    event TransactionExecuted(
        bytes32 indexed bundleHash,
        address indexed relayer,
        uint256 actualPriorityFee,
        uint256 actualFee,
        bool success
    );
    
    event MEVRewardDistributed(
        address indexed recipient,
        uint256 amount,
        bytes32 indexed transactionHash,
        bytes32 indexed bundleHash
    );
    
    event RelayerReputationUpdated(
        address indexed relayer,
        uint256 oldReputation,
        uint256 newReputation
    );
    
    // Flashbots-inspired modifiers
    modifier onlyReputableRelayer() {
        require(relayerReputation[msg.sender] >= MIN_REPUTATION, "MEVShield: Insufficient reputation");
        _;
    }
    
    modifier validDeadline(uint256 deadline) {
        require(deadline <= block.timestamp + MAX_DEADLINE, "MEVShield: Deadline too far");
        require(deadline > block.timestamp, "MEVShield: Deadline passed");
        _;
    }
    
    modifier bundleNotUsed(bytes32 bundleHash) {
        require(!usedBundleHashes[bundleHash], "MEVShield: Bundle already used");
        _;
    }
    
    /**
     * @dev Protect a transaction from MEV
     * Flashbots MEV-Share inspired protection mechanism
     */
    function protectTransaction(
        address to,
        uint256 value,
        bytes calldata data,
        uint256 maxPriorityFee,
        uint256 maxFee,
        uint256 deadline,
        bytes32 bundleHash
    ) external validDeadline(deadline) bundleNotUsed(bundleHash) returns (bytes32) {
        require(to != address(0), "MEVShield: Invalid recipient");
        require(maxPriorityFee <= maxFee, "MEVShield: Invalid fee structure");
        
        ProtectedTransaction memory protectedTx = ProtectedTransaction({
            from: msg.sender,
            to: to,
            value: value,
            data: data,
            maxPriorityFee: maxPriorityFee,
            maxFee: maxFee,
            deadline: deadline,
            bundleHash: bundleHash,
            relayer: address(0),
            timestamp: block.timestamp,
            executed: false,
            reverted: false
        });
        
        protectedTransactions[bundleHash] = protectedTx;
        usedBundleHashes[bundleHash] = true;
        
        totalProtectedVolume += value;
        
        emit TransactionProtected(
            bundleHash,
            msg.sender,
            to,
            value,
            maxPriorityFee,
            maxFee,
            deadline
        );
        
        return bundleHash;
    }
    
    /**
     * @dev Execute protected transaction (relayer only)
     * Flashbots-inspired execution with MEV protection
     */
    function executeProtectedTransaction(
        bytes32 bundleHash,
        uint256 actualPriorityFee,
        uint256 actualFee
    ) external onlyReputableRelayer nonReentrant returns (bool) {
        ProtectedTransaction storage protectedTx = protectedTransactions[bundleHash];
        
        require(protectedTx.from != address(0), "MEVShield: Transaction not found");
        require(!protectedTx.executed, "MEVShield: Already executed");
        require(block.timestamp <= protectedTx.deadline, "MEVShield: Deadline passed");
        require(actualPriorityFee <= protectedTx.maxPriorityFee, "MEVShield: Priority fee too high");
        require(actualFee <= protectedTx.maxFee, "MEVShield: Fee too high");
        
        protectedTx.relayer = msg.sender;
        protectedTx.executed = true;
        
        // Calculate MEV reward (Flashbots fair distribution)
        uint256 mevReward = _calculateMEVReward(actualPriorityFee, protectedTx.maxPriorityFee);
        
        // Execute transaction
        (bool success, ) = protectedTx.to.call{value: protectedTx.value}(
            protectedTx.data
        );
        
        protectedTx.reverted = !success;
        
        if (success && mevReward > 0) {
            _distributeMEVReward(msg.sender, mevReward, bundleHash);
            relayerReputation[msg.sender] += 10; // Increase reputation
        } else if (!success) {
            relayerReputation[msg.sender] = relayerReputation[msg.sender] > 20 ? 
                relayerReputation[msg.sender] - 20 : 0; // Decrease reputation
        }
        
        emit TransactionExecuted(
            bundleHash,
            msg.sender,
            actualPriorityFee,
            actualFee,
            success
        );
        
        return success;
    }
    
    /**
     * @dev Calculate MEV reward based on fee savings
     * Flashbots fair value distribution algorithm
     */
    function _calculateMEVReward(
        uint256 actualPriorityFee,
        uint256 maxPriorityFee
    ) internal pure returns (uint256) {
        if (actualPriorityFee >= maxPriorityFee) {
            return 0;
        }
        
        uint256 feeSavings = maxPriorityFee - actualPriorityFee;
        
        // Relayer gets 80% of savings, 20% to protocol
        uint256 relayerReward = (feeSavings * 80) / 100;
        
        return relayerReward;
    }
    
    /**
     * @dev Distribute MEV reward to relayer
     */
    function _distributeMEVReward(
        address relayer,
        uint256 amount,
        bytes32 bundleHash
    ) internal {
        (bool success, ) = relayer.call{value: amount}("");
        require(success, "MEVShield: Reward distribution failed");
        
        totalMEVRewards += amount;
        
        emit MEVRewardDistributed(
            relayer,
            amount,
            blockhash(block.number - 1),
            bundleHash
        );
    }
    
    /**
     * @dev Register relayer with initial reputation
     * Flashbots-style relayer onboarding
     */
    function registerRelayer(address relayer, uint256 initialReputation) external onlyOwner {
        require(relayer != address(0), "MEVShield: Invalid relayer");
        require(initialReputation >= MIN_REPUTATION, "MEVShield: Reputation too low");
        
        uint256 oldReputation = relayerReputation[relayer];
        relayerReputation[relayer] = initialReputation;
        
        emit RelayerReputationUpdated(relayer, oldReputation, initialReputation);
    }
    
    /**
     * @dev Update relayer reputation
     * Flashbots-style reputation system
     */
    function updateRelayerReputation(address relayer, uint256 newReputation) external onlyOwner {
        require(relayer != address(0), "MEVShield: Invalid relayer");
        
        uint256 oldReputation = relayerReputation[relayer];
        relayerReputation[relayer] = newReputation;
        
        emit RelayerReputationUpdated(relayer, oldReputation, newReputation);
    }
    
    /**
     * @dev Get transaction protection status
     */
    function getProtectionStatus(bytes32 bundleHash) external view returns (
        address from,
        address to,
        uint256 value,
        bool executed,
        bool reverted,
        uint256 deadline
    ) {
        ProtectedTransaction memory protectedTx = protectedTransactions[bundleHash];
        return (
            protectedTx.from,
            protectedTx.to,
            protectedTx.value,
            protectedTx.executed,
            protectedTx.reverted,
            protectedTx.deadline
        );
    }
    
    /**
     * @dev Withdraw protocol fees (owner only)
     */
    function withdrawProtocolFees(address recipient, uint256 amount) external onlyOwner {
        require(recipient != address(0), "MEVShield: Invalid recipient");
        require(amount <= address(this).balance, "MEVShield: Insufficient balance");
        
        (bool success, ) = recipient.call{value: amount}("");
        require(success, "MEVShield: Withdrawal failed");
    }
    
    receive() external payable {}
}
