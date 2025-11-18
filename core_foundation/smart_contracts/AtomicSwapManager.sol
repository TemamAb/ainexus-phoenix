// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title AI-NEXUS Atomic Swap Manager
 * @dev Hash Time Lock Contract for atomic cross-chain arbitrage
 */

contract AtomicSwapManager {
    struct Swap {
        address initiator;
        address participant;
        uint256 amount;
        bytes32 secretHash;
        uint256 lockTime;
        uint256 expirationTime;
        bool initiated;
        bool completed;
        bool refunded;
    }

    mapping(bytes32 => Swap) public swaps;
    mapping(bytes32 => bool) public usedSecrets;

    event SwapInitiated(
        bytes32 indexed swapId,
        address indexed initiator,
        address indexed participant,
        uint256 amount,
        uint256 expirationTime
    );

    event SwapCompleted(
        bytes32 indexed swapId,
        address indexed participant,
        bytes32 secret
    );

    event SwapRefunded(
        bytes32 indexed swapId,
        address indexed initiator
    );

    modifier onlyInitiator(bytes32 swapId) {
        require(msg.sender == swaps[swapId].initiator, "Only initiator");
        _;
    }

    modifier swapExists(bytes32 swapId) {
        require(swaps[swapId].initiated, "Swap does not exist");
        _;
    }

    modifier notCompleted(bytes32 swapId) {
        require(!swaps[swapId].completed, "Swap already completed");
        _;
    }

    modifier notRefunded(bytes32 swapId) {
        require(!swaps[swapId].refunded, "Swap already refunded");
        _;
    }

    /**
     * @dev Initiate an atomic swap
     * @param participant The participant address
     * @param secretHash The hash of the secret
     * @param expirationTime Time when swap expires
     * @return swapId The unique swap identifier
     */
    function initiateSwap(
        address participant,
        bytes32 secretHash,
        uint256 expirationTime
    ) external payable returns (bytes32 swapId) {
        require(msg.value > 0, "Amount must be positive");
        require(expirationTime > block.timestamp, "Invalid expiration time");
        require(participant != address(0), "Invalid participant");

        swapId = keccak256(
            abi.encodePacked(
                msg.sender,
                participant,
                msg.value,
                secretHash,
                expirationTime
            )
        );

        require(!swaps[swapId].initiated, "Swap already initiated");

        swaps[swapId] = Swap({
            initiator: msg.sender,
            participant: participant,
            amount: msg.value,
            secretHash: secretHash,
            lockTime: block.timestamp,
            expirationTime: expirationTime,
            initiated: true,
            completed: false,
            refunded: false
        });

        emit SwapInitiated(
            swapId,
            msg.sender,
            participant,
            msg.value,
            expirationTime
        );

        return swapId;
    }

    /**
     * @dev Complete an atomic swap by revealing the secret
     * @param swapId The swap identifier
     * @param secret The secret that matches the secret hash
     */
    function completeSwap(bytes32 swapId, bytes32 secret)
        external
        swapExists(swapId)
        notCompleted(swapId)
        notRefunded(swapId)
    {
        Swap storage swap = swaps[swapId];

        require(msg.sender == swap.participant, "Only participant can complete");
        require(block.timestamp <= swap.expirationTime, "Swap expired");
        require(keccak256(abi.encodePacked(secret)) == swap.secretHash, "Invalid secret");
        require(!usedSecrets[secret], "Secret already used");

        // Mark swap as completed
        swap.completed = true;
        usedSecrets[secret] = true;

        // Transfer funds to participant
        payable(swap.participant).transfer(swap.amount);

        emit SwapCompleted(swapId, msg.sender, secret);
    }

    /**
     * @dev Refund the swap if it expires
     * @param swapId The swap identifier
     */
    function refundSwap(bytes32 swapId)
        external
        swapExists(swapId)
        notCompleted(swapId)
        notRefunded(swapId)
    {
        Swap storage swap = swaps[swapId];

        require(block.timestamp > swap.expirationTime, "Swap not expired");
        require(
            msg.sender == swap.initiator || msg.sender == swap.participant,
            "Only swap parties can refund"
        );

        // Mark swap as refunded
        swap.refunded = true;

        // Return funds to initiator
        payable(swap.initiator).transfer(swap.amount);

        emit SwapRefunded(swapId, swap.initiator);
    }

    /**
     * @dev Get swap details
     * @param swapId The swap identifier
     */
    function getSwap(bytes32 swapId)
        external
        view
        returns (
            address initiator,
            address participant,
            uint256 amount,
            bytes32 secretHash,
            uint256 lockTime,
            uint256 expirationTime,
            bool completed,
            bool refunded
        )
    {
        Swap storage swap = swaps[swapId];
        require(swap.initiated, "Swap does not exist");

        return (
            swap.initiator,
            swap.participant,
            swap.amount,
            swap.secretHash,
            swap.lockTime,
            swap.expirationTime,
            swap.completed,
            swap.refunded
        );
    }

    /**
     * @dev Check if a secret has been used
     * @param secret The secret to check
     */
    function isSecretUsed(bytes32 secret) external view returns (bool) {
        return usedSecrets[secret];
    }

    /**
     * @dev Calculate swap ID for verification
     */
    function calculateSwapId(
        address initiator,
        address participant,
        uint256 amount,
        bytes32 secretHash,
        uint256 expirationTime
    ) external pure returns (bytes32) {
        return keccak256(
            abi.encodePacked(
                initiator,
                participant,
                amount,
                secretHash,
                expirationTime
            )
        );
    }

    /**
     * @dev Emergency shutdown for contract migration (only owner in production)
     */
    function emergencyShutdown() external {
        // In production, this would have proper access control
        // For now, this is a placeholder
        require(msg.sender == address(0), "Not authorized");
        selfdestruct(payable(msg.sender));
    }
}

