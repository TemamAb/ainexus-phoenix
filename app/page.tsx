'use client';
import { EngineProvider, useEngine } from './engine/EngineContext';
import { GrafanaCard } from './components/GrafanaCard';
import { ActivationOverlay } from './components/ActivationOverlay';
import { Shield, Zap, Activity } from 'lucide-react';

const DashboardContent = () => {
  const { state, metrics, confidence, startEngine, confirmLive } = useEngine();

  // SHOW BOOT OVERLAY IF BOOTING
  if (state === 'BOOTING') {
    return <ActivationOverlay />;
  }

  if (state === 'IDLE') {
    return (
      <div className="h-screen bg-[#111217] flex items-center justify-center">
        <button onClick={startEngine} className="group w-64 h-64 bg-[#181b1f] rounded-full border-4 border-[#22252b] hover:border-[#5794F2] transition-all flex flex-col items-center justify-center shadow-[0_0_50px_rgba(0,0,0,0.5)] hover:shadow-[0_0_80px_rgba(87,148,242,0.2)]">
          <Zap className="text-gray-500 group-hover:text-[#5794F2] mb-4 transition-colors" size={48} />
          <span className="text-white font-mono font-bold text-xl tracking-widest group-hover:text-blue-100">INITIATE</span>
          <span className="text-gray-600 text-xs mt-2 font-mono group-hover:text-blue-200">START ENGINE</span>
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#111217] text-gray-200 font-mono p-4">
      <header className="flex justify-between items-center mb-6 border-b border-[#22252b] pb-4">
        <div className="flex items-center gap-2">
           <Activity className={state === 'LIVE' ? "text-[#00FF9D] animate-pulse" : "text-gray-500"} />
           <h1 className="font-bold text-xl">QUANTUMNEX <span className="text-[#5794F2] text-xs">PRO</span></h1>
        </div>
        <div className={`px-2 py-1 text-xs rounded border ${state === 'LIVE' ? 'bg-[#00FF9D]/10 text-[#00FF9D] border-[#00FF9D]/30' : 'bg-white/5 text-white border-white/10'}`}>
          STATUS: {state}
        </div>
      </header>

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

      {state === 'TRANSITION' && (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 backdrop-blur-sm">
          <div className="bg-[#181b1f] border border-[#00FF9D] p-8 w-[500px] text-center shadow-[0_0_100px_rgba(0,255,157,0.1)]">
            <h2 className="text-2xl font-bold text-white mb-2 tracking-tight">SIMULATION COMPLETE</h2>
            <p className="text-gray-400 text-xs mb-6">Strategy Confidence Threshold Met. Ready for Capital Deployment.</p>
            <div className="text-[#00FF9D] text-6xl font-bold mb-8 tracking-tighter">{confidence}%</div>
            <button onClick={confirmLive} className="w-full py-4 bg-[#00FF9D] text-black font-bold text-xl hover:bg-[#5affbd] transition-colors tracking-widest">DEPLOY LIVE</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default function Home() { return <EngineProvider><DashboardContent /></EngineProvider>; }
