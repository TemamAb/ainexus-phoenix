// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@aave/core-v3/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import "@aave/core-v3/contracts/interfaces/IPoolAddressesProvider.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

// INTERFACE FOR REAL TRADING (Uniswap/Sushi/Pancake)
interface IUniswapV2Router {
    function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
}

/**
 * @title ApexFlashLoan (Production Grade)
 * @dev Top 3 Execution Engine: Aave V3 -> Uniswap V2 Compatible
 */
contract ApexFlashLoan is FlashLoanSimpleReceiverBase {
    using SafeERC20 for IERC20;
    
    address public owner;
    
    // ARBITRAGE PAYLOAD
    struct ArbitrageData {
        address router1; // e.g., Uniswap V2 Router
        address router2; // e.g., SushiSwap V2 Router
        address tokenIn; // The token we borrowed (e.g., USDC)
        address tokenMid; // The token we flip to (e.g., WETH)
        uint256 amountIn; // The loan amount
    }
    
    event FlashLoanExecuted(address indexed token, uint256 amount, uint256 premium);
    event TradeExecuted(address indexed router, address tokenIn, uint amountOut);
    event ProfitSecured(address indexed token, uint256 profit);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Apex: Not Command");
        _;
    }

    constructor(IPoolAddressesProvider provider) FlashLoanSimpleReceiverBase(provider) {
        owner = msg.sender;
    }
    
    /**
     * @dev ONE-CLICK TRIGGER
     * This is the function your Dashboard calls to start the war.
     */
    function executeArbitrage(
        address token,
        uint256 amount,
        bytes calldata data
    ) external onlyOwner {
        // 0 = no referral code
        POOL.flashLoanSimple(address(this), token, amount, data, 0);
    }
    
    /**
     * @dev THE CALLBACK LOOP
     */
    function executeOperation(
        address token,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        require(msg.sender == address(POOL), "Apex: Intruder Alert");
        require(initiator == address(this), "Apex: Rogue Initiator");
        
        // 1. Decode Strategy
        ArbitrageData memory arbData = abi.decode(params, (ArbitrageData));
        
        // 2. Execute The Spatial Arbitrage (Router 1 -> Router 2)
        uint256 finalBalance = _executeDualTrade(arbData);
        
        // 3. Calculate Repayment
        // Gas Opt: Use unchecked for repayment math as overflow is impossible here
        uint256 amountToRepay;
        unchecked {
            amountToRepay = amount + premium;
        }
        
        // 4. Profit Check (The "Top 3" Safety Rail)
        require(finalBalance >= amountToRepay, "Apex: Trade Unprofitable - REVERTING");
        
        // 5. Repay Aave
        IERC20(token).approve(address(POOL), amountToRepay);
        
        // 6. Secure Profit
        uint256 profit;
        unchecked {
            profit = finalBalance - amountToRepay;
        }
        
        if (profit > 0) {
            // Transfer profit to Cold Storage (Owner) immediately
            IERC20(token).safeTransfer(owner, profit);
            emit ProfitSecured(token, profit);
        }

        emit FlashLoanExecuted(token, amount, premium);
        return true;
    }
    
    /**
     * @dev REAL EXECUTION LOGIC
     */
    function _executeDualTrade(ArbitrageData memory data) internal returns (uint256) {
        // LEG 1: TokenIn -> TokenMid (on Router 1)
        uint256 amountMid = _swap(
            data.router1, 
            data.tokenIn, 
            data.tokenMid, 
            data.amountIn
        );
        
        // LEG 2: TokenMid -> TokenIn (on Router 2)
        uint256 amountFinal = _swap(
            data.router2, 
            data.tokenMid, 
            data.tokenIn, 
            amountMid
        );
        
        return amountFinal;
    }
    
    /**
     * @dev LOW-LEVEL SWAPPER
     */
    function _swap(
        address router, 
        address _tokenIn, 
        address _tokenOut, 
        uint256 _amountIn
    ) internal returns (uint256) {
        IERC20(_tokenIn).approve(router, _amountIn);
        
        address[] memory path = new address[](2);
        path[0] = _tokenIn;
        path[1] = _tokenOut;
        
        // Call the Real Router
        // 0 amountOutMin = Frontrun Risk (Handled by MEVShield.sol usually, or Flashbots)
        uint[] memory amounts = IUniswapV2Router(router).swapExactTokensForTokens(
            _amountIn,
            0, 
            path,
            address(this),
            block.timestamp
        );
        
        emit TradeExecuted(router, _tokenIn, amounts[1]);
        return amounts[1];
    }
    
    /**
     * @dev EMERGENCY EJECT
     */
    function rescueFunds(address token) external onlyOwner {
        uint256 balance = IERC20(token).balanceOf(address(this));
        IERC20(token).safeTransfer(owner, balance);
    }
}