import React from 'react';
import { clsx } from 'clsx';

export const GrafanaCard = ({ title, children, className, accent = 'blue' }: any) => {
  const borderColors = {
    blue: 'border-t-grafana-blue',
    green: 'border-t-grafana-green',
    red: 'border-t-grafana-red',
    amber: 'border-t-grafana-amber',
    neon: 'border-t-grafana-neon'
  };

  return (
    <div className={clsx(
      "bg-grafana-panel border border-grafana-border rounded-sm p-4 relative overflow-hidden",
      "border-t-2", 
      borderColors[accent as keyof typeof borderColors] || 'border-t-gray-500',
      className
    )}>
      <h3 className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-2 flex justify-between">
        {title}
      </h3>
      {children}
    </div>
  );
};
