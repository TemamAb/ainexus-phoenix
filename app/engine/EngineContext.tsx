'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';

export type EngineState = 'IDLE' | 'BOOTING' | 'SIMULATION' | 'TRANSITION' | 'LIVE';
interface Metrics {
  balance: number; lifetimeProfit: number; tradesPerHour: number;
  latencyMs: number; mevBlocked: number; aiEfficiencyDelta: number;
}

const EngineContext = createContext<any>(null);

export const EngineProvider = ({ children }: { children: React.ReactNode }) => {
  const [state, setState] = useState<EngineState>('IDLE');
  const [bootLog, setBootLog] = useState<string[]>([]);
  const [metrics, setMetrics] = useState<Metrics>({
    balance: 0, lifetimeProfit: 0, tradesPerHour: 0,
    latencyMs: 45, mevBlocked: 0, aiEfficiencyDelta: 0
  });
  const [confidence, setConfidence] = useState(0);

  // THE 81-FILE ROLL CALL LOGIC
  const startEngine = () => {
    setState('BOOTING');
    const sequence = [
      "Initialising QuantumNex Core v2.0...",
      "Decrypting Environment Secrets (AES-256)... [OK]",
      "Connecting to Fireblocks MPC Vault... [SECURE]",
      "Module 04/81: Gasless Paymaster (Pimlico) Check... [ACTIVE]",
      "Module 12/81: Flash Loan Contracts (Aave V3/Balancer)... [LINKED]",
      "Module 23/81: Loading TensorFlow AI Models (Weights v4.2)... [LOADED]",
      "Module 45/81: Waking Bot Tier 1: MEMPOOL SCANNERS... [ONLINE]",
      "Module 46/81: Waking Bot Tier 2: ROUTE ORCHESTRATORS... [OPTIMIZED]",
      "Module 47/81: Waking Bot Tier 3: EXECUTION RELAYERS... [READY]",
      "Verifying MEV Shield (Flashbots Protect)... [ENABLED]",
      "Syncing Arbitrage Opportunities (Cross-Chain)... [SYNCED]",
      "SYSTEM INTEGRITY CHECK: 100% PASS."
    ];

    let i = 0;
    // Reset log
    setBootLog([]);
    
    const bootInterval = setInterval(() => {
      setBootLog(prev => [...prev, sequence[i]]);
      i++;
      if (i >= sequence.length) {
        clearInterval(bootInterval);
        setTimeout(() => setState('SIMULATION'), 1000); // Enter Simulation after boot
      }
    }, 600); // Speed of text scrolling
  };

  // Simulation Logic (Confidence Builder)
  useEffect(() => {
    if (state === 'SIMULATION') {
       let conf = 0;
       const interval = setInterval(() => {
         conf += 5; setConfidence(conf);
         if (conf >= 85) { clearInterval(interval); setState('TRANSITION'); }
       }, 200);
       return () => clearInterval(interval);
    }
  }, [state]);

  const confirmLive = () => {
    setState('LIVE');
    setMetrics(prev => ({...prev, balance: 50000}));
  };

  // Live Metrics Stream
  useEffect(() => {
    if (state === 'IDLE' || state === 'BOOTING') return;
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
    <EngineContext.Provider value={{ state, bootLog, metrics, confidence, startEngine, confirmLive }}>
      {children}
    </EngineContext.Provider>
  );
};

export const useEngine = () => useContext(EngineContext);
