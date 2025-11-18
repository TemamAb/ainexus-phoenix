/**
 * AI-NEXUS v5.0 - Priority Fee Calculator
 * 7P-PILLAR: BOT13-GAS
 * PURPOSE: Dynamic priority fee calculation for EIP-1559
 */

const { ethers } = require('ethers');

class PriorityFeeCalculator {
    constructor(config) {
        this.config = config;
        this.historicalData = [];
        this.networkConditions = {};
        this.feePredictions = new Map();
        
        this.optimizationStrategies = {
            'conservative': this.calculateConservativeFee.bind(this),
            'standard': this.calculateStandardFee.bind(this),
            'aggressive': this.calculateAggressiveFee.bind(this),
            'adaptive': this.calculateAdaptiveFee.bind(this)
        };
    }

    async calculateOptimalPriorityFee(transaction, strategy = 'adaptive', networkState) {
        const calculationFn = this.optimizationStrategies[strategy];
        if (!calculationFn) {
            throw new Error(`Unknown fee strategy: ${strategy}`);
        }

        const baseFee = networkState.baseFeePerGas;
        const currentConditions = await this.analyzeNetworkConditions(networkState);
        
        const optimalFee = await calculationFn(transaction, baseFee, currentConditions);
        const validatedFee = this.validatePriorityFee(optimalFee, baseFee, currentConditions);
        
        this.recordFeeCalculation({
            transaction,
            strategy,
            baseFee,
            calculatedFee: validatedFee,
            networkConditions: currentConditions,
            timestamp: Date.now()
        });
        
        return validatedFee;
    }

    async calculateConservativeFee(transaction, baseFee, networkConditions) {
        const historicalPercentile = this.getHistoricalPercentile(0.25);
        const basePriority = historicalPercentile || ethers.utils.parseUnits('1', 'gwei');
        
        let adjustedFee = basePriority;
        
        if (networkConditions.congestionLevel > 0.7) {
            adjustedFee = adjustedFee.mul(120).div(100);
        }
        
        return this.applyTransactionSpecificAdjustments(adjustedFee, transaction, networkConditions);
    }

    async calculateStandardFee(transaction, baseFee, networkConditions) {
        const historicalPercentile = this.getHistoricalPercentile(0.5);
        const basePriority = historicalPercentile || ethers.utils.parseUnits('2', 'gwei');
        
        let adjustedFee = basePriority;
        
        if (networkConditions.congestionLevel > 0.8) {
            adjustedFee = adjustedFee.mul(150).div(100);
        } else if (networkConditions.congestionLevel < 0.3) {
            adjustedFee = adjustedFee.mul(80).div(100);
        }
        
        return this.applyTransactionSpecificAdjustments(adjustedFee, transaction, networkConditions);
    }

    async calculateAggressiveFee(transaction, baseFee, networkConditions) {
        const historicalPercentile = this.getHistoricalPercentile(0.75);
        const basePriority = historicalPercentile || ethers.utils.parseUnits('3', 'gwei');
        
        let adjustedFee = basePriority.mul(120).div(100);
        
        if (networkConditions.congestionLevel > 0.6) {
            adjustedFee = adjustedFee.mul(180).div(100);
        }
        
        if (transaction.type === 'arbitrage') {
            adjustedFee = adjustedFee.mul(150).div(100);
        }
        
        return adjustedFee;
    }

    async calculateAdaptiveFee(transaction, baseFee, networkConditions) {
        const predictedFee = await this.predictOptimalFee(transaction, networkConditions);
        
        if (predictedFee) {
            return predictedFee;
        }
        
        const conservative = await this.calculateConservativeFee(transaction, baseFee, networkConditions);
        const standard = await this.calculateStandardFee(transaction, baseFee, networkConditions);
        const aggressive = await this.calculateAggressiveFee(transaction, baseFee, networkConditions);
        
        const weights = this.calculateAdaptiveWeights(transaction, networkConditions);
        
        const weightedFee = conservative.mul(weights.conservative)
            .add(standard.mul(weights.standard))
            .add(aggressive.mul(weights.aggressive))
            .div(weights.conservative + weights.standard + weights.aggressive);
        
        return weightedFee;
    }

