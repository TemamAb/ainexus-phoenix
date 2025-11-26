'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';

export type EngineState = 'IDLE' | 'SIMULATION' | 'TRANSITION' | 'LIVE';
interface Metrics {
  balance: number; lifetimeProfit: number; tradesPerHour: number;
  latencyMs: number; mevBlocked: number; aiEfficiencyDelta: number;
}

const EngineContext = createContext<any>(null);

export const EngineProvider = ({ children }: { children: React.ReactNode }) => {
  const [state, setState] = useState<EngineState>('IDLE');
  const [metrics, setMetrics] = useState<Metrics>({
    balance: 0, lifetimeProfit: 0, tradesPerHour: 0,
    latencyMs: 45, mevBlocked: 0, aiEfficiencyDelta: 0
  });
  const [confidence, setConfidence] = useState(0);

  const startEngine = () => {
    setState('SIMULATION');
    let conf = 0;
    const interval = setInterval(() => {
      conf += 5; setConfidence(conf);
      if (conf >= 85) { clearInterval(interval); setState('TRANSITION'); }
    }, 200);
  };

  const confirmLive = () => {
    setState('LIVE');
    setMetrics(prev => ({...prev, balance: 50000})); // Mock Initial Capital
  };

  // The Data Stream Simulation
  useEffect(() => {
    if (state === 'IDLE') return;
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        balance: prev.balance + (state === 'LIVE' ? Math.random() * 50 : Math.random() * 5),
        tradesPerHour: state === 'LIVE' ? 142 : 0,
        latencyMs: 20 + Math.random() * 30,
        mevBlocked: prev.mevBlocked + (Math.random() > 0.9 ? 1 : 0),
        aiEfficiencyDelta: prev.aiEfficiencyDelta + 0.1
      }));
    }, 1000);
    return () => clearInterval(interval);
  }, [state]);

  return (
    <EngineContext.Provider value={{ state, metrics, confidence, startEngine, confirmLive }}>
      {children}
    </EngineContext.Provider>
  );
};

export const useEngine = () => useContext(EngineContext);
