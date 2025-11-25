// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./ApexAccount.sol";

/**
 * @title ApexFactory
 * @dev Factory contract for creating QuantumNex smart accounts
 * Uses CREATE2 for deterministic address calculation
 */
contract ApexFactory {
    address public immutable entryPoint;
    mapping(address => address) public accounts;
    
    event AccountCreated(address indexed owner, address indexed account);
    
    constructor(address _entryPoint) {
        entryPoint = _entryPoint;
    }
    
    /**
     * @dev Create a new ApexAccount for a user
     */
    function createAccount(address owner) external returns (address) {
        require(accounts[owner] == address(0), "Account already exists");
        
        bytes32 salt = keccak256(abi.encodePacked(owner));
        ApexAccount account = new ApexAccount{salt: salt}(entryPoint);
        accounts[owner] = address(account);
        
        emit AccountCreated(owner, address(account));
        return address(account);
    }
    
    /**
     * @dev Get account address for a user (CREATE2)
     */
    function getAccountAddress(address owner) public view returns (address) {
        bytes32 salt = keccak256(abi.encodePacked(owner));
        bytes memory creationCode = type(ApexAccount).creationCode;
        bytes memory bytecode = abi.encodePacked(creationCode, abi.encode(entryPoint));
        
        bytes32 hash = keccak256(
            abi.encodePacked(bytes1(0xff), address(this), salt, keccak256(bytecode))
        );
        
        return address(uint160(uint256(hash)));
    }
    
    /**
     * @dev Check if account exists for user
     */
    function hasAccount(address owner) external view returns (bool) {
        return accounts[owner] != address(0);
    }
}
