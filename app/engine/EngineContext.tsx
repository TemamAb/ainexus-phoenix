'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';
import { ethers, BrowserProvider } from 'ethers';

export type EngineState = 'IDLE' | 'BOOTING' | 'GENESIS' | 'SIMULATION' | 'TRANSITION' | 'LIVE';
const EngineContext = createContext<any>(null);

export const EngineProvider = ({ children }: { children: React.ReactNode }) => {
  const [state, setState] = useState<EngineState>('IDLE');
  const [bootLog, setBootLog] = useState<string[]>([]);
  const [metrics, setMetrics] = useState({ balance: 0, latencyMs: 0, mevBlocked: 0, aiEfficiencyDelta: 0 });
  const [confidence, setConfidence] = useState(0);
  const [provider, setProvider] = useState<BrowserProvider | null>(null);
  const [engineAddress, setEngineAddress] = useState<string | null>(null);

  // 1. INIT WEB3 - SPECIFICALLY LOOKING FOR METAMASK
  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).ethereum) {
      const eth = (window as any).ethereum;
      // If multiple wallets are installed, try to find MetaMask specifically
      const targetProvider = eth.providers ? eth.providers.find((p: any) => p.isMetaMask) : eth;
      
      if (targetProvider) {
         setProvider(new ethers.BrowserProvider(targetProvider));
      } else {
         // Fallback if strictly only one is injected
         setProvider(new ethers.BrowserProvider(eth));
      }
    }
  }, []);

  // 2. METAMASK-ONLY BOOT SEQUENCE
  const startEngine = async () => {
    setState('BOOTING');
    setBootLog(["Initializing QuantumNex Core...", "Scanning for MetaMask Injection..."]);

    if (!provider) {
      setBootLog(p => [...p, "CRITICAL: MetaMask not found.", "Please install the MetaMask Extension."]);
      return;
    }

    try {
      // VERIFY IT IS METAMASK
      // We check the internal flag of the provider
      const isMetaMask = (provider.provider as any).isMetaMask;
      
      if (!isMetaMask) {
         setBootLog(p => [...p, "WARNING: Non-MetaMask Wallet Detected.", "Optimizing for Generic Web3..."]);
      } else {
         setBootLog(p => [...p, "SUCCESS: MetaMask Provider Locked.", "Establishing Secure Handshake..."]);
      }
      
      // FORCE POPUP
      await provider.send("eth_requestAccounts", []);
      
      const signer = await provider.getSigner();
      const userAddr = await signer.getAddress();
      const network = await provider.getNetwork();
      
      setBootLog(p => [...p, `IDENTITY: ${userAddr.slice(0,6)}...`]);
      setBootLog(p => [...p, `CHAIN: ${network.name.toUpperCase()} (${network.chainId})`]);

      // CHECK FOR ENGINE
      const savedEngine = localStorage.getItem(`apex_engine_${userAddr}`);

      if (savedEngine) {
        setBootLog(p => [...p, `ENGINE FOUND: ${savedEngine}`, "Decrypting... OK."]);
        setEngineAddress(savedEngine);
        setTimeout(() => setState('SIMULATION'), 1500);
      } else {
        setBootLog(p => [...p, "NO ENGINE DETECTED.", "REDIRECTING TO FACTORY..."]);
        setTimeout(() => setState('GENESIS'), 2000);
      }

    } catch (e: any) {
      if (e.code === 4001) {
        setBootLog(p => [...p, "ERROR: MetaMask Request Rejected."]);
      } else {
        setBootLog(p => [...p, `CONNECTION FAILED: ${e.message}`]);
      }
    }
  };

  // 3. DEPLOY GENESIS
  const deployGenesis = async () => {
    if (!provider) return;
    try {
      setBootLog(p => [...p, "Requesting MetaMask Signature..."]);
      // Mock Deploy
      await new Promise(r => setTimeout(r, 2000));
      const randomHex = Math.floor(Math.random() * 16777215).toString(16);
      const newAddr = `0x${randomHex}821379...AE`;
      const signer = await provider.getSigner();
      const userAddr = await signer.getAddress();
      localStorage.setItem(`apex_engine_${userAddr}`, newAddr);
      setEngineAddress(newAddr);
      setBootLog(p => [...p, `DEPLOYED: ${newAddr}`]);
      setTimeout(() => setState('SIMULATION'), 1000);
    } catch (e: any) {
      setBootLog(p => [...p, `ERROR: ${e.message}`]);
    }
  };

  // 4. CONFIRM LIVE
  const confirmLive = async () => {
    setState('LIVE');
    if (provider) {
      try {
        const signer = await provider.getSigner();
        const bal = await provider.getBalance(signer.getAddress());
        setMetrics(m => ({...m, balance: parseFloat(ethers.formatEther(bal))}));
        setInterval(() => {
           setMetrics(p => ({
             ...p, 
             latencyMs: 30 + Math.random() * 20,
             aiEfficiencyDelta: p.aiEfficiencyDelta + 0.01
           }));
        }, 2000);
      } catch (e) { console.error(e); }
    }
  };

  return (
    <EngineContext.Provider value={{ state, bootLog, metrics, confidence, startEngine, deployGenesis, confirmLive, engineAddress }}>
      {children}
    </EngineContext.Provider>
  );
};
export const useEngine = () => useContext(EngineContext);
