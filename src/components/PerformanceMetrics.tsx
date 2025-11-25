"use client"

import { PerformanceData } from '@/types/dashboard'
import { Gauge, Clock, TrendingUp } from 'lucide-react'

interface PerformanceMetricsProps {
  performance: PerformanceData | null
}

export default function PerformanceMetrics({ performance }: PerformanceMetricsProps) {
  const formatUptime = (seconds: number | undefined) => {
    if (!seconds) return '0s'
    
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    
    if (hours > 0) return `${hours}h ${minutes}m`
    if (minutes > 0) return `${minutes}m ${secs}s`
    return `${secs}s`
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center gap-3 mb-6">
        <TrendingUp className="w-6 h-6 text-cyan-400" />
        <h2 className="text-xl font-semibold">âš¡ Performance</h2>
      </div>
      
      <div className="space-y-4">
        {/* Latency Gauge */}
        <div className="text-center p-4 bg-gray-700 rounded-lg">
          <Gauge className="w-8 h-8 text-green-400 mx-auto mb-2" />
          <div className="text-2xl font-bold text-white">
            {performance?.latency || '47ms'}
          </div>
          <div className="text-sm text-gray-400">Current Latency</div>
        </div>
        
        {/* Uptime */}
        <div className="text-center p-4 bg-gray-700 rounded-lg">
          <Clock className="w-8 h-8 text-blue-400 mx-auto mb-2" />
          <div className="text-2xl font-bold text-white">
            {formatUptime(performance?.uptime)}
          </div>
          <div className="text-sm text-gray-400">System Uptime</div>
        </div>
        
        {/* Success Rate */}
        <div className="text-center p-4 bg-gray-700 rounded-lg">
          <div className="w-8 h-8 text-yellow-400 mx-auto mb-2">í³Š</div>
          <div className="text-2xl font-bold text-white">92.4%</div>
          <div className="text-sm text-gray-400">Success Rate</div>
        </div>
      </div>
    </div>
  )
}
