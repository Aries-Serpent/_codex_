import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '../resizable';

describe('resizable panels integration', () => {
  it.each(['horizontal', 'vertical'] as const)(
    'renders a %s group with an accessible resize handle',
    (orientation) => {
      render(
        <ResizablePanelGroup orientation={orientation} data-testid="group">
          <ResizablePanel id="first" defaultSize="40%">First panel</ResizablePanel>
          <ResizableHandle withHandle aria-label="Resize panels" />
          <ResizablePanel id="second" defaultSize="60%">Second panel</ResizablePanel>
        </ResizablePanelGroup>,
      );

      expect(screen.getByTestId('group')).toHaveStyle({
        flexDirection: orientation === 'horizontal' ? 'row' : 'column',
      });
      expect(screen.getByText('First panel')).toBeInTheDocument();
      expect(screen.getByText('Second panel')).toBeInTheDocument();
      const handle = screen.getByRole('separator', { name: 'Resize panels' });
      expect(handle).toHaveAttribute(
        'aria-orientation',
        orientation === 'horizontal' ? 'vertical' : 'horizontal',
      );
      expect(handle).toHaveAttribute('tabindex', '0');
      expect(handle.querySelector('svg')).toBeInTheDocument();
    },
  );

  it('preserves the direction prop used by existing wrapper consumers', () => {
    render(
      <ResizablePanelGroup direction="vertical" data-testid="group">
        <ResizablePanel>First panel</ResizablePanel>
        <ResizableHandle />
        <ResizablePanel>Second panel</ResizablePanel>
      </ResizablePanelGroup>,
    );

    expect(screen.getByTestId('group')).toHaveStyle({ flexDirection: 'column' });
    expect(screen.getByRole('separator')).toHaveAttribute('aria-orientation', 'horizontal');
  });
});
