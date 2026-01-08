import { RiskSeverity } from '@/types/risk';
import { cn } from '@/lib/utils';

interface RiskBadgeProps {
  severity: RiskSeverity;
  className?: string;
}

const severityConfig = {
  high: {
    label: 'High',
    className: 'bg-risk-high/15 text-risk-high border-risk-high/30',
  },
  medium: {
    label: 'Medium',
    className: 'bg-risk-medium/15 text-risk-medium border-risk-medium/30',
  },
  low: {
    label: 'Low',
    className: 'bg-risk-low/15 text-risk-low border-risk-low/30',
  },
};

export function RiskBadge({ severity, className }: RiskBadgeProps) {
  const config = severityConfig[severity];

  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 text-xs font-medium rounded border',
        config.className,
        className
      )}
    >
      {config.label}
    </span>
  );
}
