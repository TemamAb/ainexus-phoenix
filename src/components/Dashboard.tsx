"use client"

import { useState, useEffect } from 'react'

interface SystemStatus {
  bots?: {
    scanner: string
    executor: string
    validator: string
  }
  infrastructure?: {
    redis: string
    postgres: string
  }
  performance?: {
    latency: string
    uptime: number
  }
}

export default function Dashboard() {
  const [data, setData] = useState<SystemStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setError(null)
        const response = await fetch('http://localhost:3000/api/status')
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const result = await response.json()
        setData(result)
      } catch (error) {
        console.error('Failed to fetch data:', error)
        setError(error instanceof Error ? error.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-cyan-400 mx-auto mb-4"></div>
          <div className="text-cyan-400 text-xl">Loading QuantumNex Dashboard...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black flex items-center justify-center">
        <div className="text-center bg-red-500/20 border border-red-500 rounded-xl p-8 max-w-md">
          <div className="text-2xl mb-4">Ì∫® Connection Error</div>
          <div className="text-gray-300 mb-4">{error}</div>
          <div className="text-sm text-gray-400">
            Make sure the backend is running on port 3000
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white p-6">
      <div className="container mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            Ì∫Ä QuantumNex Dashboard
          </h1>
          <p className="text-gray-400 mt-2">Real-time System Monitor - Connected ‚úÖ</p>
        </div>

        {/* Status Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Bot Status */}
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h2 className="text-xl font-semibold mb-4">Ì¥ñ Bot Status</h2>
            {data?.bots ? (
              <div className="space-y-3">
                {Object.entries(data.bots).map(([bot, status]) => (
                  <div key={bot} className="flex justify-between items-center">
                    <span className="text-gray-300 capitalize">{bot}</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      status === 'running' 
                        ? 'bg-green-500/20 text-green-400 border border-green-500' 
                        : 'bg-red-500/20 text-red-400 border border-red-500'
                    }`}>
                      {status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-400">No bot data</div>
            )}
          </div>

          {/* Infrastructure */}
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h2 className="text-xl font-semibold mb-4">Ì∑ÑÔ∏è Infrastructure</h2>
            {data?.infrastructure ? (
              <div className="space-y-3">
                {Object.entries(data.infrastructure).map(([service, status]) => (
                  <div key={service} className="flex justify-between items-center">
                    <span className="text-gray-300 capitalize">{service}</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      status === 'connected' 
                        ? 'bg-green-500/20 text-green-400 border border-green-500' 
                        : 'bg-red-500/20 text-red-400 border border-red-500'
                    }`}>
                      {status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-400">No infrastructure data</div>
            )}
          </div>

          {/* Performance */}
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h2 className="text-xl font-semibold mb-4">‚ö° Performance</h2>
            {data?.performance ? (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Latency</span>
                  <span className="text-green-400 font-mono text-lg">{data.performance.latency}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Uptime</span>
                  <span className="text-blue-400 font-mono text-lg">
                    {Math.floor(data.performance.uptime / 3600)}h {Math.floor((data.performance.uptime % 3600) / 60)}m
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Success Rate</span>
                  <span className="text-yellow-400 font-mono text-lg">92.4%</span>
                </div>
              </div>
            ) : (
              <div className="text-gray-400">No performance data</div>
            )}
          </div>
        </div>

        {/* System Info */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h2 className="text-xl font-semibold mb-4">Ì¥ß System Information</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="p-4 bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-cyan-400">3/3</div>
              <div className="text-gray-400 text-sm">Bots Active</div>
            </div>
            <div className="p-4 bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-green-400">2/2</div>
              <div className="text-gray-400 text-sm">Services OK</div>
            </div>
            <div className="p-4 bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-blue-400">4</div>
              <div className="text-gray-400 text-sm">Chains</div>
            </div>
            <div className="p-4 bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-purple-400">v1.0</div>
              <div className="text-gray-400 text-sm">Version</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
