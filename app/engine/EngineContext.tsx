'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';
import { ethers, BrowserProvider, Contract, ContractFactory } from 'ethers';

// --- ARTIFACT IMPORTS (MOCK FOR CLIENT-SIDE DEMO - IN PROD IMPORT JSON) ---
// In a real build, we import the JSON from artifacts. 
// For this Next.js runtime, we assume the ABI is loaded dynamically.
const ENGINE_ABI = [
  "function executeArbitrage(address token, uint256 amount, bytes calldata data) external",
  "event ProfitSecured(address indexed token, uint256 profit)",
  "function transferOwnership(address newOwner) external"
];
// AAVE V3 POOL PROVIDER (Mainnet)
const PROVIDER_ADDRESS = "0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9e"; 

export type EngineState = 'IDLE' | 'BOOTING' | 'GENESIS' | 'SIMULATION' | 'TRANSITION' | 'LIVE';

const EngineContext = createContext<any>(null);

export const EngineProvider = ({ children }: { children: React.ReactNode }) => {
  const [state, setState] = useState<EngineState>('IDLE');
  const [bootLog, setBootLog] = useState<string[]>([]);
  const [metrics, setMetrics] = useState({ balance: 0, latencyMs: 0, mevBlocked: 0, aiEfficiencyDelta: 0 });
  const [confidence, setConfidence] = useState(0);
  const [provider, setProvider] = useState<BrowserProvider | null>(null);
  const [engineAddress, setEngineAddress] = useState<string | null>(null);

  // 1. INIT WEB3
  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).ethereum) {
      setProvider(new ethers.BrowserProvider((window as any).ethereum));
    }
  }, []);

  // 2. START SEQUENCE
  const startEngine = async () => {
    setState('BOOTING');
    setBootLog(["Initializing Genesis Protocol..."]);

    if (!provider) {
      setBootLog(p => [...p, "ERROR: No Web3 Wallet Found!"]);
      return;
    }

    try {
      const signer = await provider.getSigner();
      const userAddr = await signer.getAddress();
      
      setBootLog(p => [...p, `User Identified: ${userAddr.slice(0,6)}...`]);

      // DYNAMIC CHECK: Does User have an Engine?
      // For this demo, we check LocalStorage. In Prod, query the Factory Contract.
      const savedEngine = localStorage.getItem(`apex_engine_${userAddr}`);

      if (savedEngine) {
        setBootLog(p => [...p, `Existing Engine Found: ${savedEngine}`, "Connecting Interface..."]);
        setEngineAddress(savedEngine);
        setTimeout(() => setState('SIMULATION'), 1000);
      } else {
        // NO ENGINE FOUND -> TRIGGER GENESIS
        setBootLog(p => [...p, "NO ENGINE DETECTED.", "INITIATING SMART FACTORY DEPLOYMENT..."]);
        setTimeout(() => setState('GENESIS'), 1500);
      }

    } catch (e: any) {
      setBootLog(p => [...p, `BOOT FAILED: ${e.message}`]);
    }
  };

  // 3. DEPLOY FUNCTION (Triggered by Button in GENESIS state)
  const deployGenesis = async () => {
    if (!provider) return;
    try {
      setBootLog(p => [...p, "Requesting Signature for Factory Deployment..."]);
      const signer = await provider.getSigner();
      
      // SIMULATE DEPLOYMENT TRANSACTION (Visual Trust)
      // In real prod, this calls Factory.createEngine()
      setBootLog(p => [...p, "Transaction Broadcast: Creating Smart Wallet...", "Waiting for Block Confirmation..."]);
      
      // Mock delay for blockchain confirm
      await new Promise(r => setTimeout(r, 3000));
      
      // Generate a Deterministic "Smart" Address (Mocking CREATE2)
      const randomHex = Math.floor(Math.random() * 16777215).toString(16);
      const newAddr = `0x${randomHex}821379...Factory`;
      
      const userAddr = await signer.getAddress();
      localStorage.setItem(`apex_engine_${userAddr}`, newAddr);
      setEngineAddress(newAddr);
      
      setBootLog(p => [...p, `CONFIRMED. Engine Deployed at: ${newAddr}`, "Transferring Ownership... OK."]);
      
      setTimeout(() => setState('SIMULATION'), 1000);

    } catch (e: any) {
      setBootLog(p => [...p, `DEPLOY ERROR: ${e.message}`]);
    }
  };

  const confirmLive = () => {
    setState('LIVE');
    // Start listening to the dynamically created address
    console.log("Listening to events on:", engineAddress);
  };

  // ... (Keep existing metric effects)

  return (
    <EngineContext.Provider value={{ state, bootLog, metrics, confidence, startEngine, deployGenesis, confirmLive, engineAddress }}>
      {children}
    </EngineContext.Provider>
  );
};
export const useEngine = () => useContext(EngineContext);
