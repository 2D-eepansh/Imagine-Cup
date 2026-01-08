import { RiskSeverity } from '@/types/risk';
import { cn } from '@/lib/utils';

interface RiskScoreDisplayProps {
  score: number;
  severity: RiskSeverity;
  size?: 'sm' | 'lg';
  className?: string;
}

export function RiskScoreDisplay({ score, severity, size = 'sm', className }: RiskScoreDisplayProps) {
  const colorClass = {
    high: 'text-risk-high',
    medium: 'text-risk-medium',
    low: 'text-risk-low',
  }[severity];

  const sizeClass = {
    sm: 'text-lg font-semibold',
    lg: 'text-5xl font-bold tracking-tight',
  }[size];

  return (
    <span className={cn(colorClass, sizeClass, 'tabular-nums', className)}>
      {score}
    </span>
  );
}
