import React from 'react';
export const GrafanaCard = ({ title, children, accent = 'blue' }: any) => {
  const colors: any = { blue: 'border-blue-500', green: 'border-green-500', red: 'border-red-500', neon: 'border-[#00FF9D]' };
  return (
    <div className={`bg-[#181b1f] border border-[#22252b] rounded-sm p-4 border-t-2 ${colors[accent]}`}>
      <h3 className="text-gray-400 text-xs font-bold uppercase mb-2">{title}</h3>
      {children}
    </div>
  );
};
