"use client"

import { BotStatus } from '@/types/dashboard'
import { Play, Square, Settings } from 'lucide-react'

interface BotArmyProps {
  bots: BotStatus | null
}

export default function BotArmy({ bots }: BotArmyProps) {
  const botsList = [
    { id: 'scanner', name: 'Scanner Bot', description: 'Market opportunity detection' },
    { id: 'executor', name: 'Executor Bot', description: 'Trade execution engine' },
    { id: 'validator', name: 'Validator Bot', description: 'Risk validation system' },
  ]

  const getStatusColor = (status: string) => {
    return status === 'running' ? 'text-green-400' : 'text-red-400'
  }

  const handleBotControl = (botId: string, action: 'start' | 'stop') => {
    // TODO: Implement bot control API calls
    console.log(`${action} ${botId}`)
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Settings className="w-6 h-6 text-cyan-400" />
          <h2 className="text-xl font-semibold">Ì¥ñ Bot Army</h2>
        </div>
        <span className="text-sm text-gray-400">
          {bots ? '3/3' : '0/3'} Active
        </span>
      </div>
      
      <div className="space-y-4">
        {botsList.map((bot) => {
          const status = bots ? bots[bot.id as keyof BotStatus] : 'unknown'
          const isRunning = status === 'running'
          
          return (
            <div key={bot.id} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-white">{bot.name}</span>
                  <span className={`text-xs ${getStatusColor(status || '')}`}>
                    ‚óè {isRunning ? 'RUNNING' : 'STOPPED'}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mt-1">{bot.description}</p>
              </div>
              
              <div className="flex gap-2">
                <button
                  onClick={() => handleBotControl(bot.id, isRunning ? 'stop' : 'start')}
                  className={`p-2 rounded-lg transition-colors ${
                    isRunning 
                      ? 'bg-red-500 hover:bg-red-600' 
                      : 'bg-green-500 hover:bg-green-600'
                  }`}
                >
                  {isRunning ? <Square className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
