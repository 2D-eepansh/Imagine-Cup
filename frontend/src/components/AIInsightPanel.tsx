import { AIInsight } from '@/types/risk';

interface AIInsightPanelProps {
  insight: AIInsight;
}

export function AIInsightPanel({ insight }: AIInsightPanelProps) {
  return (
    <div className="space-y-4 animate-fade-in">
      <div>
        <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
          Why This Matters
        </h4>
        <p className="text-sm text-foreground leading-relaxed">
          {insight.whyItMatters}
        </p>
      </div>

      <div>
        <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
          What Typically Happens Next
        </h4>
        <p className="text-sm text-foreground leading-relaxed">
          {insight.whatHappensNext}
        </p>
      </div>

      <div className="p-3 rounded-md bg-primary/10 border border-primary/20">
        <h4 className="text-xs font-medium text-primary uppercase tracking-wider mb-2">
          Recommended Action
        </h4>
        <p className="text-sm text-foreground leading-relaxed">
          {insight.recommendedAction}
        </p>
      </div>

      <p className="text-[10px] text-muted-foreground/60 pt-2">
        Risk detected using Azure Machine Learning · Insight generated via Azure OpenAI
      </p>
    </div>
  );
}
