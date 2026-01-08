import { RiskSeverity } from '@/types/risk';

interface RiskChartProps {
  data: number[];
  severity: RiskSeverity;
}

export function RiskChart({ data, severity }: RiskChartProps) {
  if (data.length < 2) return null;

  const width = 280;
  const height = 80;
  const padding = { top: 8, right: 8, bottom: 20, left: 32 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const min = Math.min(...data) - 5;
  const max = Math.max(...data) + 5;
  const range = max - min || 1;

  const points = data.map((value, index) => {
    const x = padding.left + (index / (data.length - 1)) * chartWidth;
    const y = padding.top + chartHeight - ((value - min) / range) * chartHeight;
    return { x, y, value };
  });

  const linePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');

  const areaPath = `${linePath} L ${points[points.length - 1].x} ${padding.top + chartHeight} L ${padding.left} ${padding.top + chartHeight} Z`;

  const strokeColor = {
    high: 'hsl(0 65% 55%)',
    medium: 'hsl(35 85% 55%)',
    low: 'hsl(160 45% 45%)',
  }[severity];

  const fillColor = {
    high: 'hsl(0 65% 55% / 0.1)',
    medium: 'hsl(35 85% 55% / 0.1)',
    low: 'hsl(160 45% 45% / 0.1)',
  }[severity];

  const days = ['6d', '5d', '4d', '3d', '2d', '1d', 'Now'];

  return (
    <svg width={width} height={height} className="overflow-visible">
      {/* Grid lines */}
      {[0, 0.5, 1].map((ratio, i) => {
        const y = padding.top + chartHeight * (1 - ratio);
        const value = Math.round(min + range * ratio);
        return (
          <g key={i}>
            <line
              x1={padding.left}
              y1={y}
              x2={width - padding.right}
              y2={y}
              stroke="hsl(215 20% 18%)"
              strokeDasharray="2,2"
            />
            <text
              x={padding.left - 6}
              y={y}
              textAnchor="end"
              dominantBaseline="middle"
              className="fill-muted-foreground text-[10px]"
            >
              {value}
            </text>
          </g>
        );
      })}

      {/* X-axis labels */}
      {[0, 3, 6].map((i) => (
        <text
          key={i}
          x={padding.left + (i / (data.length - 1)) * chartWidth}
          y={height - 4}
          textAnchor="middle"
          className="fill-muted-foreground text-[10px]"
        >
          {days[i]}
        </text>
      ))}

      {/* Area */}
      <path d={areaPath} fill={fillColor} />

      {/* Line */}
      <path d={linePath} fill="none" stroke={strokeColor} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />

      {/* End dot */}
      <circle cx={points[points.length - 1].x} cy={points[points.length - 1].y} r="3" fill={strokeColor} />
    </svg>
  );
}
