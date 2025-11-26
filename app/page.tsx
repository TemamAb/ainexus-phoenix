'use client';
import { EngineProvider, useEngine } from './engine/EngineContext';
import { ActivationOverlay } from './components/ActivationOverlay';
import { Zap, Shield, Activity, Box, Cpu } from 'lucide-react';
import { GrafanaCard } from './components/GrafanaCard';

const DashboardContent = () => {
  const { state, metrics, confidence, startEngine, deployGenesis, confirmLive, engineAddress } = useEngine();

  if (state === 'BOOTING') return <ActivationOverlay />;

  // THE GENESIS SCREEN (Dynamic Creation)
  if (state === 'GENESIS') {
    return (
      <div className="h-screen bg-[#111217] flex items-center justify-center font-mono">
        <div className="bg-[#181b1f] border border-[#5794F2] p-8 w-[600px] text-center shadow-[0_0_50px_rgba(87,148,242,0.2)]">
          <Cpu className="mx-auto text-[#5794F2] mb-4" size={64} />
          <h2 className="text-2xl font-bold text-white mb-2">GENESIS PROTOCOL DETECTED</h2>
          <p className="text-gray-400 text-sm mb-6">
            No Arbitrage Engine associated with this wallet.
            <br/>System must deploy a dedicated <strong>ApexFlashLoan Smart Contract</strong>.
          </p>
          <div className="bg-black/30 p-4 rounded mb-6 text-left text-xs font-mono text-gray-500">
            <p>Target: Ethereum Mainnet</p>
            <p>Type: ApexFlashLoan (Factory Clone)</p>
            <p>Gas Est: 0.04 ETH</p>
          </div>
          <button 
            onClick={deployGenesis}
            className="w-full py-4 bg-[#5794F2] text-black font-bold text-xl hover:bg-white transition-all"
          >
            DEPLOY ENGINE NOW
          </button>
        </div>
      </div>
    );
  }

  if (state === 'IDLE') {
    return (
      <div className="h-screen bg-[#111217] flex items-center justify-center">
        <button onClick={startEngine} className="group w-64 h-64 bg-[#181b1f] rounded-full border-4 border-[#22252b] hover:border-[#5794F2] transition-all flex flex-col items-center justify-center">
          <Zap className="text-gray-500 group-hover:text-[#5794F2] mb-4" size={48} />
          <span className="text-white font-mono font-bold text-xl tracking-widest">INITIATE</span>
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#111217] text-gray-200 font-mono p-4">
      {/* HEADER */}
      <header className="flex justify-between items-center mb-6 border-b border-[#22252b] pb-4">
        <div className="flex items-center gap-2">
           <Activity className={state === 'LIVE' ? "text-[#00FF9D] animate-pulse" : "text-gray-500"} />
           <h1 className="font-bold text-xl">QUANTUMNEX</h1>
        </div>
        <div className="flex gap-4 text-xs">
           <div className="bg-[#181b1f] px-3 py-1 rounded border border-[#22252b] text-gray-400">
             ENGINE: <span className="text-[#5794F2]">{engineAddress || '---'}</span>
           </div>
           <div className={`px-2 py-1 rounded ${state === 'LIVE' ? 'text-[#00FF9D]' : 'text-gray-500'}`}>
             STATUS: {state}
           </div>
        </div>
      </header>

      {/* METRICS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <GrafanaCard title="Live Balance" accent="blue">
           <div className="text-2xl text-white font-bold">${metrics.balance.toFixed(4)}</div>
        </GrafanaCard>
        <GrafanaCard title="Latency" accent="amber">
           <div className="text-2xl text-white">{metrics.latencyMs} <span className="text-xs text-gray-500">ms</span></div>
        </GrafanaCard>
        <GrafanaCard title="AI Optimizations" accent="neon">
           <div className="text-2xl text-white">+{metrics.aiEfficiencyDelta.toFixed(1)}%</div>
        </GrafanaCard>
        <GrafanaCard title="Active Threats" accent="red">
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
