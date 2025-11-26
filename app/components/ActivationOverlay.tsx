import React, { useEffect, useRef } from 'react';
import { useEngine } from '../engine/EngineContext';
import { Terminal } from 'lucide-react';

export const ActivationOverlay = () => {
  const { state, bootLog } = useEngine();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [bootLog]);

  if (state !== 'BOOTING') return null;

  return (
    <div className="fixed inset-0 z-50 bg-[#0b0c0f] flex items-center justify-center font-mono">
      <div className="w-[600px] bg-[#111217] border border-[#22252b] rounded-sm p-4">
        <div className="flex items-center gap-2 mb-4 border-b border-[#22252b] pb-2">
          <Terminal size={16} className="text-gray-400" />
          <span className="text-gray-400 text-xs">BOOT_SEQUENCE</span>
        </div>
        <div className="h-[300px] overflow-y-auto space-y-2 text-xs">
          {bootLog.map((log: string, i: number) => (
            <div key={i} className="text-[#00FF9D]">{`> ${log}`}</div>
          ))}
          <div ref={bottomRef} />
        </div>
        <div className="mt-2 h-1 bg-[#22252b] w-full"><div className="h-full bg-[#5794F2] transition-all" style={{width: '100%'}}></div></div>
      </div>
    </div>
  );
};
