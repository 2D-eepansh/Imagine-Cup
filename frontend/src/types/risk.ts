export type RiskSeverity = 'high' | 'medium' | 'low';
export type TrendDirection = 'up' | 'down' | 'stable';

export interface RiskDriver {
  label: string;
  detail: string;
}

export interface AIInsight {
  whyItMatters: string;
  whatHappensNext: string;
  recommendedAction: string;
}

export interface Startup {
  id: string;
  name: string;
  sector: string;
  riskScore: number;
  severity: RiskSeverity;
  trend: TrendDirection;
  trendDelta: number;
  riskHistory: number[];
  riskDrivers: RiskDriver[];
  aiInsight: AIInsight;
  requiresPartnerAttention: boolean;
}
