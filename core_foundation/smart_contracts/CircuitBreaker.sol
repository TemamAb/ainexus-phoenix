// File: core_foundation/smart_contracts/CircuitBreaker.sol
// 7P-PILLAR: BOT3-7P, MEV-7P
// PURPOSE: Enhanced circuit breaker with multi-level protection

pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title AI-Nexus Circuit Breaker
 * @dev Advanced circuit breaker with multi-level protection mechanisms
 * Provides emergency shutdown capabilities for the arbitrage system
 */
contract CircuitBreaker is Ownable, ReentrancyGuard {
    // Circuit breaker states
    enum SystemState { 
        OPERATIONAL, 
        HIGH_LOAD, 
        DEGRADED, 
        EMERGENCY_STOP 
    }
    
    // Protection triggers
    struct ProtectionTrigger {
        string name;
        uint256 threshold;
        uint256 cooldown;
        uint256 lastTriggered;
        bool enabled;
    }
    
    // System metrics for monitoring
    struct SystemMetrics {
        uint256 totalTransactions;
        uint256 failedTransactions;
        uint256 totalVolume;
        uint256 averageGasUsed;
        uint256 lastUpdate;
    }
    
    // State variables
    SystemState public currentState;
    SystemMetrics public metrics;
    
    // Protection triggers
    mapping(string => ProtectionTrigger) public triggers;
    string[] public triggerNames;
    
    // Events
    event SystemStateChanged(SystemState previousState, SystemState newState, address triggeredBy);
    event ProtectionTriggered(string triggerName, uint256 threshold, uint256 actualValue, address triggeredBy);
    event EmergencyStop(address executedBy, string reason);
    event SystemResume(address executedBy);
    
    // Modifiers
    modifier onlyOperational() {
        require(currentState == SystemState.OPERATIONAL, "CircuitBreaker: System not operational");
        _;
    }
    
    modifier onlyAboveState(SystemState requiredState) {
        require(currentState <= requiredState, "CircuitBreaker: System state too restrictive");
        _;
    }
    
    constructor() {
        currentState = SystemState.OPERATIONAL;
        metrics.lastUpdate = block.timestamp;
        
        // Initialize protection triggers
        _initializeTriggers();
    }
    
    /**
     * @dev Initialize default protection triggers
     */
    function _initializeTriggers() internal {
        _addTrigger("high_failure_rate", 10, 300); // 10% failure rate, 5min cooldown
        _addTrigger("high_volume", 1000 ether, 60); // 1000 ETH volume, 1min cooldown
        _addTrigger("gas_spike", 200 gwei, 120); // 200 gwei gas, 2min cooldown
        _addTrigger("rapid_transactions", 100, 30); // 100 tx/min, 30sec cooldown
    }
    
    /**
     * @dev Add a new protection trigger
     */
    function addTrigger(string memory name, uint256 threshold, uint256 cooldown) external onlyOwner {
        _addTrigger(name, threshold, cooldown);
    }
    
    function _addTrigger(string memory name, uint256 threshold, uint256 cooldown) internal {
        triggers[name] = ProtectionTrigger({
            name: name,
            threshold: threshold,
            cooldown: cooldown,
            lastTriggered: 0,
            enabled: true
        });
        triggerNames.push(name);
    }
    
    /**
     * @dev Update system metrics (called by arbitrage engine)
     */
    function updateMetrics(
        uint256 txCount, 
        uint256 failedTxCount, 
        uint256 volume, 
        uint256 gasUsed
    ) external onlyOwner {
        metrics.totalTransactions += txCount;
        metrics.failedTransactions += failedTxCount;
        metrics.totalVolume += volume;
        
        // Update average gas used (moving average)
        metrics.averageGasUsed = (metrics.averageGasUsed * 9 + gasUsed) / 10;
        metrics.lastUpdate = block.timestamp;
        
        // Check protection triggers
        _checkTriggers();
    }
    
    /**
     * @dev Check all protection triggers
     */
    function _checkTriggers() internal {
        for (uint i = 0; i < triggerNames.length; i++) {
            string memory triggerName = triggerNames[i];
            ProtectionTrigger storage trigger = triggers[triggerName];
            
            if (!trigger.enabled) continue;
            if (block.timestamp < trigger.lastTriggered + trigger.cooldown) continue;
            
            bool shouldTrigger = _evaluateTrigger(triggerName, trigger.threshold);
            
            if (shouldTrigger) {
                trigger.lastTriggered = block.timestamp;
                emit ProtectionTriggered(triggerName, trigger.threshold, _getTriggerValue(triggerName), msg.sender);
                
                // Escalate system state based on trigger severity
                _escalateState();
            }
        }
    }
    
    /**
     * @dev Evaluate if a trigger condition is met
     */
    function _evaluateTrigger(string memory triggerName, uint256 threshold) internal view returns (bool) {
        uint256 currentValue = _getTriggerValue(triggerName);
        
        if (keccak256(abi.encodePacked(triggerName)) == keccak256(abi.encodePacked("high_failure_rate"))) {
            // Failure rate trigger
            if (metrics.totalTransactions > 0) {
                uint256 failureRate = (metrics.failedTransactions * 100) / metrics.totalTransactions;
                return failureRate > threshold;
            }
        } else if (keccak256(abi.encodePacked(triggerName)) == keccak256(abi.encodePacked("high_volume"))) {
            // Volume trigger
            return metrics.totalVolume > threshold;
        } else if (keccak256(abi.encodePacked(triggerName)) == keccak256(abi.encodePacked("gas_spike"))) {
            // Gas price trigger
            return tx.gasprice > threshold;
        } else if (keccak256(abi.encodePacked(triggerName)) == keccak256(abi.encodePacked("rapid_transactions"))) {
            // Transaction rate trigger (simplified)
            return metrics.totalTransactions / ((block.timestamp - metrics.lastUpdate) / 60) > threshold;
        }
        
        return false;
    }
    
    /**
     * @dev Get current value for a trigger
     */
    function _getTriggerValue(string memory triggerName) internal view returns (uint256) {
        if (keccak256(abi.encodePacked(triggerName)) == keccak256(abi.encodePacked("high_failure_rate"))) {
            if (metrics.totalTransactions == 0) return 0;
            return (metrics.failedTransactions * 100) / metrics.totalTransactions;
        } else if (keccak256(abi.encodePacked(triggerName)) == keccak256(abi.encodePacked("high_volume"))) {
            return metrics.totalVolume;
        } else if (keccak256(abi.encodePacked(triggerName)) == keccak256(abi.encodePacked("gas_spike"))) {
            return tx.gasprice;
        } else if (keccak256(abi.encodePacked(triggerName)) == keccak256(abi.encodePacked("rapid_transactions"))) {
            if (block.timestamp == metrics.lastUpdate) return 0;
            return metrics.totalTransactions / ((block.timestamp - metrics.lastUpdate) / 60);
        }
        
        return 0;
    }
    
    /**
     * @dev Escalate system state based on trigger conditions
     */
    function _escalateState() internal {
        SystemState newState = currentState;
        
        // Calculate overall system health score
        uint256 healthScore = _calculateHealthScore();
        
        if (healthScore < 30) {
            newState = SystemState.EMERGENCY_STOP;
        } else if (healthScore < 60) {
            newState = SystemState.DEGRADED;
        } else if (healthScore < 80) {
            newState = SystemState.HIGH_LOAD;
        } else {
            newState = SystemState.OPERATIONAL;
        }
        
        if (newState != currentState) {
            SystemState previousState = currentState;
            currentState = newState;
            emit SystemStateChanged(previousState, newState, msg.sender);
        }
    }
    
    /**
     * @dev Calculate overall system health score (0-100)
     */
    function _calculateHealthScore() internal view returns (uint256) {
        uint256 score = 100;
        
        // Deduct points for high failure rate
        if (metrics.totalTransactions > 0) {
            uint256 failureRate = (metrics.failedTransactions * 100) / metrics.totalTransactions;
            if (failureRate > 5) score -= (failureRate - 5) * 2;
        }
        
        // Deduct points for high volume concentration
        if (metrics.totalVolume > 1000 ether) {
            score -= 10;
        }
        
        // Deduct points for high gas prices
        if (tx.gasprice > 100 gwei) {
            score -= 15;
        }
        
        return score > 0 ? score : 0;
    }
    
    /**
     * @dev Manual emergency stop
     */
    function emergencyStop(string memory reason) external onlyOwner {
        SystemState previousState = currentState;
        currentState = SystemState.EMERGENCY_STOP;
        
        emit SystemStateChanged(previousState, SystemState.EMERGENCY_STOP, msg.sender);
        emit EmergencyStop(msg.sender, reason);
    }
    
    /**
     * @dev Resume system operations
     */
    function resumeOperations() external onlyOwner {
        require(currentState == SystemState.EMERGENCY_STOP, "CircuitBreaker: Not in emergency stop");
        
        // Reset metrics for fresh start
        metrics.totalTransactions = 0;
        metrics.failedTransactions = 0;
        metrics.totalVolume = 0;
        metrics.lastUpdate = block.timestamp;
        
        SystemState previousState = currentState;
        currentState = SystemState.OPERATIONAL;
        
        emit SystemStateChanged(previousState, SystemState.OPERATIONAL, msg.sender);
        emit SystemResume(msg.sender);
    }
    
    /**
     * @dev Check if system is operational for a specific operation
     */
    function isOperational() external view returns (bool) {
        return currentState == SystemState.OPERATIONAL;
    }
    
    /**
     * @dev Get current system state with details
     */
    function getSystemStatus() external view returns (
        SystemState state,
        uint256 healthScore,
        uint256 totalTx,
        uint256 failedTx,
        uint256 totalVolume
    ) {
        return (
            currentState,
            _calculateHealthScore(),
            metrics.totalTransactions,
            metrics.failedTransactions,
            metrics.totalVolume
        );
    }
    
    /**
     * @dev Enable/disable specific protection triggers
     */
    function setTriggerEnabled(string memory triggerName, bool enabled) external onlyOwner {
        require(bytes(triggers[triggerName].name).length > 0, "CircuitBreaker: Trigger not found");
        triggers[triggerName].enabled = enabled;
    }
    
    /**
     * @dev Update trigger threshold
     */
    function updateTriggerThreshold(string memory triggerName, uint256 newThreshold) external onlyOwner {
        require(bytes(triggers[triggerName].name).length > 0, "CircuitBreaker: Trigger not found");
        triggers[triggerName].threshold = newThreshold;
    }
}
