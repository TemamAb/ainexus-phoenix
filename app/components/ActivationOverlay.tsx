import React, { useEffect, useRef } from 'react';
import { useEngine } from '../engine/EngineContext';
import { Terminal } from 'lucide-react';

export const ActivationOverlay = () => {
  const { state, bootLog } = useEngine();
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of logs
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [bootLog]);

  if (state !== 'BOOTING') return null;

  return (
    <div className="fixed inset-0 z-50 bg-[#0b0c0f] flex items-center justify-center font-mono">
      <div className="w-[600px] bg-[#111217] border border-[#22252b] rounded-sm shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-[#181b1f] px-4 py-2 border-b border-[#22252b] flex items-center justify-between">
          <div className="flex items-center gap-2 text-gray-400">
            <Terminal size={14} />
            <span className="text-xs font-bold tracking-widest">SYSTEM_BOOT_SEQUENCE.exe</span>
          </div>
          <span className="text-[#5794F2] text-xs animate-pulse">INITIALIZING...</span>
        </div>

        {/* Log Console */}
        <div className="h-[300px] p-6 overflow-y-auto space-y-2 text-xs">
          {bootLog.map((log: string, i: number) => (
            <div key={i} className="flex gap-3">
              <span className="text-gray-600">[{new Date().toLocaleTimeString()}]</span>
              <span className={
                log.includes("ERROR") ? "text-red-500" :
                log.includes("OK") || log.includes("ACTIVE") || log.includes("SECURE") || log.includes("READY") || log.includes("SYNCED") || log.includes("PASS") ? "text-[#00FF9D]" :
                log.includes("Waking") || log.includes("Loading") ? "text-[#5794F2]" :
                "text-gray-300"
              }>
                {log}
              </span>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Footer Progress */}
        <div className="p-2 bg-[#181b1f] border-t border-[#22252b]">
           <div className="w-full bg-[#22252b] h-1 rounded-full overflow-hidden">
             <div 
               className="bg-[#5794F2] h-full transition-all duration-300"
               style={{ width: `${(bootLog.length / 12) * 100}%` }}
             />
           </div>
           <div className="flex justify-between mt-1 text-[10px] text-gray-500">
             <span>VERIFYING MODULES</span>
             <span>{(bootLog.length / 12 * 100).toFixed(0)}%</span>
           </div>
        </div>
      </div>
    </div>
  );
};
