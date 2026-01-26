import { useEffect, useRef, useState } from 'react';
import { Card } from '@/components/ui/card';
import { WorkflowToken } from '@/lib/workflow-dependency-engine';
import { motion } from 'framer-motion';
import { Lightning, CheckCircle, Circle } from '@phosphor-icons/react';

interface WaterfallNode {
  tokenId: string;
  token: WorkflowToken;
  status: 'waiting' | 'ready' | 'executing' | 'completed';
  x: number;
  y: number;
  depth: number;
  triggeredAt?: number;
}

interface CascadeWaterfallVisualizerProps {
  tokens: WorkflowToken[];
  activeTokens: Set<string>;
  completedTokens: Set<string>;
}

export function CascadeWaterfallVisualizer({
  tokens,
  activeTokens,
  completedTokens,
}: CascadeWaterfallVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [nodes, setNodes] = useState<WaterfallNode[]>([]);
  const [cascadeEffects, setCascadeEffects] = useState<Array<{
    from: { x: number; y: number };
    to: { x: number; y: number };
    timestamp: number;
  }>>([]);
  const animationFrameRef = useRef<number>(0);

  useEffect(() => {
    const calculateLayout = () => {
      const depths = new Map<string, number>();
      
      const calculateDepth = (token: WorkflowToken): number => {
        if (depths.has(token.id)) return depths.get(token.id)!;
        
        if (!token.dependencies || token.dependencies.length === 0) {
          depths.set(token.id, 0);
          return 0;
        }
        
        const depTokens = tokens.filter(t => token.dependencies!.includes(t.id));
        const maxDepth = depTokens.length > 0 ? Math.max(...depTokens.map(calculateDepth)) : 0;
        const depth = maxDepth + 1;
        depths.set(token.id, depth);
        return depth;
      };

      tokens.forEach(token => calculateDepth(token));

      const width = containerRef.current?.clientWidth || 800;
      const depthValues = Array.from(depths.values());
      const maxDepth = depthValues.length > 0 ? Math.max(...depthValues) : 0;
      const height = Math.max(400, (maxDepth + 1) * 140);

      const depthGroups = new Map<number, WorkflowToken[]>();
      tokens.forEach(token => {
        const depth = depths.get(token.id) || 0;
        if (!depthGroups.has(depth)) {
          depthGroups.set(depth, []);
        }
        depthGroups.get(depth)!.push(token);
      });

      const waterfallNodes: WaterfallNode[] = [];
      depthGroups.forEach((tokensAtDepth, depth) => {
        const levelWidth = width - 120;
        const spacing = levelWidth / (tokensAtDepth.length + 1);

        tokensAtDepth.forEach((token, index) => {
          const status = completedTokens.has(token.id) ? 'completed' :
                        activeTokens.has(token.id) ? 'executing' :
                        depth === 0 ? 'ready' : 'waiting';

          waterfallNodes.push({
            tokenId: token.id,
            token,
            status,
            x: 60 + spacing * (index + 1),
            y: 60 + depth * 140,
            depth,
          });
        });
      });

      setNodes(waterfallNodes);

      if (canvasRef.current) {
        canvasRef.current.width = width;
        canvasRef.current.height = height;
      }
    };

    calculateLayout();
    const handleResize = () => calculateLayout();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [tokens, activeTokens, completedTokens]);

  useEffect(() => {
    nodes.forEach(node => {
      if (completedTokens.has(node.tokenId)) {
        const dependents = nodes.filter(n => 
          n.token.dependencies?.includes(node.tokenId)
        );

        dependents.forEach(dependent => {
          setCascadeEffects(prev => {
            const exists = prev.some(
              effect => effect.from.x === node.x && 
                       effect.from.y === node.y &&
                       effect.to.x === dependent.x &&
                       effect.to.y === dependent.y
            );

            if (exists) return prev;

            return [...prev, {
              from: { x: node.x, y: node.y },
              to: { x: dependent.x, y: dependent.y },
              timestamp: Date.now(),
            }];
          });
        });
      }
    });
  }, [completedTokens, nodes]);

  useEffect(() => {
    const animate = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      nodes.forEach(fromNode => {
        if (!fromNode.token.dependencies) return;

        fromNode.token.dependencies.forEach(depId => {
          const toNode = nodes.find(n => n.tokenId === depId);
          if (!toNode) return;

          ctx.beginPath();
          ctx.moveTo(toNode.x, toNode.y);
          ctx.lineTo(fromNode.x, fromNode.y);
          
          const isActive = activeTokens.has(fromNode.tokenId) || 
                          activeTokens.has(toNode.tokenId);
          const isCompleted = completedTokens.has(fromNode.tokenId) && 
                             completedTokens.has(toNode.tokenId);

          if (isCompleted) {
            ctx.strokeStyle = 'oklch(0.70 0.20 145)';
            ctx.lineWidth = 2;
          } else if (isActive) {
            ctx.strokeStyle = 'oklch(0.75 0.15 195)';
            ctx.lineWidth = 3;
          } else {
            ctx.strokeStyle = 'oklch(0.35 0.02 250)';
            ctx.lineWidth = 1.5;
          }
          
          ctx.setLineDash([4, 4]);
          ctx.stroke();
          ctx.setLineDash([]);
        });
      });

      const now = Date.now();
      setCascadeEffects(prev => prev.filter(effect => now - effect.timestamp < 2000));

      cascadeEffects.forEach(effect => {
        const age = now - effect.timestamp;
        const progress = age / 2000;
        
        if (progress >= 1) return;

        const currentX = effect.from.x + (effect.to.x - effect.from.x) * progress;
        const currentY = effect.from.y + (effect.to.y - effect.from.y) * progress;

        const gradient = ctx.createRadialGradient(
          currentX, currentY, 0,
          currentX, currentY, 20
        );
        gradient.addColorStop(0, `rgba(117, 201, 250, ${0.8 * (1 - progress)})`);
        gradient.addColorStop(1, `rgba(117, 201, 250, 0)`);

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(currentX, currentY, 20, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = 'oklch(0.75 0.15 195)';
        ctx.font = '16px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('⚡', currentX, currentY);
      });

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [nodes, cascadeEffects, activeTokens, completedTokens]);

  return (
    <Card className="p-6 bg-gradient-to-br from-card to-[oklch(0.26_0.03_265)]">
      <div className="flex items-center gap-3 mb-6">
        <div className="flex items-center justify-center w-12 h-12 bg-accent/20 backdrop-blur-sm rounded-lg">
          <Lightning weight="duotone" className="w-7 h-7 text-accent" />
        </div>
        <div>
          <h3 className="text-xl font-semibold text-accent">Cascade Waterfall View</h3>
          <p className="text-sm text-muted-foreground">
            Live cascading execution visualization
          </p>
        </div>
      </div>

      {tokens.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          <Lightning weight="duotone" className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p>No workflow tokens to visualize</p>
        </div>
      ) : (
        <div ref={containerRef} className="relative bg-[oklch(0.18_0.02_260)] rounded-lg overflow-hidden border border-border">
          <canvas
            ref={canvasRef}
            className="w-full"
            style={{ display: 'block' }}
          />

          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {nodes.map(node => {
              const isActive = activeTokens.has(node.tokenId);
              const isCompleted = completedTokens.has(node.tokenId);
              const isReady = node.status === 'ready' && !isActive && !isCompleted;

              return (
                <g key={node.tokenId}>
                  <motion.circle
                    cx={node.x}
                    cy={node.y}
                    r={35}
                    className={`transition-all ${
                      isCompleted ? 'fill-green-500/20 stroke-green-500' :
                      isActive ? 'fill-accent/20 stroke-accent' :
                      isReady ? 'fill-blue-500/20 stroke-blue-400' :
                      'fill-muted/20 stroke-border'
                    }`}
                    strokeWidth={isActive ? 3 : 2}
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ 
                      type: 'spring',
                      stiffness: 260,
                      damping: 20,
                      delay: node.depth * 0.1 
                    }}
                  />
                  
                  {isActive && (
                    <>
                      <motion.circle
                        cx={node.x}
                        cy={node.y}
                        r={35}
                        fill="none"
                        stroke="oklch(0.75 0.15 195)"
                        strokeWidth={2}
                        opacity={0.5}
                        initial={{ r: 35, opacity: 0.5 }}
                        animate={{ r: 50, opacity: 0 }}
                        transition={{ 
                          duration: 1.5,
                          repeat: Infinity,
                          ease: 'easeOut'
                        }}
                      />
                      <motion.circle
                        cx={node.x}
                        cy={node.y}
                        r={35}
                        fill="none"
                        stroke="oklch(0.75 0.15 195)"
                        strokeWidth={2}
                        opacity={0.5}
                        initial={{ r: 35, opacity: 0.5 }}
                        animate={{ r: 50, opacity: 0 }}
                        transition={{ 
                          duration: 1.5,
                          repeat: Infinity,
                          ease: 'easeOut',
                          delay: 0.75
                        }}
                      />
                    </>
                  )}

                  {isCompleted && (
                    <motion.circle
                      cx={node.x}
                      cy={node.y}
                      r={35}
                      fill="none"
                      stroke="oklch(0.70 0.20 145)"
                      strokeWidth={3}
                      initial={{ scale: 1, opacity: 0 }}
                      animate={{ scale: 1.3, opacity: 0 }}
                      transition={{ duration: 0.6 }}
                    />
                  )}

                  <text
                    x={node.x}
                    y={node.y}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize="20"
                  >
                    {node.token.icon}
                  </text>

                  {isCompleted && (
                    <text
                      x={node.x + 18}
                      y={node.y - 18}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fontSize="16"
                    >
                      ✓
                    </text>
                  )}

                  <text
                    x={node.x}
                    y={node.y + 50}
                    textAnchor="middle"
                    className="fill-foreground text-xs font-semibold"
                    fontSize="12"
                  >
                    {node.token.name}
                  </text>
                </g>
              );
            })}
          </svg>

          <div className="absolute bottom-4 right-4 flex gap-3 bg-card/90 backdrop-blur-sm px-4 py-2 rounded-lg border border-border">
            <div className="flex items-center gap-2 text-xs">
              <Circle weight="regular" className="w-3 h-3 text-muted-foreground" />
              <span className="text-muted-foreground">Waiting</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <Circle weight="fill" className="w-3 h-3 text-blue-400" />
              <span className="text-blue-400">Ready</span>
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
      )}
    </Card>
  );
}
