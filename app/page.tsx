'use client';
import { EngineProvider, useEngine } from './engine/EngineContext';
import { ActivationOverlay } from './components/ActivationOverlay';
import { Zap, Shield, Activity } from 'lucide-react';

// Inline Card Component to prevent import errors
const Card = ({ title, value, accent }: any) => {
  const colors: any = { blue: 'border-blue-500', green: 'border-green-500', red: 'border-red-500', neon: 'border-[#00FF9D]' };
  return (
    <div className={`bg-[#181b1f] border border-[#22252b] p-4 border-t-2 ${colors[accent]}`}>
      <h3 className="text-gray-500 text-xs font-bold mb-1">{title}</h3>
      <div className="text-white text-2xl font-bold">{value}</div>
    </div>
  );
};

const DashboardContent = () => {
  const { state, metrics, confidence, startEngine, confirmLive } = useEngine();

  if (state === 'BOOTING') return <ActivationOverlay />;

  if (state === 'IDLE') {
    return (
      <div className="h-screen flex items-center justify-center">
        <button onClick={startEngine} className="bg-[#181b1f] border-2 border-[#22252b] hover:border-[#5794F2] w-64 h-64 rounded-full flex flex-col items-center justify-center">
          <Zap className="text-gray-500 mb-4" size={48} />
          <span className="text-white font-mono text-xl">INITIATE</span>
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 font-mono">
      <header className="flex justify-between items-center mb-8 border-b border-[#22252b] pb-4">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <Activity className={state === 'LIVE' ? "text-[#00FF9D]" : "text-gray-500"} />
          QUANTUMNEX
        </h1>
        <div className="text-xs bg-[#22252b] px-2 py-1 rounded text-gray-300">STATUS: {state}</div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <Card title="BALANCE" value={`$${metrics.balance.toFixed(2)}`} accent="blue" />
        <Card title="LATENCY" value={`${metrics.latencyMs.toFixed(0)} ms`} accent="green" />
        <Card title="AI EFFICIENCY" value={`+${metrics.aiEfficiencyDelta.toFixed(1)}%`} accent="neon" />
        <Card title="THREATS BLOCKED" value={metrics.mevBlocked} accent="red" />
      </div>

      {state === 'TRANSITION' && (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50">
          <div className="bg-[#181b1f] border border-[#00FF9D] p-8 text-center">
            <h2 className="text-white text-2xl mb-2">SIMULATION COMPLETE</h2>
            <div className="text-[#00FF9D] text-6xl font-bold mb-6">{confidence}%</div>
            <button onClick={confirmLive} className="bg-[#00FF9D] text-black w-full py-4 font-bold">DEPLOY LIVE</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default function Home() { return <EngineProvider><DashboardContent /></EngineProvider>; }
