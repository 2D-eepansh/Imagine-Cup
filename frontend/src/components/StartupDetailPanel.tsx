import { Startup } from '@/types/risk';
import { RiskScoreDisplay } from './RiskScoreDisplay';
import { RiskBadge } from './RiskBadge';
import { RiskChart } from './RiskChart';
import { RiskDriverCard } from './RiskDriverCard';
import { AIInsightPanel } from './AIInsightPanel';
import { AlertTriangle, Eye } from 'lucide-react';

interface StartupDetailPanelProps {
  startup: Startup;
}

export function StartupDetailPanel({ startup }: StartupDetailPanelProps) {
  return (
    <div className="h-full flex flex-col animate-slide-in">
      {/* Header */}
      <div className="p-6 border-b border-border">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h2 className="text-xl font-semibold text-foreground">{startup.name}</h2>
              {startup.requiresPartnerAttention && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded bg-risk-high/15 text-risk-high border border-risk-high/30">
                  <AlertTriangle className="w-3 h-3" />
                  Partner Attention
                </span>
              )}
              {!startup.requiresPartnerAttention && startup.severity !== 'high' && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded bg-muted text-muted-foreground border border-border">
                  <Eye className="w-3 h-3" />
                  Monitor Only
                </span>
              )}
            </div>
            <p className="text-sm text-muted-foreground">{startup.sector}</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left: Score & Chart */}
          <div className="space-y-6">
            <div>
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
                Risk Score
              </p>
              <div className="flex items-baseline gap-3">
                <RiskScoreDisplay score={startup.riskScore} severity={startup.severity} size="lg" />
                <RiskBadge severity={startup.severity} />
              </div>
              {startup.severity === 'high' && (
                <p className="mt-2 text-xs font-medium text-risk-high">
                  Intervention recommended within 7 days
                </p>
              )}
              {startup.severity === 'medium' && (
                <p className="mt-2 text-xs font-medium text-risk-medium">
                  Review recommended within 14 days
                </p>
              )}
            </div>

            <div>
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">
                7-Day Trend
              </p>
              <RiskChart data={startup.riskHistory} severity={startup.severity} />
            </div>
          </div>

          {/* Right: Risk Drivers */}
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">
              Top Risk Drivers
            </p>
            {startup.riskDrivers.length > 0 ? (
              <div className="space-y-2">
                {startup.riskDrivers.map((driver, index) => (
                  <RiskDriverCard key={index} driver={driver} index={index} />
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground italic">
                No significant risk drivers detected.
              </p>
            )}
          </div>
        </div>

        {/* AI Insight */}
        <div className="mt-8 pt-6 border-t border-border">
          <h3 className="text-sm font-semibold text-foreground mb-4">
            Risk Intelligence Analysis
          </h3>
          <AIInsightPanel insight={startup.aiInsight} />
        </div>
      </div>
    </div>
  );
}
