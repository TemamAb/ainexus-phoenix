'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

export type EngineState = 'IDLE' | 'SIMULATION' | 'TRANSITION' | 'LIVE';
export type Currency = 'ETH' | 'USD';

interface Metrics {
  balance: number;
  lifetimeProfit: number;
  tradesPerHour: number;
  profitPerHour: number;
  latencyMs: number;
  mevBlocked: number;
  aiEfficiencyDelta: number;
  nextAiRun: number;
}

interface EngineContextType {
  state: EngineState;
  currency: Currency;
  refreshRate: number;
  metrics: Metrics;
  toggleCurrency: () => void;
  setRefreshRate: (ms: number) => void;
  startEngine: () => void;
  confirmLive: () => void;
  confidence: number;
}

const EngineContext = createContext<EngineContextType | null>(null);

export const EngineProvider = ({ children }: { children: React.ReactNode }) => {
  const [state, setState] = useState<EngineState>('IDLE');
  const [currency, setCurrency] = useState<Currency>('USD');
  const [refreshRate, setRefreshRate] = useState(1000);
  const [confidence, setConfidence] = useState(0);
  
  const [metrics, setMetrics] = useState<Metrics>({
    balance: 0,
    lifetimeProfit: 0,
    tradesPerHour: 0,
    profitPerHour: 0,
    latencyMs: 45,
    mevBlocked: 0,
    aiEfficiencyDelta: 0,
    nextAiRun: 900
  });

  const startEngine = () => {
    setState('SIMULATION');
    let conf = 0;
    const interval = setInterval(() => {
      conf += 5;
      setConfidence(conf);
      if (conf >= 85) {
        clearInterval(interval);
        setState('TRANSITION');
      }
    }, 500);
  };

  const confirmLive = () => {
    setConfidence(100);
    setMetrics(prev => ({ ...prev, balance: 50000, lifetimeProfit: 0 }));
    setState('LIVE');
  };

  useEffect(() => {
    if (state === 'IDLE') return;
    const stream = setInterval(() => {
      setMetrics(prev => {
        const isLive = state === 'LIVE';
        const profitTick = isLive ? (Math.random() * 50) : (Math.random() * 10);
        return {
          ...prev,
          balance: prev.balance + profitTick,
          lifetimeProfit: prev.lifetimeProfit + profitTick,
          tradesPerHour: isLive ? 142 : 0,
          profitPerHour: isLive ? 2450 : 0,
          latencyMs: 20 + Math.random() * 30,
          mevBlocked: prev.mevBlocked + (Math.random() > 0.9 ? 1 : 0),
          nextAiRun: prev.nextAiRun > 0 ? prev.nextAiRun - (refreshRate/1000) : 900,
          aiEfficiencyDelta: prev.nextAiRun <= 0 ? (prev.aiEfficiencyDelta + 0.1) : prev.aiEfficiencyDelta
        };
      });
    }, refreshRate);
    return () => clearInterval(stream);
  }, [state, refreshRate]);

  return (
    <EngineContext.Provider value={{
      state, currency, refreshRate, metrics, confidence,
      toggleCurrency: () => setCurrency(c => c === 'USD' ? 'ETH' : 'USD'),
      setRefreshRate, startEngine, confirmLive
    }}>
      {children}
    </EngineContext.Provider>
  );
};

export const useEngine = () => {
  const context = useContext(EngineContext);
  if (!context) throw new Error("useEngine must be used within EngineProvider");
  return context;
};
