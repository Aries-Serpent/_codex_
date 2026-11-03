import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DocumentationContent } from '../DocumentationContent';

describe('Markdown and KaTeX integration', () => {
  it('renders headings, tables, code, inline math and display math', () => {
    const { container } = render(
      <DocumentationContent markdown={[
        '# Dependency compatibility',
        '',
        '| Package | Status |',
        '| --- | --- |',
        '| marked | ready |',
        '',
        '`npm ci`',
        '',
        'Inline $x^2$ and display:',
        '',
        '$$\\frac{1}{2}$$',
      ].join('\n')} />,
    );

    expect(screen.getByRole('heading', { name: 'Dependency compatibility' })).toBeInTheDocument();
    expect(screen.getByRole('table')).toHaveTextContent('marked');
    expect(screen.getByText('npm ci').tagName).toBe('CODE');
    expect(container.querySelectorAll('.katex')).toHaveLength(2);
    expect(container.querySelector('.katex-display .katex-html')).toBeInTheDocument();
    expect(container.querySelector('.katex-error')).not.toBeInTheDocument();
  });

  it('keeps script content, event handlers and unsafe links out of rendered Markdown', () => {
    const { container } = render(
      <DocumentationContent markdown={[
        '<script>alert(1)</script>',
        '<img src="/image.png" onerror="alert(1)">',
        '',
        '[unsafe](javascript:alert%281%29)',
        '',
        '[safe](https://example.com/docs)',
        '',
        '$\\href{javascript:alert(1)}{unsafe}$',
      ].join('\n')} />,
    );

    expect(container.querySelector('script')).not.toBeInTheDocument();
    expect(container.querySelector('img')).not.toHaveAttribute('onerror');
    expect(screen.getByText('unsafe', { selector: 'a' })).not.toHaveAttribute('href');
    expect(screen.getByRole('link', { name: 'safe' })).toHaveAttribute('href', 'https://example.com/docs');
    expect(container.querySelector('[href^="javascript:"]')).not.toBeInTheDocument();
  });

  it('retains documentation navigation after Markdown rendering', async () => {
    const onNavigate = vi.fn();
    const user = userEvent.setup();
    render(<DocumentationContent markdown="Open [file:docs/README.md]" onNavigate={onNavigate} />);

    await user.click(screen.getByText('docs/README.md'));

    expect(onNavigate).toHaveBeenCalledExactlyOnceWith('docs/README.md');
  });
});
