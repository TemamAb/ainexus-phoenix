"use client"

import { SystemData } from '@/types/dashboard'
import { Database, Cpu, Network, Server } from 'lucide-react'

interface InfrastructureProps {
  data: SystemData | null
}

export default function Infrastructure({ data }: InfrastructureProps) {
  const services = [
    { name: 'Redis Cache', status: data?.infrastructure?.redis || 'connected', icon: Database },
    { name: 'PostgreSQL', status: data?.infrastructure?.postgres || 'connected', icon: Server },
    { name: 'Blockchain Nodes', status: '5/5 online', icon: Network },
    { name: 'CPU Load', status: '42%', icon: Cpu },
  ]

  const getStatusColor = (status: string) => {
    if (status === 'connected') return 'text-green-400'
    if (status.includes('/')) return 'text-yellow-400'
    return 'text-gray-400'
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center gap-3 mb-6">
        <Server className="w-6 h-6 text-cyan-400" />
        <h2 className="text-xl font-semibold">Ì∑ÑÔ∏è Infrastructure</h2>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {services.map((service, index) => (
          <div key={index} className="flex items-center gap-4 p-4 bg-gray-700 rounded-lg">
            <service.icon className="w-8 h-8 text-blue-400" />
            <div className="flex-1">
              <div className="font-medium text-white">{service.name}</div>
              <div className={`text-sm ${getStatusColor(service.status)}`}>
                {service.status.toUpperCase()}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Multi-Chain Status */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <h3 className="font-semibold text-white mb-3">Ìºê Multi-Chain Status</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
          {['Ethereum', 'Polygon', 'BSC', 'Arbitrum'].map((chain) => (
            <div key={chain} className="flex items-center gap-2 p-2 bg-gray-700 rounded">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <span className="text-gray-300">{chain}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
