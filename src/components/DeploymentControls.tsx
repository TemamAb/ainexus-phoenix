"use client"

import { useState } from 'react'
import { Rocket, Play, Square, RefreshCw, Settings } from 'lucide-react'
import { DeploymentStatus } from '@/types/dashboard'

export default function DeploymentControls() {
  const [deploymentStatus, setDeploymentStatus] = useState<DeploymentStatus>({
    status: 'idle',
    message: 'Ready for deployment',
    timestamp: new Date().toISOString()
  })

  const deploymentActions = [
    { id: 'deploy-bots', name: 'Deploy Trading Bots', description: 'Launch new bot instances' },
    { id: 'upgrade-contracts', name: 'Upgrade Contracts', description: 'Deploy new smart contracts' },
    { id: 'scale-infrastructure', name: 'Scale Infrastructure', description: 'Adjust resource allocation' },
    { id: 'emergency-stop', name: 'Emergency Stop', description: 'Halt all trading activity', dangerous: true },
  ]

  const handleDeployment = async (actionId: string) => {
    setDeploymentStatus({
      status: 'deploying',
      message: `Executing ${actionId}...`,
      timestamp: new Date().toISOString()
    })

    // TODO: Connect to deployment-manager.js API
    await new Promise(resolve => setTimeout(resolve, 3000))

    setDeploymentStatus({
      status: 'success',
      message: `${actionId} completed successfully`,
      timestamp: new Date().toISOString()
    })
  }

  const getStatusColor = () => {
    switch (deploymentStatus.status) {
      case 'deploying': return 'text-yellow-400'
      case 'success': return 'text-green-400'
      case 'error': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center gap-3 mb-6">
        <Rocket className="w-6 h-6 text-cyan-400" />
        <h2 className="text-xl font-semibold">íº€ Deployment Controls</h2>
      </div>

      {/* Deployment Status */}
      <div className="mb-6 p-4 bg-gray-700 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <div className={`font-medium ${getStatusColor()}`}>
              {deploymentStatus.status.toUpperCase()}
            </div>
            <div className="text-sm text-gray-400">{deploymentStatus.message}</div>
          </div>
          <div className="text-sm text-gray-400">
            {new Date(deploymentStatus.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Deployment Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {deploymentActions.map((action) => (
          <button
            key={action.id}
            onClick={() => handleDeployment(action.id)}
            disabled={deploymentStatus.status === 'deploying'}
            className={`p-4 text-left rounded-lg transition-all ${
              action.dangerous
                ? 'bg-red-500/20 border border-red-500 hover:bg-red-500/30'
                : 'bg-gray-700 hover:bg-gray-600'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            <div className="flex items-center gap-2 mb-2">
              {action.dangerous ? <Square className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              <span className="font-medium text-white">{action.name}</span>
            </div>
            <p className="text-sm text-gray-400">{action.description}</p>
          </button>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <h3 className="font-semibold text-white mb-3">âš¡ Quick Actions</h3>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg transition-colors">
            <RefreshCw className="w-4 h-4" />
            Restart All Bots
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg transition-colors">
            <Settings className="w-4 h-4" />
            Optimize Performance
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-yellow-500 hover:bg-yellow-600 rounded-lg transition-colors">
            <Rocket className="w-4 h-4" />
            Deploy All
          </button>
        </div>
      </div>
    </div>
  )
}
