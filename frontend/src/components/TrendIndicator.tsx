import { TrendDirection } from '@/types/risk';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TrendIndicatorProps {
  trend: TrendDirection;
  delta: number;
  className?: string;
}

export function TrendIndicator({ trend, delta, className }: TrendIndicatorProps) {
  const config = {
    up: {
      icon: TrendingUp,
      className: 'text-risk-high',
      prefix: '+',
    },
    down: {
      icon: TrendingDown,
      className: 'text-risk-low',
      prefix: '',
    },
    stable: {
      icon: Minus,
      className: 'text-muted-foreground',
      prefix: '',
    },
  };

  const { icon: Icon, className: trendClass, prefix } = config[trend];

  return (
    <div className={cn('flex items-center gap-1 text-sm', trendClass, className)}>
      <Icon className="w-3.5 h-3.5" />
      <span className="font-medium tabular-nums">
        {delta !== 0 ? `${prefix}${delta}` : '—'}
      </span>
    </div>
  );
}