/**
 * @title CrossChainArbitrageExecutor
 * @dev Executes arbitrage operations with atomic swap support
 */
contract CrossChainArbitrageExecutor {
    AtomicSwapManager public swapManager;
    
    event ArbitrageExecuted(
        bytes32 indexed swapId,
        address indexed executor,
        uint256 profit,
        uint256 timestamp
    );

    event ArbitrageFailed(
        bytes32 indexed swapId,
        address indexed executor,
        string reason
    );

    constructor(address _swapManager) {
        swapManager = AtomicSwapManager(_swapManager);
    }

    /**
     * @dev Execute arbitrage with atomic swap completion
     */
    function executeArbitrageWithSwap(
        bytes32 swapId,
        bytes32 secret,
        address[] calldata path,
        uint256 minOutput
    ) external {
        // Verify swap can be completed
        (,, uint256 amount,,, uint256 expirationTime, bool completed, bool refunded) = 
            swapManager.getSwap(swapId);
            
        require(!completed, "Swap already completed");
        require(!refunded, "Swap was refunded");
        require(block.timestamp <= expirationTime, "Swap expired");

        // Complete the swap to receive funds
        swapManager.completeSwap(swapId, secret);

        // Execute arbitrage with the received funds
        uint256 initialBalance = address(this).balance;
        
        try this.executeArbitrage(path, minOutput) {
            uint256 finalBalance = address(this).balance;
            uint256 profit = finalBalance - initialBalance;

            emit ArbitrageExecuted(swapId, msg.sender, profit, block.timestamp);

            // Transfer profit to executor
            if (profit > 0) {
                payable(msg.sender).transfer(profit);
            }

        } catch Error(string memory reason) {
            emit ArbitrageFailed(swapId, msg.sender, reason);
            revert(reason);
        } catch {
            emit ArbitrageFailed(swapId, msg.sender, "Unknown error");
            revert("Arbitrage execution failed");
        }
    }

    /**
     * @dev Execute arbitrage (simplified implementation)
     */
    function executeArbitrage(
        address[] calldata path,
        uint256 minOutput
    ) external payable {
        // This would contain the actual arbitrage logic
        // For now, it's a placeholder that simulates success
        
        require(path.length >= 2, "Invalid path");
        require(msg.value > 0, "No value sent");
        
        // Simulate arbitrage execution with 1% profit
        uint256 output = msg.value * 101 / 100;
        require(output >= minOutput, "Insufficient output");
        
        // In production, this would interact with DEXes
        // For now, just keep the funds in contract
    }

    /**
     * @dev Withdraw funds from contract
     */
    function withdraw(uint256 amount) external {
        require(amount <= address(this).balance, "Insufficient balance");
        payable(msg.sender).transfer(amount);
    }

    /**
     * @dev Get contract balance
     */
    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }

    // Fallback function to receive ETH
    receive() external payable {}
}
