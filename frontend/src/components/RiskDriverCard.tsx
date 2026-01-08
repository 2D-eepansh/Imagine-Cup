import { RiskDriver } from '@/types/risk';
import { AlertCircle } from 'lucide-react';

interface RiskDriverCardProps {
  driver: RiskDriver;
  index: number;
}

export function RiskDriverCard({ driver, index }: RiskDriverCardProps) {
  return (
    <div 
      className="flex gap-3 p-3 rounded-md bg-muted/50 animate-fade-in"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      <AlertCircle className="w-4 h-4 text-risk-medium flex-shrink-0 mt-0.5" />
      <div className="min-w-0">
        <p className="text-sm font-medium text-foreground">{driver.label}</p>
        <p className="text-xs text-muted-foreground mt-0.5">{driver.detail}</p>
      </div>
    </div>
  );
}
