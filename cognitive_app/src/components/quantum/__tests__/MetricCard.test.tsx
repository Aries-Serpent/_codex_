import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MetricCard } from '@/components/quantum/MetricCard';
import { Brain } from '@phosphor-icons/react';

describe('MetricCard', () => {
  it('renders with basic props', () => {
    render(
      <MetricCard
        title="Test Metric"
        value="42"
        unit="ms"
      />
    );

    expect(screen.getByText('Test Metric')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('ms')).toBeInTheDocument();
  });

  it('displays icon when provided', () => {
    render(
      <MetricCard
        title="Test Metric"
        value="42"
        icon={<Brain data-testid="brain-icon" weight="duotone" className="w-4 h-4" />}
      />
    );

    expect(screen.getByTestId('brain-icon')).toBeInTheDocument();
  });

  it('shows status badge', () => {
    render(
      <MetricCard
        title="Test Metric"
        value="42"
        status="optimal"
      />
    );

    expect(screen.getByText('optimal')).toBeInTheDocument();
  });

  it('displays subtitle when provided', () => {
    render(
      <MetricCard
        title="Test Metric"
        value="42"
        subtitle="Additional info"
      />
    );

    expect(screen.getByText('Additional info')).toBeInTheDocument();
  });

  it('shows trend indicator with up trend', () => {
    render(
      <MetricCard
        title="Test Metric"
        value="42"
        trend="up"
        trendValue="+10%"
      />
    );

    expect(screen.getByText('+10%')).toBeInTheDocument();
  });

  it('shows trend indicator with down trend', () => {
    render(
      <MetricCard
        title="Test Metric"
        value="42"
        trend="down"
        trendValue="-5%"
      />
    );

    expect(screen.getByText('-5%')).toBeInTheDocument();
  });

  it('displays target when provided', () => {
    render(
      <MetricCard
        title="Test Metric"
        value="42"
        target="≥50"
      />
    );

    expect(screen.getByText(/Target:/)).toBeInTheDocument();
    expect(screen.getByText(/≥50/)).toBeInTheDocument();
  });

  it('applies correct status colors', () => {
    const { rerender } = render(
      <MetricCard
        title="Test Metric"
        value="42"
        status="optimal"
      />
    );

    let badge = screen.getByText('optimal');
    expect(badge).toHaveClass('text-[oklch(0.80_0.20_145)]');

    rerender(
      <MetricCard
        title="Test Metric"
        value="42"
        status="critical"
      />
    );

    badge = screen.getByText('critical');
    expect(badge).toHaveClass('text-[oklch(0.55_0.22_25)]');
  });

  it('renders sparkline when data provided', () => {
    const sparklineData = [0.1, 0.3, 0.5, 0.7, 0.9];
    
    render(
      <MetricCard
        title="Test Metric"
        value="42"
        sparkline={sparklineData}
      />
    );

    const svg = screen.getByRole('img', { hidden: true });
    expect(svg).toBeInTheDocument();
  });

  it('handles animated prop correctly', () => {
    const { rerender } = render(
      <MetricCard
        title="Test Metric"
        value="42"
        animated={true}
      />
    );

    let valueElement = screen.getByText('42');
    expect(valueElement.parentElement).toHaveStyle({ willChange: 'transform' });

    rerender(
      <MetricCard
        title="Test Metric"
        value="42"
        animated={false}
      />
    );

    valueElement = screen.getByText('42');
    expect(valueElement).toBeInTheDocument();
  });

  it('handles custom color prop', () => {
    render(
      <MetricCard
        title="Test Metric"
        value="42"
        color="text-blue-500"
      />
    );

    const valueElement = screen.getByText('42');
    expect(valueElement).toHaveClass('text-blue-500');
  });

  it('displays all status variants correctly', () => {
    const statuses: Array<'optimal' | 'good' | 'warning' | 'critical'> = ['optimal', 'good', 'warning', 'critical'];

    statuses.forEach(status => {
      const { unmount } = render(
        <MetricCard
          title="Test Metric"
          value="42"
          status={status}
        />
      );

      expect(screen.getByText(status)).toBeInTheDocument();
      unmount();
    });
  });
});
