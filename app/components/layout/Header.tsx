'use client';
import { useEngine } from '../../engine/EngineContext';
import { Activity, RefreshCw } from 'lucide-react';

export const Header = () => {
  const { state, currency, toggleCurrency, refreshRate, setRefreshRate } = useEngine();

  return (
    <header className="h-14 bg-grafana-panel border-b border-grafana-border flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <Activity className={state === 'LIVE' ? "text-grafana-neon animate-pulse" : "text-gray-500"} size={20} />
        <h1 className="text-white font-mono font-bold tracking-tight">
          QUANTUMNEX <span className="text-grafana-blue text-xs align-top">PRO</span>
        </h1>
        <span className={`px-2 py-0.5 text-[10px] rounded font-mono ${
          state === 'LIVE' ? 'bg-grafana-green/20 text-grafana-green' : 
          state === 'SIMULATION' ? 'bg-white/20 text-white' : 'bg-gray-800 text-gray-500'
        }`}>
          {state}
        </span>
      </div>

      <div className="flex items-center gap-4 text-xs font-mono">
        <div className="flex items-center gap-2 text-gray-400">
          <RefreshCw size={12} />
          <span>POLL:</span>
          <select 
            value={refreshRate}
            onChange={(e) => setRefreshRate(Number(e.target.value))}
            className="bg-grafana-bg border border-grafana-border rounded px-1 py-0.5 text-white focus:outline-none"
          >
            <option value={1000}>1s</option>
            <option value={5000}>5s</option>
            <option value={10000}>10s</option>
          </select>
        </div>
        <button 
          onClick={toggleCurrency}
          className="flex items-center gap-2 px-3 py-1 bg-grafana-bg border border-grafana-border rounded hover:border-grafana-blue transition-colors text-white"
        >
          <span className={currency === 'ETH' ? 'text-grafana-blue' : 'text-gray-500'}>ETH</span>
          <span className="text-gray-600">|</span>
          <span className={currency === 'USD' ? 'text-grafana-green' : 'text-gray-500'}>USD</span>
        </button>
      </div>
    </header>
  );
};
