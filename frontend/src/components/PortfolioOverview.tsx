import { Startup } from '@/types/risk';
import { StartupRow } from './StartupRow';

interface PortfolioOverviewProps {
  startups: Startup[];
  selectedStartup: Startup | null;
  onSelectStartup: (startup: Startup) => void;
}

export function PortfolioOverview({ startups, selectedStartup, onSelectStartup }: PortfolioOverviewProps) {
  // Sort by risk score descending (highest risk first)
  const sortedStartups = [...startups].sort((a, b) => b.riskScore - a.riskScore);

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="flex-1 overflow-auto">
        <div className="inline-block min-w-full">
          {/* Header */}
          <div className="sticky top-0 z-10 grid grid-cols-[minmax(200px,1fr)_80px_100px_80px_100px] items-center gap-4 px-4 py-2 border-b border-border bg-background">
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Company</span>
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider text-center">Score</span>
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider text-center">Severity</span>
            <span className="text-xs font-medium text-muted-foreground/50 uppercase tracking-wider text-center">7d</span>
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider text-right">Trend</span>
          </div>

          {/* Rows */}
          <div className="divide-y divide-border">
            {sortedStartups.map((startup, index) => (
              <StartupRow
                key={startup.id}
                startup={startup}
                rank={index + 1}
                isSelected={selectedStartup?.id === startup.id}
                onSelect={onSelectStartup}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
