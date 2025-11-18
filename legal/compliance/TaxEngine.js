/**
 * AI-NEXUS Global Tax Calculation Engine
 * Multi-jurisdiction tax compliance and reporting
 */

class TaxEngine {
    constructor(config = {}) {
        this.config = {
            defaultJurisdiction: config.defaultJurisdiction || 'US',
            taxTreaties: config.taxTreaties || {},
            reportingThresholds: config.reportingThresholds || {},
            ...config
        };

        this.taxRates = this.initializeTaxRates();
        this.tradingActivity = [];
        this.taxLiabilities = new Map();
    }

    /**
     * Initialize tax rates for different jurisdictions
     */
    initializeTaxRates() {
        return {
            US: {
                shortTermRate: 0.37, // Federal + NIIT
                longTermRate: 0.20,
                washSalePeriod: 30,
                forms: ['8949', 'Schedule D'],
                reportingThreshold: 600 // USD
            },
            UK: {
                shortTermRate: 0.20,
                longTermRate: 0.20,
                allowance: 12570, // GBP
                forms: ['SA100'],
                reportingThreshold: 1000
            },
            EU: {
                shortTermRate: 0.25, // Average
                longTermRate: 0.25,
                forms: ['Various'],
                reportingThreshold: 500 // EUR
            },
            SG: {
                shortTermRate: 0.00, // No capital gains tax
                longTermRate: 0.00,
                forms: [],
                reportingThreshold: 0
            }
        };
    }

    /**
     * Calculate tax liability for a trade
     */
    calculateTradeTax(trade, jurisdiction = 'US') {
        const taxConfig = this.taxRates[jurisdiction];
        if (!taxConfig) {
            throw new Error(`No tax configuration for jurisdiction: ${jurisdiction}`);
        }

        const holdingPeriod = this.calculateHoldingPeriod(trade);
        const isLongTerm = holdingPeriod > 365; // 1 year threshold for long-term

        // Calculate gain/loss
        const costBasis = trade.quantity * trade.buyPrice;
        const proceeds = trade.quantity * trade.sellPrice;
        const gainLoss = proceeds - costBasis;

        // Apply tax rates
        let taxRate = isLongTerm ? taxConfig.longTermRate : taxConfig.shortTermRate;
        let taxLiability = gainLoss > 0 ? gainLoss * taxRate : 0;

        // Apply jurisdiction-specific rules
        taxLiability = this.applyJurisdictionRules(taxLiability, trade, jurisdiction);

        return {
            jurisdiction,
            tradeId: trade.id,
            gainLoss,
            holdingPeriod,
            taxRate,
            taxLiability,
            isLongTerm,
            costBasis,
            proceeds,
            currency: trade.currency
        };
    }

    /**
     * Calculate holding period in days
     */
    calculateHoldingPeriod(trade) {
        const buyDate = new Date(trade.buyTimestamp);
        const sellDate = new Date(trade.sellTimestamp);
        return Math.ceil((sellDate - buyDate) / (1000 * 60 * 60 * 24));
    }

    /**
     * Apply jurisdiction-specific tax rules
     */
    applyJurisdictionRules(taxLiability, trade, jurisdiction) {
        switch (jurisdiction) {
            case 'US':
                return this.applyUSRules(taxLiability, trade);
            case 'UK':
                return this.applyUKRules(taxLiability, trade);
            case 'EU':
                return this.applyEURules(taxLiability, trade);
            default:
                return taxLiability;
        }
    }

    /**
     * Apply US-specific tax rules
     */
    applyUSRules(taxLiability, trade) {
        // Check for wash sale
        if (this.isWashSale(trade)) {
            // Wash sale rules apply - disallow loss recognition
            if (trade.gainLoss < 0) {
                return 0; // Disallow loss deduction
            }
        }

        // Net Investment Income Tax (NIIT) for high incomes
        if (trade.proceeds > 200000) { // Threshold for NIIT
            taxLiability *= 1.038; // Additional 3.8% NIIT
        }

        return taxLiability;
    }

