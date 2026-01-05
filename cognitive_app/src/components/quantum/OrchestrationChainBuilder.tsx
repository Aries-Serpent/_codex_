import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Plus, Link, Lightning, Trash, ArrowRight, CheckCircle, Warning, TrendUp } from '@phosphor-icons/react';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import { useKV } from '@github/spark/hooks';
import { WorkflowToken, OrchestrationChain, workflowDependencyEngine } from '@/lib/workflow-dependency-engine';

interface OrchestrationChainBuilderProps {
  allTokens: WorkflowToken[];
  onChainExecute: (chain: OrchestrationChain) => void;
}

export function OrchestrationChainBuilder({ allTokens, onChainExecute }: OrchestrationChainBuilderProps) {
  const [chains, setChains] = useKV<OrchestrationChain[]>('orchestration-chains', []);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingChain, setEditingChain] = useState<OrchestrationChain | null>(null);
  
  const [newChain, setNewChain] = useState<Partial<OrchestrationChain>>({
    name: '',
    description: '',
    tokens: [],
    autoExecute: false,
  });

  const [selectedTokenId, setSelectedTokenId] = useState<string>('');
  const [expandedChain, setExpandedChain] = useState<string | null>(null);

  const handleCreateChain = () => {
    if (!newChain.name || !newChain.tokens || newChain.tokens.length === 0) {
      toast.error('Chain name and at least one token required');
      return;
    }

    const cycles = workflowDependencyEngine.detectCircularDependencies(
      allTokens.filter(t => newChain.tokens!.includes(t.id))
    );

    if (cycles.length > 0) {
      toast.error('Circular dependency detected', {
        description: `Tokens involved: ${cycles.join(', ')}`,
      });
      return;
    }

    const chain: OrchestrationChain = {
      id: `chain-${Date.now()}`,
      name: newChain.name,
      description: newChain.description || '',
      tokens: newChain.tokens,
      autoExecute: newChain.autoExecute || false,
      createdAt: Date.now(),
    };

    setChains(current => [...(current || []), chain]);

    toast.success('Orchestration chain created', {
      description: `${chain.name} with ${chain.tokens.length} tokens`,
    });

    setNewChain({ name: '', description: '', tokens: [], autoExecute: false });
    setDialogOpen(false);
  };

  const handleAddTokenToChain = () => {
    if (!selectedTokenId) return;

    if (newChain.tokens?.includes(selectedTokenId)) {
      toast.error('Token already in chain');
      return;
    }

    setNewChain(prev => ({
      ...prev,
      tokens: [...(prev.tokens || []), selectedTokenId],
    }));
    setSelectedTokenId('');
  };

  const handleRemoveTokenFromChain = (tokenId: string) => {
    setNewChain(prev => ({
      ...prev,
      tokens: (prev.tokens || []).filter(id => id !== tokenId),
    }));
  };

  const handleDeleteChain = (chainId: string) => {
    setChains(current => (current || []).filter(c => c.id !== chainId));
    toast.success('Chain deleted');
  };

  const handleExecuteChain = (chain: OrchestrationChain) => {
    const metrics = workflowDependencyEngine.calculateChainMetrics(chain, allTokens);
    
    toast.info(`Executing ${chain.name}`, {
      description: `${metrics.totalStages} stages across ${metrics.paradigmsUsed.length} paradigms`,
    });

    onChainExecute(chain);
  };

  const getChainTokens = (chain: OrchestrationChain): WorkflowToken[] => {
    return chain.tokens
      .map(id => allTokens.find(t => t.id === id))
      .filter(Boolean) as WorkflowToken[];
  };

  const getChainMetrics = (chain: OrchestrationChain) => {
    return workflowDependencyEngine.calculateChainMetrics(chain, allTokens);
  };

  const getSuggestions = (chain: OrchestrationChain) => {
    return workflowDependencyEngine.suggestOptimizations(chain, allTokens);
  };

  return (
    <Card className="p-6 bg-gradient-to-br from-card to-[oklch(0.27_0.03_270)]">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-12 h-12 bg-primary/20 backdrop-blur-sm rounded-lg">
            <Link weight="duotone" className="w-7 h-7 text-primary" />
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-primary">Orchestration Chains</h2>
            <p className="text-sm text-muted-foreground">
              Build automated workflows with token dependencies
            </p>
          </div>
        </div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus weight="bold" className="w-4 h-4 mr-2" />
              New Chain
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create Orchestration Chain</DialogTitle>
              <DialogDescription>
                Build a sequence of workflow tokens with automatic dependency resolution
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="chain-name">Chain Name</Label>
                <Input
                  id="chain-name"
                  placeholder="e.g., Full Code Review Pipeline"
                  value={newChain.name}
                  onChange={(e) => setNewChain(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="chain-description">Description</Label>
                <Textarea
                  id="chain-description"
                  placeholder="Describe what this chain does..."
                  value={newChain.description}
                  onChange={(e) => setNewChain(prev => ({ ...prev, description: e.target.value }))}
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label>Workflow Tokens</Label>
                <div className="flex gap-2">
                  <select
                    className="flex-1 px-3 py-2 rounded-md border border-input bg-background text-foreground"
                    value={selectedTokenId}
                    onChange={(e) => setSelectedTokenId(e.target.value)}
                  >
                    <option value="">Select a token...</option>
                    {allTokens.map(token => (
                      <option key={token.id} value={token.id}>
                        {token.icon} {token.name}
                      </option>
                    ))}
                  </select>
                  <Button onClick={handleAddTokenToChain} disabled={!selectedTokenId}>
                    <Plus weight="bold" className="w-4 h-4" />
                  </Button>
                </div>

                <div className="space-y-2 mt-3">
                  {(newChain.tokens || []).map((tokenId, idx) => {
                    const token = allTokens.find(t => t.id === tokenId);
                    if (!token) return null;

                    return (
                      <motion.div
                        key={tokenId}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center gap-2"
                      >
                        <span className="text-muted-foreground font-mono text-sm w-6">{idx + 1}.</span>
                        <Card className="flex-1 p-3 flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-xl">{token.icon}</span>
                            <span className="font-medium">{token.name}</span>
                            <div className="flex gap-1 ml-2">
                              {token.paradigms.slice(0, 2).map(p => (
                                <Badge key={p} variant="secondary" className="text-xs">
                                  {p}
                                </Badge>
                              ))}
                              {token.paradigms.length > 2 && (
                                <Badge variant="secondary" className="text-xs">
                                  +{token.paradigms.length - 2}
                                </Badge>
                              )}
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveTokenFromChain(tokenId)}
                          >
                            <Trash weight="bold" className="w-4 h-4 text-destructive" />
                          </Button>
                        </Card>
                        {idx < (newChain.tokens?.length || 0) - 1 && (
                          <ArrowRight weight="bold" className="w-4 h-4 text-muted-foreground" />
                        )}
                      </motion.div>
                    );
                  })}
                </div>
              </div>

              <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div className="space-y-0.5">
                  <Label htmlFor="auto-execute">Auto-execute on trigger</Label>
                  <p className="text-xs text-muted-foreground">
                    Start chain when dependencies are met
                  </p>
                </div>
                <Switch
                  id="auto-execute"
                  checked={newChain.autoExecute}
                  onCheckedChange={(checked) => setNewChain(prev => ({ ...prev, autoExecute: checked }))}
                />
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateChain}>
                Create Chain
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-4">
        {(chains || []).length === 0 ? (
          <Card className="p-12 text-center border-dashed">
            <Link weight="duotone" className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
            <h3 className="text-lg font-semibold mb-2 text-muted-foreground">No chains created yet</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Create orchestration chains to automate complex workflows
            </p>
            <Button onClick={() => setDialogOpen(true)}>
              <Plus weight="bold" className="w-4 h-4 mr-2" />
              Create First Chain
            </Button>
          </Card>
        ) : (
          (chains || []).map(chain => {
            const metrics = getChainMetrics(chain);
            const suggestions = getSuggestions(chain);
            const isExpanded = expandedChain === chain.id;

            return (
              <Card key={chain.id} className="overflow-hidden">
                <div className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-lg font-semibold">{chain.name}</h3>
                        {chain.autoExecute && (
                          <Badge variant="outline" className="bg-accent/20 text-accent border-accent">
                            Auto
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">{chain.description}</p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setExpandedChain(isExpanded ? null : chain.id)}
                      >
                        {isExpanded ? 'Hide' : 'Details'}
                      </Button>
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => handleExecuteChain(chain)}
                      >
                        <Lightning weight="duotone" className="w-4 h-4 mr-1" />
                        Execute
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteChain(chain.id)}
                      >
                        <Trash weight="bold" className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-3">
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <span className="font-mono">{chain.tokens.length}</span> tokens
                    </Badge>
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <span className="font-mono">{metrics.totalStages}</span> stages
                    </Badge>
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <span className="font-mono">{metrics.paradigmsUsed.length}</span> paradigms
                    </Badge>
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <span className="font-mono">~{Math.round(metrics.estimatedDuration / 1000)}s</span> duration
                    </Badge>
                  </div>

                  <div className="flex items-center gap-2 overflow-x-auto pb-2">
                    {getChainTokens(chain).map((token, idx) => (
                      <div key={token.id} className="flex items-center gap-2 flex-shrink-0">
                        <div className="flex items-center gap-2 px-3 py-2 bg-muted rounded-lg">
                          <span className="text-lg">{token.icon}</span>
                          <span className="text-sm font-medium whitespace-nowrap">{token.name}</span>
                        </div>
                        {idx < chain.tokens.length - 1 && (
                          <ArrowRight weight="bold" className="w-4 h-4 text-muted-foreground" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="border-t border-border"
                    >
                      <div className="p-4 space-y-4 bg-muted/30">
                        <div>
                          <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
                            <TrendUp weight="duotone" className="w-4 h-4" />
                            Chain Metrics
                          </h4>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            <Card className="p-3">
                              <p className="text-xs text-muted-foreground mb-1">Total Stages</p>
                              <p className="text-2xl font-bold font-mono">{metrics.totalStages}</p>
                            </Card>
                            <Card className="p-3">
                              <p className="text-xs text-muted-foreground mb-1">Parallel Tokens</p>
                              <p className="text-2xl font-bold font-mono">{metrics.parallelizableTokens}</p>
                            </Card>
                            <Card className="p-3">
                              <p className="text-xs text-muted-foreground mb-1">Critical Path</p>
                              <p className="text-2xl font-bold font-mono">{metrics.criticalPathLength}</p>
                            </Card>
                            <Card className="p-3">
                              <p className="text-xs text-muted-foreground mb-1">Paradigms</p>
                              <p className="text-2xl font-bold font-mono">{metrics.paradigmsUsed.length}</p>
                            </Card>
                          </div>
                        </div>

                        {suggestions.length > 0 && (
                          <div>
                            <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
                              <Warning weight="duotone" className="w-4 h-4 text-yellow-500" />
                              Optimization Suggestions
                            </h4>
                            <div className="space-y-2">
                              {suggestions.map((suggestion, idx) => (
                                <div key={idx} className="flex items-start gap-2 text-sm p-2 bg-yellow-500/10 border border-yellow-500/20 rounded">
                                  <CheckCircle weight="fill" className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                                  <span>{suggestion}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        <div>
                          <h4 className="text-sm font-semibold mb-2">Physics Paradigms Used</h4>
                          <div className="flex flex-wrap gap-2">
                            {metrics.paradigmsUsed.map(paradigm => (
                              <Badge key={paradigm} variant="outline" className="capitalize">
                                {paradigm}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </Card>
            );
          })
        )}
      </div>
    </Card>
  );
}