    async analyzeNetworkConditions(networkState) {
        const {
            baseFeePerGas,
            gasUsedRatio,
            pendingTransactions,
            blockNumber
        } = networkState;
        
        const congestionLevel = this.calculateCongestionLevel(gasUsedRatio, pendingTransactions);
        const baseFeeTrend = await this.analyzeBaseFeeTrend(baseFeePerGas);
        const inclusionProbability = this.estimateInclusionProbability(congestionLevel, baseFeeTrend);
        
        return {
            congestionLevel,
            baseFeeTrend,
            inclusionProbability,
            gasUsedRatio: gasUsedRatio || [],
            pendingTransactions: pendingTransactions || 0,
            timestamp: Date.now()
        };
    }

    calculateCongestionLevel(gasUsedRatio, pendingTransactions) {
        let congestion = 0;
        
        if (gasUsedRatio && gasUsedRatio.length > 0) {
            const recentUtilization = gasUsedRatio.slice(-10);
            const avgUtilization = recentUtilization.reduce((a, b) => a + b, 0) / recentUtilization.length;
            congestion += avgUtilization * 0.6;
        }
        
        const normalizedPending = Math.min(pendingTransactions / 10000, 1);
        congestion += normalizedPending * 0.4;
        
        return Math.min(congestion, 1);
    }

    async analyzeBaseFeeTrend(currentBaseFee) {
        if (this.historicalData.length < 5) {
            return 'stable';
        }
        
        const recentBaseFees = this.historicalData
            .slice(-10)
            .map(data => data.baseFeePerGas);
        
        if (recentBaseFees.length < 3) {
            return 'stable';
        }
        
        const current = parseFloat(ethers.utils.formatUnits(currentBaseFee, 'gwei'));
        const previous = parseFloat(ethers.utils.formatUnits(recentBaseFees[recentBaseFees.length - 2], 'gwei'));
        
        const change = (current - previous) / previous;
        
        if (change > 0.1) return 'rising';
        if (change < -0.1) return 'falling';
        return 'stable';
    }

    estimateInclusionProbability(congestionLevel, baseFeeTrend) {
        let probability = 0.8;
        
        probability -= congestionLevel * 0.3;
        
        if (baseFeeTrend === 'rising') {
            probability -= 0.1;
        } else if (baseFeeTrend === 'falling') {
            probability += 0.1;
        }
        
        return Math.max(0.1, Math.min(0.95, probability));
    }

    applyTransactionSpecificAdjustments(baseFee, transaction, networkConditions) {
        let adjustedFee = baseFee;
        
        switch (transaction.type) {
            case 'arbitrage':
                adjustedFee = adjustedFee.mul(140).div(100);
                break;
            case 'liquidation':
                adjustedFee = adjustedFee.mul(130).div(100);
                break;
            case 'flash_loan':
                adjustedFee = adjustedFee.mul(110).div(100);
                break;
            case 'governance':
                adjustedFee = adjustedFee.mul(80).div(100);
                break;
        }
        
        if (transaction.value) {
            const valueInEth = parseFloat(ethers.utils.formatEther(transaction.value));
            if (valueInEth > 10) {
                const boost = Math.min(valueInEth / 100, 0.5);
                adjustedFee = adjustedFee.mul(100 + Math.floor(boost * 100)).div(100);
            }
        }
        
        return adjustedFee;
    }

