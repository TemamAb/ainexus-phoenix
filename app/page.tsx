'use client';
import React, { useState } from 'react';
import { EngineProvider, useEngine } from './engine/EngineContext';
import { ActivationOverlay } from './components/ActivationOverlay';
import { Zap, Shield, Activity, Cpu, Link, CheckCircle, AlertCircle } from 'lucide-react';
import { GrafanaCard } from './components/GrafanaCard';

const DashboardContent = () => {
  const { state, metrics, confidence, startEngine, deployGenesis, manualLink, confirmLive, engineAddress } = useEngine();
  
  // Local state for Manual Input
  const [manualInput, setManualInput] = useState("");
  const [isValid, setIsValid] = useState(false);

  const handleManualChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setManualInput(val);
    // Basic Regex for ETH Address (0x + 40 hex chars)
    setIsValid(/^0x[a-fA-F0-9]{40}$/.test(val));
  };

  if (state === 'BOOTING') return <ActivationOverlay />;

  // THE DUAL-MODE SCREEN
  if (state === 'GENESIS') {
    return (
      <div className="h-screen bg-[#111217] flex items-center justify-center font-mono p-4">
        <div className="bg-[#181b1f] border border-[#5794F2] p-8 w-[600px] shadow-[0_0_50px_rgba(87,148,242,0.1)] relative overflow-hidden">
          
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-white mb-2">CONFIGURATION REQUIRED</h2>
            <p className="text-gray-400 text-xs">Select Engine Acquisition Protocol</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            
            {/* OPTION A: AUTO */}
            <div className="border border-[#22252b] p-4 hover:border-[#5794F2] transition-colors cursor-pointer group" onClick={deployGenesis}>
              <Cpu className="text-[#5794F2] mb-2 group-hover:scale-110 transition-transform" />
              <h3 className="text-white font-bold text-sm">AUTO-DEPLOY</h3>
              <p className="text-gray-500 text-[10px] mt-2">Deploy new Factory Clone.</p>
              <div className="mt-4 bg-[#5794F2] text-black text-center py-2 font-bold text-xs hover:bg-white transition-colors">INITIATE</div>
            </div>

            {/* OPTION B: MANUAL */}
            <div className="border border-[#22252b] p-4">
              <Link className="text-[#00FF9D] mb-2" />
              <h3 className="text-white font-bold text-sm">MANUAL LINK</h3>
              <p className="text-gray-500 text-[10px] mt-2">Connect existing contract.</p>
              
              <div className="mt-4 relative">
                <input 
                  type="text" 
                  placeholder="0x..." 
                  className={`w-full bg-black border ${isValid ? 'border-[#00FF9D]' : 'border-[#22252b]'} text-xs p-2 text-white focus:outline-none`}
                  value={manualInput}
                  onChange={handleManualChange}
                />
                {isValid && <CheckCircle className="absolute right-2 top-2 text-[#00FF9D]" size={14} />}
              </div>

              {isValid ? (
                <button onClick={() => manualLink(manualInput)} className="w-full mt-2 bg-[#00FF9D] text-black text-xs py-2 font-bold hover:bg-white">
                  LINK: {manualInput.slice(0,6)}...{manualInput.slice(-4)}
                </button>
              ) : (
                <div className="w-full mt-2 bg-[#22252b] text-gray-500 text-xs py-2 text-center cursor-not-allowed">
                  ENTER VALID ADDR
                </div>
              )}
            </div>

          </div>
        </div>
      </div>
    );
  }

  if (state === 'IDLE') {
    return (
      <div className="h-screen bg-[#111217] flex items-center justify-center">
        <button onClick={startEngine} className="group w-64 h-64 bg-[#181b1f] rounded-full border-4 border-[#22252b] hover:border-[#5794F2] transition-all flex flex-col items-center justify-center shadow-[0_0_50px_rgba(0,0,0,0.5)] hover:shadow-[0_0_80px_rgba(87,148,242,0.2)]">
          <Zap className="text-gray-500 group-hover:text-[#5794F2] mb-4 transition-colors" size={48} />
          <span className="text-white font-mono font-bold text-xl tracking-widest group-hover:text-blue-100">INITIATE</span>
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#111217] text-gray-200 font-mono p-4">
      <header className="flex justify-between items-center mb-6 border-b border-[#22252b] pb-4">
        <div className="flex items-center gap-2">
           <Activity className={state === 'LIVE' ? "text-[#00FF9D] animate-pulse" : "text-gray-500"} />
           <h1 className="font-bold text-xl">QUANTUMNEX</h1>
        </div>
        <div className="flex gap-4 text-xs">
           <div className="bg-[#181b1f] px-3 py-1 rounded border border-[#22252b] text-gray-400">
             TARGET: <span className="text-[#5794F2]">{engineAddress ? `${engineAddress.slice(0,6)}...${engineAddress.slice(-4)}` : '---'}</span>
           </div>
           <div className={`px-2 py-1 rounded ${state === 'LIVE' ? 'text-[#00FF9D]' : 'text-gray-500'}`}>
             STATUS: {state}
           </div>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <GrafanaCard title="Live Balance" accent="blue">
           <div className="text-2xl text-white font-bold">{metrics.balance.toFixed(4)} ETH</div>
        </GrafanaCard>
        <GrafanaCard title="Latency" accent="amber">
           <div className="text-2xl text-white">{metrics.latencyMs.toFixed(0)} <span className="text-xs text-gray-500">ms</span></div>
        </GrafanaCard>
        <GrafanaCard title="Optimization" accent="neon">
           <div className="text-2xl text-white">+{metrics.aiEfficiencyDelta.toFixed(1)}%</div>
        </GrafanaCard>
        <GrafanaCard title="Threats" accent="red">
           <div className="text-xl flex items-center gap-2">
             <Shield className="text-[#F2495C]" size={20}/> {metrics.mevBlocked}
           </div>
        </GrafanaCard>
      </div>

      {state === 'TRANSITION' && (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50">
          <div className="bg-[#181b1f] border border-[#00FF9D] p-8 w-[500px] text-center">
            <h2 className="text-2xl font-bold text-white mb-2">SIMULATION COMPLETE</h2>
            <div className="text-[#00FF9D] text-6xl font-bold mb-8">{confidence}%</div>
            <button onClick={confirmLive} className="w-full py-4 bg-[#00FF9D] text-black font-bold text-xl hover:bg-white">ACTIVATE LIVE TRADING</button>
          </div>
        </div>
      )}
    </div>
  );
};
export default function Home() { return <EngineProvider><DashboardContent /></EngineProvider>; }
