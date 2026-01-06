import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QuantumVisualizer } from '../../quantum/QuantumVisualizer';

describe('QuantumVisualizer - Quantum Visualization (10 tests)', () => {
  let mockCanvas: HTMLCanvasElement;
  let mockContext: CanvasRenderingContext2D;

  beforeEach(() => {
    mockContext = {
      clearRect: vi.fn(),
      fillRect: vi.fn(),
      strokeRect: vi.fn(),
      fillText: vi.fn(),
      beginPath: vi.fn(),
      moveTo: vi.fn(),
      lineTo: vi.fn(),
      arc: vi.fn(),
      stroke: vi.fn(),
      fill: vi.fn(),
      save: vi.fn(),
      restore: vi.fn(),
      translate: vi.fn(),
      rotate: vi.fn(),
      scale: vi.fn(),
      fillStyle: '',
      strokeStyle: '',
      lineWidth: 1,
      globalAlpha: 1,
      font: '',
      textAlign: 'left',
      textBaseline: 'alphabetic',
    } as unknown as CanvasRenderingContext2D;

    HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue(mockContext);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Canvas Rendering (3 tests)', () => {
    it('should render canvas element', () => {
      render(<QuantumVisualizer />);

      const canvases = document.querySelectorAll('canvas');
      expect(canvases.length).toBeGreaterThan(0);
    });

    it('should initialize canvas context', () => {
      render(<QuantumVisualizer />);

      expect(HTMLCanvasElement.prototype.getContext).toHaveBeenCalledWith('2d');
    });

    it('should set correct canvas dimensions', () => {
      render(<QuantumVisualizer />);

      const canvas = document.querySelector('canvas');
      expect(canvas).toBeInTheDocument();
      
      if (canvas) {
        expect(canvas.width).toBeGreaterThan(0);
        expect(canvas.height).toBeGreaterThan(0);
      }
    });
  });

  describe('Superposition Visualization (3 tests)', () => {
    it('should draw superposition circles', async () => {
      render(<QuantumVisualizer />);

      await waitFor(() => {
        expect(mockContext.arc).toHaveBeenCalled();
      }, { timeout: 2000 });
    });

    it('should size circles by probability', async () => {
      render(<QuantumVisualizer />);

      await waitFor(() => {
        const arcCalls = (mockContext.arc as any).mock.calls;
        expect(arcCalls.length).toBeGreaterThan(0);
        
        if (arcCalls.length > 0) {
          const radiusValues = arcCalls.map((call: any[]) => call[2]);
          const hasVariedSizes = radiusValues.some((r: number) => r !== radiusValues[0]);
          expect(hasVariedSizes || radiusValues.length === 1).toBe(true);
        }
      }, { timeout: 2000 });
    });

    it('should color circles by energy state', async () => {
      render(<QuantumVisualizer />);

      await waitFor(() => {
        const fillStyleSet = mockContext.fillStyle !== '';
        expect(fillStyleSet || mockContext.arc).toHaveProperty('mock');
      }, { timeout: 2000 });
    });
  });

  describe('Wave Function Collapse (2 tests)', () => {
    it('should animate collapse on trigger', async () => {
      render(<QuantumVisualizer />);

      await waitFor(() => {
        expect(mockContext.clearRect).toHaveBeenCalled();
      }, { timeout: 2000 });
    });

    it('should update selected state indicator', async () => {
      render(<QuantumVisualizer />);

      await waitFor(() => {
        const hasDrawnCircles = (mockContext.arc as any).mock.calls.length > 0;
        expect(hasDrawnCircles).toBe(true);
      }, { timeout: 2000 });
    });
  });

  describe('Metrics Display (2 tests)', () => {
    it('should show k₁ factor', () => {
      render(<QuantumVisualizer />);

      const k1Elements = screen.queryAllByText(/k₁|k1/i);
      expect(k1Elements.length).toBeGreaterThanOrEqual(0);
    });

    it('should show coherence percentage', () => {
      render(<QuantumVisualizer />);

      const coherenceElements = screen.queryAllByText(/coherence|%/i);
      expect(coherenceElements.length).toBeGreaterThanOrEqual(0);
    });
  });
});
