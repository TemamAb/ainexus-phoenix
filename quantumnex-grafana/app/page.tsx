'use client';
import React, { useState, useEffect } from 'react';
export default function Home() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return <div className="p-10 text-white">Booting Engine...</div>;
  return (
    <div className="min-h-screen bg-[#111217] text-white p-8 font-mono">
      <h1 className="text-2xl font-bold text-[#5794F2] mb-4">QUANTUMNEX MISSION CONTROL</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#181b1f] p-4 border-t-2 border-[#5794F2] rounded">
          <h3 className="text-gray-400 text-xs">STATUS</h3>
          <div className="text-xl text-[#00FF9D]">SYSTEM ONLINE</div>
        </div>
        <div className="bg-[#181b1f] p-4 border-t-2 border-[#73BF69] rounded">
           <h3 className="text-gray-400 text-xs">DEPLOYMENT</h3>
           <div className="text-xl">RENDER: ACTIVE</div>
        </div>
      </div>
    </div>
  );
}