    calculateAdaptiveWeights(transaction, networkConditions) {
        const weights = {
            conservative: 1,
            standard: 1,
            aggressive: 1
        };
        
        if (networkConditions.congestionLevel > 0.8) {
            weights.aggressive += 2;
            weights.standard += 1;
        } else if (networkConditions.congestionLevel < 0.3) {
            weights.conservative += 2;
        }
        
        if (transaction.type === 'arbitrage' || transaction.type === 'liquidation') {
            weights.aggressive += 3;
            weights.standard += 1;
        }
        
        if (networkConditions.baseFeeTrend === 'rising') {
            weights.aggressive += 1;
        }
        
        return weights;
    }

    getHistoricalPercentile(percentile) {
        if (this.historicalData.length === 0) {
            return null;
        }
        
        const priorityFees = this.historicalData
            .map(data => data.priorityFeePerGas)
            .filter(fee => fee)
            .sort((a, b) => a.sub(b).isNegative() ? -1 : 1);
        
        if (priorityFees.length === 0) {
            return null;
        }
        
        const index = Math.floor(priorityFees.length * percentile);
        return priorityFees[Math.min(index, priorityFees.length - 1)];
    }

    async predictOptimalFee(transaction, networkConditions) {
        const basePrediction = ethers.utils.parseUnits('2', 'gwei');
        
        let adjustment = 100;
        
        adjustment += Math.floor(networkConditions.congestionLevel * 40);
        
        if (transaction.type === 'arbitrage') adjustment += 30;
        if (transaction.type === 'liquidation') adjustment += 20;
        
        if (transaction.timeSensitive) adjustment += 25;
        
        return basePrediction.mul(adjustment).div(100);
    }

    validatePriorityFee(priorityFee, baseFee, networkConditions) {
        const minFee = ethers.utils.parseUnits('0.1', 'gwei');
        const maxFee = ethers.utils.parseUnits('100', 'gwei');
        
        let validatedFee = priorityFee;
        
        if (validatedFee.lt(minFee)) {
            validatedFee = minFee;
        }
        
        if (validatedFee.gt(maxFee)) {
            validatedFee = maxFee;
        }
        
        const baseFeeGwei = parseFloat(ethers.utils.formatUnits(baseFee, 'gwei'));
        const priorityFeeGwei = parseFloat(ethers.utils.formatUnits(validatedFee, 'gwei'));
        
        if (priorityFeeGwei > baseFeeGwei * 10) {
            if (networkConditions.congestionLevel < 0.9) {
                validatedFee = baseFee.mul(10);
            }
        }
        
        return validatedFee;
    }

    recordFeeCalculation(calculation) {
        this.historicalData.push(calculation);
        
        if (this.historicalData.length > 1000) {
            this.historicalData = this.historicalData.slice(-1000);
        }
    }

    async updateNetworkState(networkState) {
        this.networkConditions = await this.analyzeNetworkConditions(networkState);
        
        this.historicalData.push({
            ...networkState,
            timestamp: Date.now()
        });
    }

    getFeeStatistics() {
        const recentCalculations = this.historicalData.slice(-100);
        
        if (recentCalculations.length === 0) {
            return {
                averageFee: '0',
                successRate: 0,
                averageCongestion: 0
            };
        }
        
        const averageFee = recentCalculations
            .reduce((sum, calc) => sum.add(calc.calculatedFee), ethers.BigNumber.from(0))
            .div(recentCalculations.length);
            
        const averageCongestion = recentCalculations
            .reduce((sum, calc) => sum + (calc.networkConditions?.congestionLevel || 0), 0)
            / recentCalculations.length;
        
        return {
            averageFee: ethers.utils.formatUnits(averageFee, 'gwei'),
            averageCongestion,
            calculationsCount: recentCalculations.length,
            recentStrategies: this.getStrategyDistribution(recentCalculations)
        };
    }

    getStrategyDistribution(calculations) {
        const distribution = {};
        
        calculations.forEach(calc => {
            distribution[calc.strategy] = (distribution[calc.strategy] || 0) + 1;
        });
        
        return distribution;
    }
}

module.exports = PriorityFeeCalculator;