    /**
     * Check if trade qualifies as wash sale
     */
    isWashSale(trade) {
        const washSalePeriod = this.taxRates.US.washSalePeriod;
        const tradeDate = new Date(trade.sellTimestamp);
        const washSaleStart = new Date(tradeDate);
        washSaleStart.setDate(washSaleStart.getDate() - washSalePeriod);
        const washSaleEnd = new Date(tradeDate);
        washSaleEnd.setDate(washSaleEnd.getDate() + washSalePeriod);

        // Look for substantially identical securities bought in wash sale period
        const washTrades = this.tradingActivity.filter(t => 
            t.asset === trade.asset &&
            new Date(t.buyTimestamp) >= washSaleStart &&
            new Date(t.buyTimestamp) <= washSaleEnd &&
            t.id !== trade.id
        );

        return washTrades.length > 0;
    }

    /**
     * Apply UK-specific tax rules
     */
    applyUKRules(taxLiability, trade) {
        const allowance = this.taxRates.UK.allowance;

        // Apply annual allowance
        const annualGains = this.calculateAnnualGains(trade.sellTimestamp.getFullYear());
        if (annualGains <= allowance) {
            return 0; // Within tax-free allowance
        }

        // Only tax gains above allowance
        if (annualGains - trade.gainLoss > allowance) {
            return taxLiability; // Fully taxable
        } else {
            // Partial allowance application
            const taxableAmount = annualGains - allowance;
            return taxableAmount * this.taxRates.UK.shortTermRate;
        }
    }

    /**
     * Apply EU-specific tax rules (simplified)
     */
    applyEURules(taxLiability, trade) {
        // Many EU countries have progressive rates or exemptions
        // This is a simplified implementation
        return taxLiability;
    }

    /**
     * Calculate total gains for a tax year
     */
    calculateAnnualGains(taxYear) {
        const yearTrades = this.tradingActivity.filter(t => 
            new Date(t.sellTimestamp).getFullYear() === taxYear
        );

        return yearTrades.reduce((total, trade) => {
            const gainLoss = (trade.sellPrice - trade.buyPrice) * trade.quantity;
            return total + Math.max(0, gainLoss); // Only count gains for allowance
        }, 0);
    }

    /**
     * Generate tax report for jurisdiction and period
     */
    generateTaxReport(jurisdiction, taxYear) {
        const jurisdictionTrades = this.tradingActivity.filter(t => 
            new Date(t.sellTimestamp).getFullYear() === taxYear
        );

        const report = {
            jurisdiction,
            taxYear,
            summary: {
                totalTrades: jurisdictionTrades.length,
                totalProceeds: 0,
                totalCostBasis: 0,
                totalGainLoss: 0,
                totalTaxLiability: 0
            },
            trades: [],
            forms: this.taxRates[jurisdiction].forms
        };

        jurisdictionTrades.forEach(trade => {
            const taxCalculation = this.calculateTradeTax(trade, jurisdiction);

            report.summary.totalProceeds += taxCalculation.proceeds;
            report.summary.totalCostBasis += taxCalculation.costBasis;
            report.summary.totalGainLoss += taxCalculation.gainLoss;
            report.summary.totalTaxLiability += taxCalculation.taxLiability;

            report.trades.push({
                tradeId: trade.id,
                asset: trade.asset,
                buyDate: trade.buyTimestamp,
                sellDate: trade.sellTimestamp,
                quantity: trade.quantity,
                costBasis: taxCalculation.costBasis,
                proceeds: taxCalculation.proceeds,
                gainLoss: taxCalculation.gainLoss,
                holdingPeriod: taxCalculation.holdingPeriod,
                taxRate: taxCalculation.taxRate,
                taxLiability: taxCalculation.taxLiability
            });
        });

        return report;
    }

