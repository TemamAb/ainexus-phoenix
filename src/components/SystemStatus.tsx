"use client"

import { SystemData } from '@/types/dashboard'
import { Server, Cpu, Activity } from 'lucide-react'

interface SystemStatusProps {
  data: SystemData | null
}

export default function SystemStatus({ data }: SystemStatusProps) {
  const getStatusColor = (status: string) => {
    return status === 'connected' || status === 'running' 
      ? 'text-green-400' 
      : 'text-red-400'
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center gap-3 mb-4">
        <Server className="w-6 h-6 text-cyan-400" />
        <h2 className="text-xl font-semibold">íº€ System Status</h2>
      </div>
      
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-gray-400">Platform</span>
          <span className="text-green-400 flex items-center gap-1">
            <Activity className="w-4 h-4" />
            OPERATIONAL
          </span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-gray-400">Version</span>
          <span className="text-white">v1.0.0</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-gray-400">API Health</span>
          <span className="text-green-400">HEALTHY</span>
        </div>
        
        {data?.infrastructure && (
          <>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Redis</span>
              <span className={getStatusColor(data.infrastructure.redis)}>
                {data.infrastructure.redis.toUpperCase()}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">PostgreSQL</span>
              <span className={getStatusColor(data.infrastructure.postgres)}>
                {data.infrastructure.postgres.toUpperCase()}
              </span>
            </div>
          </>
        )}
        
        <div className="pt-3 border-t border-gray-700">
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-400">Last Update</span>
            <span className="text-gray-300">
              {data?.timestamp ? new Date(data.timestamp).toLocaleTimeString() : 'Loading...'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
