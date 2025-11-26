'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';
import { ethers, BrowserProvider, isAddress } from 'ethers';

export type EngineState = 'IDLE' | 'BOOTING' | 'GENESIS' | 'SIMULATION' | 'TRANSITION' | 'LIVE';
const EngineContext = createContext<any>(null);

export const EngineProvider = ({ children }: { children: React.ReactNode }) => {
  const [state, setState] = useState<EngineState>('IDLE');
  const [bootLog, setBootLog] = useState<string[]>([]);
  const [metrics, setMetrics] = useState({ balance: 0, latencyMs: 0, mevBlocked: 0, aiEfficiencyDelta: 0 });
  const [confidence, setConfidence] = useState(0);
  const [provider, setProvider] = useState<BrowserProvider | null>(null);
  const [engineAddress, setEngineAddress] = useState<string | null>(null);

  // INIT
  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).ethereum) {
      const eth = (window as any).ethereum;
      const targetProvider = eth.providers ? eth.providers.find((p: any) => p.isMetaMask) : eth;
      setProvider(new ethers.BrowserProvider(targetProvider || eth));
    }
  }, []);

  // START SEQUENCE
  const startEngine = async () => {
    setState('BOOTING');
    setBootLog(["Initializing Core...", "Scanning for MetaMask..."]);

    if (!provider) {
      setBootLog(p => [...p, "CRITICAL: MetaMask not found."]);
      return;
    }

    try {
      await provider.send("eth_requestAccounts", []);
      const signer = await provider.getSigner();
      const userAddr = await signer.getAddress();
      
      setBootLog(p => [...p, `IDENTITY: ${userAddr.slice(0,6)}...`, "Checking Registry..."]);

      const savedEngine = localStorage.getItem(`apex_engine_${userAddr}`);

      if (savedEngine) {
        setBootLog(p => [...p, `ENGINE FOUND: ${savedEngine}`, "Linking..."]);
        setEngineAddress(savedEngine);
        setTimeout(() => setState('SIMULATION'), 1500);
      } else {
        setBootLog(p => [...p, "NO ASSOCIATED ENGINE.", "OPENING CONFIGURATION PROTOCOL..."]);
        setTimeout(() => setState('GENESIS'), 2000);
      }
    } catch (e: any) {
      setBootLog(p => [...p, `ERROR: ${e.message}`]);
    }
  };

  // AUTO DEPLOY
  const deployGenesis = async () => {
    if (!provider) return;
    try {
      setBootLog(p => [...p, "Auto-Deploying Factory Clone..."]);
      await new Promise(r => setTimeout(r, 2000)); // Mock tx
      const randomHex = Math.floor(Math.random() * 16777215).toString(16);
      const newAddr = `0x${randomHex}821379...AE`;
      linkEngine(newAddr);
    } catch (e: any) { console.error(e); }
  };

  // MANUAL LINK
  const manualLink = (address: string) => {
    if (!isAddress(address)) {
      alert("Invalid Ethereum Address Format");
      return;
    }
    setBootLog(p => [...p, `MANUAL OVERRIDE: Linking to ${address}...`]);
    linkEngine(address);
  };

  const linkEngine = async (addr: string) => {
    if (!provider) return;
    const signer = await provider.getSigner();
    const userAddr = await signer.getAddress();
    localStorage.setItem(`apex_engine_${userAddr}`, addr);
    setEngineAddress(addr);
    setTimeout(() => setState('SIMULATION'), 1000);
  };

  const confirmLive = () => {
    setState('LIVE');
    if (provider) {
      provider.getSigner().then(s => provider.getBalance(s.getAddress()))
        .then(b => setMetrics(m => ({...m, balance: parseFloat(ethers.formatEther(b)) })));
      
      setInterval(() => {
         setMetrics(p => ({
           ...p, latencyMs: 30 + Math.random() * 20, aiEfficiencyDelta: p.aiEfficiencyDelta + 0.01
         }));
      }, 2000);
    }
  };

  return (
    <EngineContext.Provider value={{ state, bootLog, metrics, confidence, startEngine, deployGenesis, manualLink, confirmLive, engineAddress }}>
      {children}
    </EngineContext.Provider>
  );
};
export const useEngine = () => useContext(EngineContext);
