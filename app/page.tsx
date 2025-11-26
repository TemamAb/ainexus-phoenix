'use client';
import { EngineProvider, useEngine } from './engine/EngineContext';
import { GrafanaCard } from './components/GrafanaCard';
import { Shield, Zap, Activity } from 'lucide-react';

const DashboardContent = () => {
  const { state, metrics, confidence, startEngine, confirmLive } = useEngine();

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
           <h1 className="font-bold text-xl">QUANTUMNEX <span className="text-[#5794F2] text-xs">PRO</span></h1>
        </div>
        <div className={`px-2 py-1 text-xs rounded ${state === 'LIVE' ? 'bg-[#00FF9D]/20 text-[#00FF9D]' : 'bg-white/10 text-white'}`}>
          STATUS: {state}
        </div>
      </header>

      {/* METRICS ROW */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <GrafanaCard title="Balance" accent="blue">
           <div className="text-2xl text-white font-bold">${metrics.balance.toFixed(2)}</div>
        </GrafanaCard>
        <GrafanaCard title="Execution Speed" accent="amber">
           <div className="text-2xl text-white">{metrics.latencyMs.toFixed(0)} <span className="text-xs text-gray-500">ms</span></div>
        </GrafanaCard>
        <GrafanaCard title="AI Learning" accent="neon">
           <div className="text-2xl text-white">+{metrics.aiEfficiencyDelta.toFixed(1)}%</div>
        </GrafanaCard>
        <GrafanaCard title="Security" accent="red">
           <div className="flex items-center gap-2">
             <Shield className="text-[#F2495C]" size={20}/>
             <span className="text-xl">{metrics.mevBlocked} <span className="text-xs text-gray-500">Attacks</span></span>
           </div>
        </GrafanaCard>
      </div>

      {/* TRANSITION MODAL */}
      {state === 'TRANSITION' && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
          <div className="bg-[#181b1f] border border-[#00FF9D] p-8 w-[400px] text-center">
            <h2 className="text-2xl font-bold text-white mb-2">SIMULATION COMPLETE</h2>
            <div className="text-[#00FF9D] text-4xl font-bold mb-4">{confidence}%</div>
            <button onClick={confirmLive} className="w-full py-4 bg-[#00FF9D] text-black font-bold text-xl hover:opacity-80">DEPLOY LIVE</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default function Home() { return <EngineProvider><DashboardContent /></EngineProvider>; }
