import { Startup } from '@/types/risk';
import { RiskBadge } from './RiskBadge';
import { TrendIndicator } from './TrendIndicator';
import { RiskScoreDisplay } from './RiskScoreDisplay';
import { MiniSparkline } from './MiniSparkline';
import { cn } from '@/lib/utils';

interface StartupRowProps {
  startup: Startup;
  rank: number;
  isSelected: boolean;
  onSelect: (startup: Startup) => void;
}

export function StartupRow({ startup, rank, isSelected, onSelect }: StartupRowProps) {
  return (
    <button
      onClick={() => onSelect(startup)}
      className={cn(
        'w-full grid grid-cols-[minmax(200px,1fr)_80px_100px_80px_100px] items-center gap-4 px-4 py-3 text-left transition-colors',
        'hover:bg-accent/50 focus:outline-none focus-visible:ring-1 focus-visible:ring-ring',
        isSelected ? 'bg-accent' : 'bg-transparent'
      )}
    >
      <div className="flex items-center gap-2 min-w-0">
        <span className="text-xs text-muted-foreground/40 w-4 flex-shrink-0">#{rank}</span>
        <div className="min-w-0">
          <p className="font-medium text-foreground truncate">{startup.name}</p>
          <p className="text-xs text-muted-foreground">{startup.sector}</p>
        </div>
      </div>

      <div className="flex justify-center">
        <RiskScoreDisplay score={startup.riskScore} severity={startup.severity} />
      </div>

      <div className="flex justify-center">
        <RiskBadge severity={startup.severity} />
      </div>

      <div className="flex justify-center">
        <TrendIndicator trend={startup.trend} delta={startup.trendDelta} />
      </div>

      <div className="flex justify-end">
        <MiniSparkline data={startup.riskHistory} severity={startup.severity} />
      </div>
    </button>
  );
}