    /**
     * Generate multiple jurisdiction tax report
     */
    generateGlobalTaxReport(taxYear) {
        const reports = {};

        for (const jurisdiction of Object.keys(this.taxRates)) {
            reports[jurisdiction] = this.generateTaxReport(jurisdiction, taxYear);
        }

        // Calculate global totals
        const globalSummary = {
            totalTaxLiability: Object.values(reports).reduce(
                (sum, report) => sum + report.summary.totalTaxLiability, 0
            ),
            totalGainLoss: Object.values(reports).reduce(
                (sum, report) => sum + report.summary.totalGainLoss, 0
            ),
            jurisdictions: Object.keys(reports)
        };

        return {
            globalSummary,
            jurisdictionReports: reports
        };
    }

    /**
     * Record trading activity for tax purposes
     */
    recordTrade(trade) {
        this.tradingActivity.push(trade);

        // Calculate immediate tax liability
        const taxLiability = this.calculateTradeTax(trade, this.config.defaultJurisdiction);
        this.taxLiabilities.set(trade.id, taxLiability);
    }

    /**
     * Estimate tax liability for prospective trade
     */
    estimateTaxLiability(prospectiveTrade, jurisdiction = 'US') {
        return this.calculateTradeTax(prospectiveTrade, jurisdiction);
    }

    /**
     * Apply tax treaty benefits
     */
    applyTaxTreaty(taxLiability, homeJurisdiction, sourceJurisdiction) {
        const treatyKey = `${homeJurisdiction}-${sourceJurisdiction}`;
        const treaty = this.config.taxTreaties[treatyKey];

        if (treaty && treaty.withholdingRate) {
            // Reduce tax liability based on treaty withholding rate
            const reduction = taxLiability * (1 - treaty.withholdingRate);
            return Math.max(0, taxLiability - reduction);
        }

        return taxLiability;
    }

    /**
     * Generate tax forms data
     */
    generateFormData(formType, taxYear) {
        switch (formType) {
            case '8949': // US Form 8949
                return this.generateForm8949(taxYear);
            case 'Schedule D': // US Schedule D
                return this.generateScheduleD(taxYear);
            case 'SA100': // UK Self Assessment
                return this.generateSA100(taxYear);
            default:
                throw new Error(`Unsupported form type: ${formType}`);
        }
    }

    /**
     * Generate US Form 8949 data
     */
    generateForm8949(taxYear) {
        const usTrades = this.tradingActivity.filter(t => 
            new Date(t.sellTimestamp).getFullYear() === taxYear
        );

        return {
            form: '8949',
            taxYear,
            parts: {
                shortTerm: usTrades.filter(t => this.calculateHoldingPeriod(t) <= 365),
                longTerm: usTrades.filter(t => this.calculateHoldingPeriod(t) > 365)
            },
            totals: {
                shortTermProceeds: 0,
                shortTermCostBasis: 0,
                longTermProceeds: 0,
                longTermCostBasis: 0
            }
        };
    }

    /**
     * Generate US Schedule D data
     */
    generateScheduleD(taxYear) {
        const form8949 = this.generateForm8949(taxYear);

        return {
            form: 'Schedule D',
            taxYear,
            shortTerm: {
                totalProceeds: form8949.totals.shortTermProceeds,
                totalCostBasis: form8949.totals.shortTermCostBasis,
                netGain: form8949.totals.shortTermProceeds - form8949.totals.shortTermCostBasis
            },
            longTerm: {
                totalProceeds: form8949.totals.longTermProceeds,
                totalCostBasis: form8949.totals.longTermCostBasis,
                netGain: form8949.totals.longTermProceeds - form8949.totals.longTermCostBasis
            }
        };
    }

    /**
     * Generate UK SA100 data
     */
    generateSA100(taxYear) {
        const ukReport = this.generateTaxReport('UK', taxYear);

        return {
            form: 'SA100',
            taxYear,
            capitalGainsSummary: {
                totalGains: ukReport.summary.totalGainLoss,
                annualAllowance: this.taxRates.UK.allowance,
                taxableGains: Math.max(0, ukReport.summary.totalGainLoss - this.taxRates.UK.allowance),
                taxDue: ukReport.summary.totalTaxLiability
            }
        };
    }
}

module.exports = TaxEngine;
