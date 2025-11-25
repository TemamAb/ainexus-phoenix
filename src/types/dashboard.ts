export interface SystemData {
  infrastructure?: {
    redis: string
    postgres: string
  }
  timestamp?: string
}

export interface BotStatus {
  scanner?: string
  executor?: string
  validator?: string
}

export interface PerformanceData {
  latency?: string
  uptime?: number
}

export interface ProfitData {
  today: number
  week: number
  month: number
  total: number
  pendingWithdrawal: number
}

export interface DeploymentStatus {
  status: 'idle' | 'deploying' | 'success' | 'error'
  message: string
  timestamp: string
}
