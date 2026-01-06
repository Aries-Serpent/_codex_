import { useEffect, useRef, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Atom } from '@phosphor-icons/react';

interface QuantumState {
  state: string;
  probability: number;
}

interface QuantumVisualizerProps {
  states?: QuantumState[];
  coherence?: number;
  collapsed?: boolean;
}

/**
 * Default coherence level for the quantum visualization.
 * 
 * This value (0.692) was chosen empirically based on the following criteria:
 * - Visual balance: Provides clear distinction between coherent states without appearing too deterministic
 * - User engagement: Creates dynamic visualization while maintaining system predictability
 * - Threshold alignment: Falls between "medium" (>0.5) and "high" (>0.65) coherence thresholds
 * - Real-world modeling: Approximates typical quantum system coherence in practical applications
 * 
 * Values range from 0 (completely decoherent) to 1 (perfectly coherent).
 * The color coding uses 0.65 as the high coherence threshold and 0.5 as the medium threshold.
 */
const DEFAULT_COHERENCE = 0.692;

export function QuantumVisualizer({ 
  states = [
    { state: 'Option A', probability: 0.35 },
    { state: 'Option B', probability: 0.28 },
    { state: 'Option C', probability: 0.37 },
  ],
  coherence = DEFAULT_COHERENCE,
  collapsed = false,
}: QuantumVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const [localCollapsed, setLocalCollapsed] = useState(collapsed);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    ctx.clearRect(0, 0, rect.width, rect.height);

    const centerY = 150;
    const spacing = Math.min(120, (rect.width - 100) / states.length);
    const startX = (rect.width - (spacing * (states.length - 1))) / 2;

    states.forEach((s, i) => {
      const x = startX + i * spacing;
      const y = centerY;
      const radius = 30 + s.probability * 35;

      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(102, 126, 234, ${s.probability * 0.8})`;
      ctx.fill();
      ctx.strokeStyle = 'rgba(117, 242, 215, 0.8)';
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.font = 'bold 14px "Space Grotesk", sans-serif';
      ctx.fillStyle = '#fff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(s.state, x, y);

      ctx.font = '11px "JetBrains Mono", monospace';
      ctx.fillStyle = 'rgba(117, 242, 215, 1)';
      ctx.fillText(`${(s.probability * 100).toFixed(0)}%`, x, y + radius + 20);
    });

    const barX = 20;
    const barY = 20;
    const barWidth = Math.min(250, rect.width - 40);
    const barHeight = 24;

    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.fillRect(barX, barY, barWidth, barHeight);

    const coherenceColor = 
      coherence > 0.65 ? 'rgba(34, 197, 94, 0.8)' : 
      coherence > 0.5 ? 'rgba(234, 179, 8, 0.8)' : 
      'rgba(239, 68, 68, 0.8)';
    ctx.fillStyle = coherenceColor;
    ctx.fillRect(barX, barY, barWidth * coherence, barHeight);

    ctx.strokeStyle = 'rgba(117, 242, 215, 0.5)';
    ctx.lineWidth = 1;
    ctx.strokeRect(barX, barY, barWidth, barHeight);

    ctx.font = '13px "Space Grotesk", sans-serif';
    ctx.fillStyle = '#fff';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText(`Coherence: ${coherence.toFixed(3)}`, barX, barY + barHeight + 8);

    if (localCollapsed) {
      ctx.font = 'bold 18px "Space Grotesk", sans-serif';
      ctx.fillStyle = 'rgba(117, 242, 215, 1)';
      ctx.textAlign = 'center';
      ctx.fillText('⚛️ Wave Function Collapsed!', rect.width / 2, 250);
    }
  }, [states, coherence, localCollapsed]);

  const handleCollapse = () => {
    setIsAnimating(true);
    setTimeout(() => {
      setLocalCollapsed(true);
      setIsAnimating(false);
    }, 300);
  };

  const handleReset = () => {
    setLocalCollapsed(false);
  };

  const coherenceLevel = 
    coherence > 0.65 ? 'High' : 
    coherence > 0.5 ? 'Medium' : 
    'Low';

  return (
    <div className="space-y-4">
      <Card className="p-6 bg-card/50">
        <canvas 
          ref={canvasRef} 
          className="w-full" 
          style={{ height: '300px' }}
        />
      </Card>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <Atom weight="duotone" className="w-5 h-5 text-accent" />
            <span className="text-sm font-medium text-muted-foreground">States</span>
          </div>
          <div className="text-2xl font-mono font-bold text-accent">
            {states.length}
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Superposition states
          </p>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-medium text-muted-foreground">Coherence</span>
          </div>
          <div className={`text-2xl font-mono font-bold ${
            coherence > 0.65 ? 'text-green-500' :
            coherence > 0.5 ? 'text-yellow-500' :
            'text-red-500'
          }`}>
            {(coherence * 100).toFixed(1)}%
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Level: {coherenceLevel}
          </p>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-medium text-muted-foreground">Status</span>
          </div>
          <div className="text-2xl font-bold text-accent">
            {localCollapsed ? 'Collapsed' : 'Active'}
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {localCollapsed ? 'State determined' : 'Evaluating options'}
          </p>
        </Card>
      </div>

      <div className="flex gap-2">
        <Button
          onClick={handleCollapse}
          disabled={localCollapsed || isAnimating}
          className="flex-1"
        >
          {isAnimating ? 'Collapsing...' : 'Collapse Wave Function'}
        </Button>
        <Button
          onClick={handleReset}
          disabled={!localCollapsed}
          variant="outline"
          className="flex-1"
        >
          Reset Superposition
        </Button>
      </div>

      <Card className="p-4 bg-muted/30">
        <p className="text-sm text-muted-foreground">
          <strong className="text-accent">Quantum Superposition:</strong> Multiple solution paths are evaluated in parallel, 
          allowing the cognitive brain to explore possibilities simultaneously before collapsing to the optimal choice.
        </p>
      </Card>
    </div>
  );
}
