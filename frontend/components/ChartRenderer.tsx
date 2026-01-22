'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { PlotlyJson } from '@/lib/api';

// Dynamic import to avoid SSR issues with Plotly
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface ChartRendererProps {
  data: PlotlyJson;
  title?: string;
}

export default function ChartRenderer({ data, title }: ChartRendererProps) {
  return (
    <div className="w-full h-[400px] border border-border rounded-lg bg-card/50 p-4">
      {title && (
        <h3 className="text-sm font-medium text-muted-foreground mb-4 text-center">
          {title}
        </h3>
      )}
      <div className="w-full h-full">
        <Plot
          data={data.data}
          layout={{
            ...data.layout,
            autosize: true,
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {
              color: '#ededed'
            },
            margin: { t: 30, r: 20, l: 40, b: 40 },
          }}
          useResizeHandler={true}
          style={{ width: '100%', height: '100%' }}
          config={{ responsive: true, displayModeBar: false }}
        />
      </div>
    </div>
  );
}
