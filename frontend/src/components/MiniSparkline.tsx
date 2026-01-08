import { RiskSeverity } from '@/types/risk';

interface MiniSparklineProps {
  data: number[];
  severity: RiskSeverity;
  width?: number;
  height?: number;
}

export function MiniSparkline({ data, severity, width = 64, height = 24 }: MiniSparklineProps) {
  if (data.length < 2) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const points = data
    .map((value, index) => {
      const x = (index / (data.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      return `${x},${y}`;
    })
    .join(' ');

  const strokeColor = {
    high: 'hsl(0 65% 55%)',
    medium: 'hsl(35 85% 55%)',
    low: 'hsl(160 45% 45%)',
  }[severity];

  return (
    <svg width={width} height={height} className="overflow-visible">
      <polyline
        points={points}
        fill="none"
        stroke={strokeColor}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
