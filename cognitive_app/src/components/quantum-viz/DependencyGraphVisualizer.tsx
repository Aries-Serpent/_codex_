import { useEffect, useRef, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { WorkflowToken, workflowDependencyEngine } from '@/lib/workflow-dependency-engine';
import { GitBranch, CheckCircle, Circle, Warning } from '@phosphor-icons/react';
import { motion } from 'framer-motion';

interface DependencyGraphVisualizerProps {
  tokens: WorkflowToken[];
  highlightedToken?: string;
  executingTokens?: Set<string>;
  completedTokens?: Set<string>;
}

interface GraphNode {
  id: string;
  x: number;
  y: number;
  token: WorkflowToken;
  level: number;
}

export function DependencyGraphVisualizer({ 
  tokens, 
  highlightedToken,
  executingTokens = new Set(),
  completedTokens = new Set()
}: DependencyGraphVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const calculateLayout = () => {
      const levels = new Map<string, number>();
      const visited = new Set<string>();

      const calculateLevel = (tokenId: string, visited: Set<string>): number => {
        if (levels.has(tokenId)) return levels.get(tokenId)!;
        if (visited.has(tokenId)) return 0;

        visited.add(tokenId);
        const token = tokens.find(t => t.id === tokenId);
        if (!token) return 0;

        const dependencies = token.dependencies || [];
        if (dependencies.length === 0) {
          levels.set(tokenId, 0);
          return 0;
        }

        const maxDepLevel = Math.max(
          ...dependencies.map(depId => calculateLevel(depId, new Set(visited)))
        );
        const level = maxDepLevel + 1;
        levels.set(tokenId, level);
        return level;
      };

      tokens.forEach(token => calculateLevel(token.id, new Set()));

      const maxLevel = Math.max(...Array.from(levels.values()), 0);
      const levelGroups = new Map<number, WorkflowToken[]>();

      for (let i = 0; i <= maxLevel; i++) {
        levelGroups.set(i, []);
      }

      tokens.forEach(token => {
        const level = levels.get(token.id) || 0;
        levelGroups.get(level)?.push(token);
      });

      const width = containerRef.current?.clientWidth || 800;
      const height = Math.max(400, (maxLevel + 1) * 150);
      const nodeRadius = 40;
      const levelHeight = height / (maxLevel + 2);

      const graphNodes: GraphNode[] = [];

      levelGroups.forEach((tokensInLevel, level) => {
        const levelWidth = width - 100;
        const spacing = levelWidth / (tokensInLevel.length + 1);

        tokensInLevel.forEach((token, index) => {
          graphNodes.push({
            id: token.id,
            x: 50 + spacing * (index + 1),
            y: 50 + levelHeight * (level + 1),
            token,
            level,
          });
        });
      });

      setNodes(graphNodes);

      if (canvasRef.current) {
        canvasRef.current.height = height;
        canvasRef.current.width = width;
      }
    };

    calculateLayout();

    const handleResize = () => calculateLayout();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [tokens]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    nodes.forEach(node => {
      if (!node.token.dependencies) return;

      node.token.dependencies.forEach(depId => {
        const depNode = nodes.find(n => n.id === depId);
        if (!depNode) return;

        const isHighlighted = 
          highlightedToken === node.id || 
          highlightedToken === depId ||
          hoveredNode === node.id ||
          hoveredNode === depId;

        ctx.beginPath();
        ctx.moveTo(depNode.x, depNode.y);
        ctx.lineTo(node.x, node.y);
        
        if (isHighlighted) {
          ctx.strokeStyle = 'oklch(0.75 0.15 195)';
          ctx.lineWidth = 3;
        } else {
          ctx.strokeStyle = 'oklch(0.35 0.02 250)';
          ctx.lineWidth = 2;
        }
        
        ctx.setLineDash([5, 5]);
        ctx.stroke();
        ctx.setLineDash([]);

        const angle = Math.atan2(node.y - depNode.y, node.x - depNode.x);
        const arrowSize = 8;
        const arrowX = node.x - Math.cos(angle) * 45;
        const arrowY = node.y - Math.sin(angle) * 45;

        ctx.beginPath();
        ctx.moveTo(arrowX, arrowY);
        ctx.lineTo(
          arrowX - arrowSize * Math.cos(angle - Math.PI / 6),
          arrowY - arrowSize * Math.sin(angle - Math.PI / 6)
        );
        ctx.moveTo(arrowX, arrowY);
        ctx.lineTo(
          arrowX - arrowSize * Math.cos(angle + Math.PI / 6),
          arrowY - arrowSize * Math.sin(angle + Math.PI / 6)
        );
        ctx.strokeStyle = isHighlighted 
          ? 'oklch(0.75 0.15 195)' 
          : 'oklch(0.35 0.02 250)';
        ctx.lineWidth = 2;
        ctx.stroke();
      });
    });
  }, [nodes, highlightedToken, hoveredNode, executingTokens, completedTokens]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const clickedNode = nodes.find(node => {
      const distance = Math.sqrt(
        Math.pow(x - node.x, 2) + Math.pow(y - node.y, 2)
      );
      return distance <= 40;
    });

    if (clickedNode) {
      setHoveredNode(clickedNode.id);
    }
  };

  const getNodeStatus = (tokenId: string) => {
    if (completedTokens.has(tokenId)) return 'completed';
    if (executingTokens.has(tokenId)) return 'executing';
    return 'idle';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20 border-green-500 text-green-500';
      case 'executing':
        return 'bg-accent/20 border-accent text-accent';
      default:
        return 'bg-muted border-border text-muted-foreground';
    }
  };

  const selectedNode = hoveredNode ? nodes.find(n => n.id === hoveredNode) : null;

  return (
    <Card className="p-6 bg-gradient-to-br from-card to-[oklch(0.27_0.03_270)]">
      <div className="flex items-center gap-3 mb-6">
        <div className="flex items-center justify-center w-12 h-12 bg-secondary/20 backdrop-blur-sm rounded-lg">
          <GitBranch weight="duotone" className="w-7 h-7 text-secondary" />
        </div>
        <div>
          <h2 className="text-2xl font-semibold text-secondary">Dependency Graph</h2>
          <p className="text-sm text-muted-foreground">
            Visual representation of workflow token dependencies
          </p>
        </div>
      </div>

      {tokens.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          <GitBranch weight="duotone" className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p>No workflow tokens to display</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div ref={containerRef} className="relative bg-[oklch(0.18_0.02_260)] rounded-lg overflow-hidden border border-border">
            <canvas
              ref={canvasRef}
              onClick={handleCanvasClick}
              className="w-full cursor-pointer"
              style={{ display: 'block' }}
            />

            <svg className="absolute inset-0 w-full h-full pointer-events-none">
              {nodes.map(node => {
                const status = getNodeStatus(node.id);
                const isHighlighted = 
                  highlightedToken === node.id || 
                  hoveredNode === node.id;

                return (
                  <g key={node.id}>
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r={40}
                      className={`transition-all ${getStatusColor(status)} ${
                        isHighlighted ? 'opacity-100' : 'opacity-70'
                      }`}
                      fill="currentColor"
                      stroke="currentColor"
                      strokeWidth={isHighlighted ? 3 : 2}
                    />
                    <text
                      x={node.x}
                      y={node.y}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fontSize="24"
                    >
                      {node.token.icon}
                    </text>
                    {status === 'executing' && (
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r={40}
                        fill="none"
                        stroke="oklch(0.75 0.15 195)"
                        strokeWidth={2}
                        opacity={0.5}
                      >
                        <animate
                          attributeName="r"
                          from="40"
                          to="55"
                          dur="1.5s"
                          repeatCount="indefinite"
                        />
                        <animate
                          attributeName="opacity"
                          from="0.5"
                          to="0"
                          dur="1.5s"
                          repeatCount="indefinite"
                        />
                      </circle>
                    )}
                  </g>
                );
              })}
            </svg>

            <div className="absolute bottom-4 left-4 flex gap-4 bg-card/80 backdrop-blur-sm px-4 py-2 rounded-lg border border-border">
              <div className="flex items-center gap-2 text-xs">
                <Circle weight="fill" className="w-3 h-3 text-muted-foreground" />
                <span className="text-muted-foreground">Idle</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <Circle weight="fill" className="w-3 h-3 text-accent" />
                <span className="text-accent">Executing</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <CheckCircle weight="fill" className="w-3 h-3 text-green-500" />
                <span className="text-green-500">Completed</span>
              </div>
            </div>
          </div>

          {selectedNode && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Card className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{selectedNode.token.icon}</span>
                    <div>
                      <h3 className="font-semibold text-lg">{selectedNode.token.name}</h3>
                      <p className="text-sm text-muted-foreground">{selectedNode.token.description}</p>
                    </div>
                  </div>
                  <Badge variant="outline">Level {selectedNode.level}</Badge>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div>
                    <h4 className="text-sm font-semibold mb-2 text-muted-foreground">Dependencies</h4>
                    {selectedNode.token.dependencies && selectedNode.token.dependencies.length > 0 ? (
                      <div className="space-y-1">
                        {selectedNode.token.dependencies.map(depId => {
                          const depToken = tokens.find(t => t.id === depId);
                          return depToken ? (
                            <div key={depId} className="flex items-center gap-2 text-sm">
                              <span>{depToken.icon}</span>
                              <span>{depToken.name}</span>
                            </div>
                          ) : null;
                        })}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">No dependencies</p>
                    )}
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold mb-2 text-muted-foreground">Paradigms</h4>
                    <div className="flex flex-wrap gap-1">
                      {selectedNode.token.paradigms.map(paradigm => (
                        <Badge key={paradigm} variant="secondary" className="text-xs capitalize">
                          {paradigm}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-border">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-muted-foreground">Stages:</span>
                    <span className="font-mono font-semibold">{selectedNode.token.stages.length}</span>
                    <span className="text-muted-foreground mx-2">•</span>
                    <span className="text-muted-foreground">Priority:</span>
                    <span className="font-mono font-semibold">{selectedNode.token.priority || 50}</span>
                  </div>
                </div>
              </Card>
            </motion.div>
          )}

          {tokens.some(t => t.dependencies && t.dependencies.length > 0) && (
            <div className="flex items-start gap-2 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
              <Warning weight="duotone" className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
              <div className="text-sm">
                <p className="font-semibold text-blue-400 mb-1">Dependency Resolution</p>
                <p className="text-blue-300/80">
                  Tokens will execute automatically once their dependencies complete. 
                  Click a node to see its dependencies and dependents.
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
