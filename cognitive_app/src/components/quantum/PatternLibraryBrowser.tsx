import { Card } from '@/components/ui/card';
import { Database } from '@phosphor-icons/react';

/**
 * Pattern object from the pattern library.
 */
interface Pattern {
  id: string;  // Required: unique pattern identifier
  type?: string;
  usage_count?: number;
  compression_ratio?: number;
  last_accessed?: string;
}

interface PatternLibraryBrowserProps {
  patterns: Pattern[];
}

export function PatternLibraryBrowser({ patterns }: PatternLibraryBrowserProps) {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Database weight="duotone" className="w-5 h-5 text-accent" />
        Pattern Library ({patterns.length})
      </h3>

      {patterns.length === 0 ? (
        <Card className="p-8">
          <div className="text-center text-muted-foreground">
            <Database weight="duotone" className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No patterns stored yet</p>
            <p className="text-sm mt-1">Patterns will appear here as memories are consolidated</p>
          </div>
        </Card>
      ) : (
        <Card className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Pattern ID</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Type</th>
                  <th className="text-right py-3 px-4 font-medium text-muted-foreground">Usage Count</th>
                  <th className="text-right py-3 px-4 font-medium text-muted-foreground">Compression</th>
                  <th className="text-right py-3 px-4 font-medium text-muted-foreground">Last Accessed</th>
                </tr>
              </thead>
              <tbody>
                {patterns.slice(0, 10).map((pattern) => (
                  <tr key={pattern.id} className="border-b border-border/50 hover:bg-muted/30 transition-colors">
                    <td className="py-3 px-4 font-mono text-xs">{pattern.id}</td>
                    <td className="py-3 px-4">{pattern.type || 'unknown'}</td>
                    <td className="py-3 px-4 text-right font-mono">{pattern.usage_count || 0}</td>
                    <td className="py-3 px-4 text-right font-mono text-accent">
                      {pattern.compression_ratio ? `${(pattern.compression_ratio * 100).toFixed(0)}%` : 'N/A'}
                    </td>
                    <td className="py-3 px-4 text-right text-xs text-muted-foreground">
                      {pattern.last_accessed || 'Never'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {patterns.length > 10 && (
            <p className="text-center text-sm text-muted-foreground mt-4">
              Showing 10 of {patterns.length} patterns
            </p>
          )}
        </Card>
      )}
    </div>
  );
}
