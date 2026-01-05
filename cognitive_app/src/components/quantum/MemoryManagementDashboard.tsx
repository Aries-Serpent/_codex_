import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Database, MagnifyingGlass, Brain } from '@phosphor-icons/react';
import { useMemorySystem } from '@/hooks/use-memory-system';
import { MemoryEntryCard } from './MemoryEntryCard';
import { PatternLibraryBrowser } from './PatternLibraryBrowser';
import { useState } from 'react';

export function MemoryManagementDashboard() {
  const { state, searchResults, loading, searching, error, searchMemories } = useMemorySystem(true, 10000);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    searchMemories(query);
  };

  if (loading && !state) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center py-12">
          <Database weight="duotone" className="w-8 h-8 text-accent animate-pulse" />
          <span className="ml-3 text-muted-foreground">Loading memory system...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-6 border-destructive">
        <div className="text-destructive">
          <strong>Error:</strong> {error}
        </div>
      </Card>
    );
  }

  if (!state) return null;

  const stmPercentage = (state.stm_count / state.capacity) * 100;
  const ltmPercentage = (state.ltm_count / state.capacity) * 100;
  const cacheHitTarget = 30;
  const compressionTarget = 60;

  return (
    <div className="space-y-6">
      <Card className="p-6 bg-gradient-to-br from-card via-card to-[oklch(0.28_0.03_260)]">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-12 h-12 bg-primary/20 backdrop-blur-sm rounded-lg">
              <Brain weight="duotone" className="w-7 h-7 text-primary" />
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-accent">Memory Management</h2>
              <p className="text-sm text-muted-foreground">Hippocampus-Cortex Architecture</p>
            </div>
          </div>
          <Badge variant="outline" className="border-accent text-accent">
            {state.stm_count + state.ltm_count} / {state.capacity} Total
          </Badge>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="p-4 bg-muted/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-muted-foreground">STM (Short-Term)</span>
              <span className="text-xs text-[oklch(0.70_0.18_40)]">Hot Storage</span>
            </div>
            <div className="text-3xl font-mono font-bold text-[oklch(0.70_0.18_40)]">
              {state.stm_count}
            </div>
            <div className="mt-2 h-2 bg-background/50 rounded-full overflow-hidden">
              <div 
                className="h-full bg-[oklch(0.70_0.18_40)] transition-all"
                style={{ width: `${stmPercentage}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Last 5-10 interactions
            </p>
          </Card>

          <Card className="p-4 bg-muted/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-muted-foreground">LTM (Long-Term)</span>
              <span className="text-xs text-[oklch(0.60_0.15_220)]">Cold Storage</span>
            </div>
            <div className="text-3xl font-mono font-bold text-[oklch(0.60_0.15_220)]">
              {state.ltm_count}
            </div>
            <div className="mt-2 h-2 bg-background/50 rounded-full overflow-hidden">
              <div 
                className="h-full bg-[oklch(0.60_0.15_220)] transition-all"
                style={{ width: `${ltmPercentage}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Pattern library
            </p>
          </Card>

          <Card className="p-4 bg-muted/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-muted-foreground">Cache Hit Rate</span>
              {state.cache_hit_rate * 100 >= cacheHitTarget && (
                <span className="text-xs text-green-500">✓ Target</span>
              )}
            </div>
            <div className={`text-3xl font-mono font-bold ${
              state.cache_hit_rate * 100 >= cacheHitTarget ? 'text-green-500' : 'text-yellow-500'
            }`}>
              {(state.cache_hit_rate * 100).toFixed(1)}%
            </div>
            <div className="mt-2 h-2 bg-background/50 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all ${
                  state.cache_hit_rate * 100 >= cacheHitTarget ? 'bg-green-500' : 'bg-yellow-500'
                }`}
                style={{ width: `${state.cache_hit_rate * 100}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Target: ≥{cacheHitTarget}%
            </p>
          </Card>

          <Card className="p-4 bg-muted/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-muted-foreground">Compression</span>
              {state.compression_rate * 100 >= compressionTarget && (
                <span className="text-xs text-green-500">✓ Target</span>
              )}
            </div>
            <div className={`text-3xl font-mono font-bold ${
              state.compression_rate * 100 >= compressionTarget ? 'text-green-500' : 'text-yellow-500'
            }`}>
              {(state.compression_rate * 100).toFixed(1)}%
            </div>
            <div className="mt-2 h-2 bg-background/50 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all ${
                  state.compression_rate * 100 >= compressionTarget ? 'bg-green-500' : 'bg-yellow-500'
                }`}
                style={{ width: `${state.compression_rate * 100}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Target: ≥{compressionTarget}%
            </p>
          </Card>
        </div>
      </Card>

      <div>
        <div className="mb-4">
          <div className="relative">
            <MagnifyingGlass 
              weight="bold" 
              className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" 
            />
            <Input
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search memories by content, category, or type..."
              className="pl-10"
            />
          </div>
        </div>

        {searchQuery && (
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <MagnifyingGlass weight="duotone" className="w-5 h-5 text-accent" />
              Search Results ({searchResults.length})
            </h3>
            {searching ? (
              <Card className="p-8 text-center">
                <Database weight="duotone" className="w-8 h-8 mx-auto mb-2 text-accent animate-pulse" />
                <p className="text-muted-foreground">Searching memories...</p>
              </Card>
            ) : searchResults.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {searchResults.map((entry) => (
                  <MemoryEntryCard key={entry.id} entry={entry} />
                ))}
              </div>
            ) : (
              <Card className="p-8 text-center">
                <p className="text-muted-foreground">No memories found matching "{searchQuery}"</p>
              </Card>
            )}
          </div>
        )}
      </div>

      <PatternLibraryBrowser patterns={state.patterns} />

      <Card className="p-4 bg-muted/30">
        <p className="text-sm text-muted-foreground">
          <strong className="text-accent">Memory Architecture:</strong> The system implements a 
          hippocampus-cortex model with short-term memory (STM) for immediate context and long-term 
          memory (LTM) for consolidated patterns. Automatic consolidation occurs when STM capacity 
          is reached, with {(state.compression_rate * 100).toFixed(0)}% compression reducing storage 
          requirements while maintaining {(state.cache_hit_rate * 100).toFixed(0)}% cache hit rate.
        </p>
      </Card>
    </div>
  );
}
