import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extendVE';
export type Currency = 'ETH' | 'USD';

interface Metrics {
  balance: number;          // Liquid funds
  lifetimeProfit: number;   // Total generated (Withdrawal independent)
  tradesPerHour: number;
  profitPerHour: number;
  latencyMs: number;
  mevBlocked: number;       // Security Metric
  aiEfficiencyDelta: number; // % Improvement from last run
  nextAiRun: number;        // Seconds countdown
}

interface EngineContextType {
  state: EngineState;
  currency: Currency;
  refreshRate: number; // in ms
  metrics: Metrics;
  toggleCurrency: () => void;
  setRefreshRate: (ms: number) => void;
  startEngine: () => void;
  confirmLive: () => void;
  confidence: number;
}

const EngineContext = createContext<EngineContextType | null>(null);

export const EngineProvider = ({ children }: { children: React.ReactNode }) => {
  const [state, setState] = useState<EngineState>('IDLE');
  const [currency, setCurrency] = useState<Currency>('USD');
  const [refreshRate, setRefreshRate] = useState(1000); // Default 1s
  const [confidence, setConfidence] = useState(0);
  
  // METRICS STATE
  const [metrics, setMetrics] = useState<Metrics>({
    balance: 0,
    lifetimeProfit: 0,
    tradesPerHour: 0,
    profitPerHour: 0,
    latencyMs: 45,
    mevBlocked: 0,
    aiEfficiencyDelta: 0,
    nextAiRun: 900
  });

  // 1. ONE-CLICK START
  const startEngine = () => {
    setState('SIMULATION');
    // Start Confidence Build-up
    let conf = 0;
    const interval = setInterval(() => {
      conf += 5;
      setConfidence(conf);
      if (conf >= 85) {
        clearInterval(interval);
        setState('TRANSITION');
      }
    }, 500);
  };

  // 2. LIVE CONFIRMATION
  const confirmLive = () => {
    // WIPE SIM DATA FOR LIVE
    setConfidence(100);
    setMetrics(prev => ({ ...prev, balance: 50000, lifetimeProfit: 0 })); // Initial Capital
    setState('LIVE');
  };

  // 3. THE DATA STREAM (Simulates Blockchain Events)
  useEffect(() => {
    if (state === 'IDLE') return;

    const stream = setInterval(() => {
      setMetrics(prev => {
        // Different logic for Sim (Ghost) vs Live (Real)
        const isLive = state === 'LIVE';
        const profitTick = isLive ? (Math.random() * 50) : (Math.random() * 10);
        
        return {
          ...prev,
          balance: prev.balance + profitTick,
          lifetimeProfit: prev.lifetimeProfit + profitTick, // Always goes up
          tradesPerHour: isLive ? 142 : 0,
          profitPerHour: isLive ? 2450 : 0,
          latencyMs: 20 + Math.random() * 30,
          mevBlocked: prev.mevBlocked + (Math.random() > 0.9 ? 1 : 0),
          nextAiRun: prev.nextAiRun > 0 ? prev.nextAiRun - (refreshRate/1000) : 900,
          aiEfficiencyDelta: prev.nextAiRun <= 0 ? (prev.aiEfficiencyDelta + 0.1) : prev.aiEfficiencyDelta
        };
      });
    }, refreshRate);

    return () => clearInterval(stream);
  }, [state, refreshRate]);

  return (
    <EngineContext.Provider value={{
      state, currency, refreshRate, metrics, confidence,
      toggleCurrency: () => setCurrency(c => c === 'USD' ? 'ETH' : 'USD'),
      setRefreshRate, startEngine, confirmLive
    }}>
      {children}
    </EngineContext.Provider>
  );
};

export const useEngine = () => {
  const context = useContext(EngineContext);
  if (!context) throw new Error("useEngine must be used within EngineProvider");
  return context;
};
