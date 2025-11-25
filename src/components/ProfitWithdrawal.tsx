"use client"

import { useState, useEffect } from 'react'
import { DollarSign, TrendingUp, Download, History } from 'lucide-react'
import { ProfitData } from '@/types/dashboard'

export default function ProfitWithdrawal() {
  const [profitData, setProfitData] = useState<ProfitData>({
    today: 1247.32,
    week: 8743.15,
    month: 32467.89,
    total: 156789.42,
    pendingWithdrawal: 5000.00
  })
  
  const [withdrawalAmount, setWithdrawalAmount] = useState('')
  const [isWithdrawing, setIsWithdrawing] = useState(false)

  const handleWithdrawal = async () => {
    if (!withdrawalAmount || parseFloat(withdrawalAmount) <= 0) return
    
    setIsWithdrawing(true)
    // TODO: Connect to withdrawal-manager.js API
    await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate API call
    
    console.log('Withdrawal requested:', withdrawalAmount)
    setIsWithdrawing(false)
    setWithdrawalAmount('')
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center gap-3 mb-6">
        <DollarSign className="w-6 h-6 text-green-400" />
        <h2 className="text-xl font-semibold">í²° Profit & Withdrawal</h2>
      </div>
      
      {/* Profit Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="text-center p-4 bg-gray-700 rounded-lg">
          <div className="text-2xl font-bold text-green-400">${profitData.today.toLocaleString()}</div>
          <div className="text-sm text-gray-400">Today</div>
        </div>
        
        <div className="text-center p-4 bg-gray-700 rounded-lg">
          <div className="text-2xl font-bold text-blue-400">${profitData.week.toLocaleString()}</div>
          <div className="text-sm text-gray-400">This Week</div>
        </div>
        
        <div className="text-center p-4 bg-gray-700 rounded-lg">
          <div className="text-2xl font-bold text-purple-400">${profitData.month.toLocaleString()}</div>
          <div className="text-sm text-gray-400">This Month</div>
        </div>
        
        <div className="text-center p-4 bg-gray-700 rounded-lg">
          <div className="text-2xl font-bold text-cyan-400">${profitData.total.toLocaleString()}</div>
          <div className="text-sm text-gray-400">Total Profit</div>
        </div>
      </div>
      
      {/* Withdrawal Section */}
      <div className="bg-gray-700 rounded-lg p-4">
        <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
          <Download className="w-4 h-4" />
          Quick Withdrawal
        </h3>
        
        <div className="flex gap-3 mb-3">
          <input
            type="number"
            value={withdrawalAmount}
            onChange={(e) => setWithdrawalAmount(e.target.value)}
            placeholder="Amount to withdraw"
            className="flex-1 px-3 py-2 bg-gray-600 border border-gray-500 rounded-lg text-white placeholder-gray-400"
          />
          <button
            onClick={handleWithdrawal}
            disabled={isWithdrawing || !withdrawalAmount}
            className="px-6 py-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-600 rounded-lg font-medium transition-colors"
          >
            {isWithdrawing ? 'Processing...' : 'Withdraw'}
          </button>
        </div>
        
        <div className="text-sm text-gray-400">
          Available: ${profitData.pendingWithdrawal.toLocaleString()} | Multi-sig required above $10,000
        </div>
      </div>
      
      {/* Recent Activity */}
      <div className="mt-4">
        <h3 className="font-semibold text-white mb-2 flex items-center gap-2">
          <History className="w-4 h-4" />
          Recent Activity
        </h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between text-gray-300">
            <span>ETH-USDC Arbitrage</span>
            <span className="text-green-400">+$247.15</span>
          </div>
          <div className="flex justify-between text-gray-300">
            <span>Polygon Yield Farming</span>
            <span className="text-green-400">+$89.42</span>
          </div>
          <div className="flex justify-between text-gray-300">
            <span>Withdrawal Processed</span>
            <span className="text-red-400">-$2,000.00</span>
          </div>
        </div>
      </div>
    </div>
  )
}
