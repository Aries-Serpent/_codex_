import { describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MermaidDiagram } from '../MermaidDiagram';

const mermaid = vi.hoisted(() => ({
  initialize: vi.fn(),
  render: vi.fn(),
}));
vi.mock('mermaid', () => ({ default: mermaid }));

describe('Mermaid lifecycle', () => {
  it('initializes strict rendering and rerenders changed charts', async () => {
    mermaid.render.mockResolvedValueOnce({ svg: '<svg><text>First</text></svg>' });
    const view = render(<MermaidDiagram chart="graph TD; A-->B" id="fixture-chart" />);
    await screen.findByText('First');
    expect(mermaid.initialize).toHaveBeenCalledWith(expect.objectContaining({
      startOnLoad: false,
      securityLevel: 'strict',
    }));

    mermaid.render.mockResolvedValueOnce({ svg: '<svg><text>Second</text></svg>' });
    view.rerender(<MermaidDiagram chart="graph TD; B-->C" id="fixture-chart" />);
    await screen.findByText('Second');
    expect(screen.queryByText('First')).not.toBeInTheDocument();
    expect(mermaid.render).toHaveBeenLastCalledWith('fixture-chart', 'graph TD; B-->C');
  });

  it('displays errors as text and recovers on a valid chart', async () => {
    mermaid.render.mockRejectedValueOnce(new Error('synthetic parse failure'));
    const view = render(<MermaidDiagram chart={'<script>invalid</script>'} />);
    await screen.findByText('Diagram render error');
    expect(screen.getByText('synthetic parse failure')).toBeInTheDocument();
    expect(view.container.querySelector('script')).not.toBeInTheDocument();
    expect(view.container.querySelector('pre')).toHaveTextContent('<script>invalid</script>');

    mermaid.render.mockResolvedValueOnce({ svg: '<svg><text>Recovered</text></svg>' });
    view.rerender(<MermaidDiagram chart="graph TD; C-->D" />);
    await screen.findByText('Recovered');
    expect(screen.queryByText('Diagram render error')).not.toBeInTheDocument();
  });

  it('does not replace a newer chart with a stale asynchronous result', async () => {
    let finishOld: (result: { svg: string }) => void = () => {};
    mermaid.render.mockImplementationOnce(() => new Promise((resolve) => {
      finishOld = resolve;
    }));
    const view = render(<MermaidDiagram chart="graph TD; Old-->Result" />);
    await waitFor(() => expect(mermaid.render).toHaveBeenCalled());
    mermaid.render.mockResolvedValueOnce({ svg: '<svg><text>Current</text></svg>' });
    view.rerender(<MermaidDiagram chart="graph TD; New-->Result" />);
    await screen.findByText('Current');
    finishOld({ svg: '<svg><text>Stale</text></svg>' });
    await waitFor(() => expect(screen.queryByText('Stale')).not.toBeInTheDocument());
    expect(screen.getByText('Current')).toBeInTheDocument();
  });
});
