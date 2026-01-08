import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchStartups, fetchStartup } from '@/services/api';
import { Startup } from '@/types/risk';
import { Header } from '@/components/Header';
import { PortfolioOverview } from '@/components/PortfolioOverview';
import { StartupDetailPanel } from '@/components/StartupDetailPanel';

const Index = () => {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data: startups = [], isLoading, isError } = useQuery({
    queryKey: ['startups'],
    queryFn: fetchStartups,
  });

  const { data: selectedStartup, isLoading: isLoadingDetail, isError: isDetailError } = useQuery({
    queryKey: ['startup', selectedId],
    queryFn: () => fetchStartup(selectedId as string),
    enabled: Boolean(selectedId),
  });

  // Auto-select the first startup when data loads
  useEffect(() => {
    if (!selectedId && startups.length > 0) {
      setSelectedId(startups[0].id);
    }
  }, [selectedId, startups]);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Header />
      
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel: Portfolio Overview */}
        <div className="w-[480px] border-r border-border bg-card flex-shrink-0">
          <div className="p-4 border-b border-border">
            <h1 className="text-sm font-semibold text-foreground">Portfolio Risk Overview</h1>
            <p className="text-xs text-muted-foreground mt-0.5">
              {startups.length} companies · {startups.filter(s => s.severity === 'high').length} high risk
            </p>
          </div>
          <div className="h-[calc(100vh-14rem)]">
            {isLoading && (
              <div className="h-full flex items-center justify-center text-sm text-muted-foreground">Loading portfolio...</div>
            )}
            {isError && (
              <div className="h-full flex items-center justify-center text-sm text-destructive">Error loading portfolio</div>
            )}
            {!isLoading && !isError && (
              <PortfolioOverview
                startups={startups}
                selectedStartup={startups.find((s) => s.id === selectedId) || null}
                onSelectStartup={(startup) => setSelectedId(startup.id)}
              />
            )}
          </div>
        </div>

        {/* Right Panel: Detail View */}
        <div className="flex-1 bg-background overflow-hidden">
          {isLoadingDetail && (
            <div className="h-full flex items-center justify-center text-sm text-muted-foreground">
              Loading company details...
            </div>
          )}
          {isDetailError && (
            <div className="h-full flex items-center justify-center text-sm text-destructive">
              Error loading company details
            </div>
          )}
          {!isLoadingDetail && !isDetailError && selectedStartup ? (
            <StartupDetailPanel startup={selectedStartup} />
          ) : (
            <div className="h-full flex items-center justify-center">
              <p className="text-muted-foreground text-sm">
                Select a company to view risk details
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Index;
