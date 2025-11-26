'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';

export type EngineState = 'IDLE' | 'BOOTING' | 'SIMULATION' | 'TRANSITION' | 'LIVE';
const EngineContext = createContext<any>(null);

export const EngineProvider = ({ children }: { children: React.ReactNode }) => {
  const [state, setState] = useState<EngineState>('IDLE');
  const [bootLog, setBootLog] = useState<string[]>([]);
  const [metrics, setMetrics] = useState({
    balance: 0, latencyMs: 45, mevBlocked: 0, aiEfficiencyDelta: 0
  });
  const [confidence, setConfidence] = useState(0);

  const startEngine = () => {
    setState('BOOTING');
    const logs = [
      "Initialising QuantumNex Core...", "Environment Secrets [OK]", "Fireblocks MPC [SECURE]",
      "Gasless Paymaster [ACTIVE]", "Flash Loan Contracts [LINKED]", "AI Models [LOADED]",
      "Bot Tier 1: SCANNERS [ONLINE]", "Bot Tier 2: ORCHESTRATORS [OPTIMIZED]",
      "Bot Tier 3: RELAYERS [READY]", "MEV Shield [ENABLED]", "SYSTEM PASS."
    ];
    let i = 0;
    setBootLog([]);
    const interval = setInterval(() => {
      if (i >= logs.length) {
        clearInterval(interval);
        setTimeout(() => setState('SIMULATION'), 800);
      } else {
        setBootLog(prev => [...prev, logs[i]]);
        i++;
      }
    }, 500);
  };

  useEffect(() => {
    if (state === 'SIMULATION') {
       let conf = 0;
       const interval = setInterval(() => {
         conf += 10; 
         setConfidence(c => (c >= 100 ? 100 : c + 10));
         if (conf >= 90) { clearInterval(interval); setState('TRANSITION'); }
       }, 300);
       return () => clearInterval(interval);
    }
  }, [state]);

  const confirmLive = () => { setState('LIVE'); setMetrics(m => ({...m, balance: 50000})); };

  return (
    <EngineContext.Provider value={{ state, bootLog, metrics, confidence, startEngine, confirmLive }}>
      {children}
    </EngineContext.Provider>
  );
};
export const useEngine = () => useContext(EngineContext);
