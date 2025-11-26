'use client';

import { EngineProvider, useEngine } from './engine/EngineContext';
import { Header } from './components/layout/Header';
import { GrafanaCard } from './components/GrafanaCard';
import { Shield, Zap } from 'lucide-react';

const DashboardContent = () => {
  const { state, metrics, currency, startEngine, confirmLive, confidence } = useEngine();

  const fmt = (val: number) => {
    if (currency === 'ETH') return `Ξ ${(val / 3500).toFixed(4)}`;
    return `$ ${val.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  };

  if (state === 'IDLE') {
    return (
      <div className="h-screen bg-grafana-bg flex items-center justify-center">
        <button 
          onClick={startEngine}
          className="group relative w-64 h-64 bg-grafana-panel rounded-full border-4 border-grafana-border flex flex-col items-center justify-center hover:border-grafana-blue transition-all"
        >
          <Zap className="text-gray-500 group-hover:text-grafana-blue mb-4" size={48} />
          <span className="text-white font-mono font-bold text-xl tracking-widest">INITIATE</span>
          <span className="text-gray-500 text-xs mt-2">ONE-CLICK SEQUENCE</span>
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-grafana-bg text-gray-200 font-mono">
      <Header />
      <main className="p-4 space-y-4">
        <div className="grid grid-cols-4 gap-4">
          <GrafanaCard title="Real-Time Balance" accent="blue">
            <div className="text-2xl text-white font-bold">{fmt(metrics.balance)}</div>
            <div className="text-xs text-grafana-blue mt-1">+0.4% this hour</div>
          </GrafanaCard>
          <GrafanaCard title="Lifetime Profit (Alpha)" accent="green">
            <div className="text-2xl text-grafana-green font-bold">{fmt(metrics.lifetimeProfit)}</div>
            <div className="text-xs text-gray-500 mt-1">Net Generated Value</div>
          </GrafanaCard>
          <GrafanaCard title="Execution Velocity" accent="amber">
            <div className="text-2xl text-white">{metrics.tradesPerHour} <span className="text-xs text-gray-500">TPS</span></div>
            <div className="text-xs text-gray-500">{metrics.latencyMs.toFixed(0)} ms Latency</div>
          </GrafanaCard>
          <GrafanaCard title="AI Intelligence" accent="neon">
            <div className="text-2xl text-white">+{metrics.aiEfficiencyDelta.toFixed(1)}%</div>
            <div className="text-xs text-gray-500">Next Opt: {Math.floor(metrics.nextAiRun)}s</div>
          </GrafanaCard>
        </div>

        <div className="grid grid-cols-12 gap-4 h-[400px]">
          <div className="col-span-4 h-full">
             <GrafanaCard title="Security Shield" accent="red" className="h-full">
                <div className="flex items-center gap-4 mb-6">
                  <Shield size={32} className="text-grafana-red" />
                  <div>
                    <div className="text-2xl text-white">{metrics.mevBlocked}</div>
                    <div className="text-xs text-gray-400">MEV Attacks Blocked</div>
                  </div>
                </div>
             </GrafanaCard>
          </div>
          <div className="col-span-8 h-full">
            <GrafanaCard title="Live Strategy Matrix" accent="blue" className="h-full">
              <div className="p-4 bg-black/40 h-full font-mono text-[10px] space-y-2">
                 <div className="text-grafana-green">>> [EXEC] Arbitrage Opportunity Found (Uniswap -> Sushi)</div>
                 <div className="text-gray-500">>> [CALC] Gas Est: 140,000 | Profit: 0.4 ETH</div>
                 <div className="text-grafana-blue">>> [AI] Strategy Optimized: Spatial Arbitrage</div>
              </div>
            </GrafanaCard>
          </div>
        </div>

        {state === 'TRANSITION' && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
            <div className="bg-grafana-panel border border-grafana-green p-8 w-[500px] text-center">
              <h2 className="text-2xl font-bold text-white mb-2">SIMULATION COMPLETE</h2>
              <div className="text-grafana-green text-4xl font-bold mb-4">{confidence}% CONFIDENCE</div>
              <button onClick={confirmLive} className="w-full py-4 bg-grafana-green text-black font-bold text-xl hover:bg-green-400">DEPLOY TO LIVE</button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default function Home() {
  return (
    <EngineProvider>
      <DashboardContent />
    </EngineProvider>
  );
}
