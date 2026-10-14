import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MetricCard } from '../components/MetricCard';
import { DollarSign } from 'lucide-react';
import { FilterBar } from '../components/FilterBar';
import { LoadingSpinner, ErrorAlert, EmptyState } from '../components/StatusStates';

describe('InsightIQ UI Component Suite', () => {
  it('renders MetricCard with title, value, and formula note correctly', () => {
    render(
      <MetricCard
        title="Total Revenue"
        value="$2,703,982.31"
        icon={DollarSign}
        growthPct={12.5}
        hasBaseline={true}
        formulaNote="Sum of revenue across orders"
      />
    );

    expect(screen.getByText('Total Revenue')).toBeInTheDocument();
    expect(screen.getByText('$2,703,982.31')).toBeInTheDocument();
    expect(screen.getByText('+12.5%')).toBeInTheDocument();
    expect(screen.getByText('vs prior period')).toBeInTheDocument();
  });

  it('renders FilterBar with options and handles interactions', () => {
    const mockChange = vi.fn();
    const mockReset = vi.fn();

    render(
      <FilterBar
        filters={{ dataset_id: 'sample_superstore', region: 'All', category: 'All' }}
        options={{
          regions: ['All', 'North', 'South'],
          categories: ['All', 'Technology', 'Furniture'],
          segments: ['All', 'Consumer'],
          min_date: ['2024-01-01'],
          max_date: ['2025-12-31'],
        }}
        onChange={mockChange}
        onReset={mockReset}
      />
    );

    expect(screen.getByText('Interactive Analytical Filters')).toBeInTheDocument();
    expect(screen.getByText('Reset Filters')).toBeInTheDocument();
  });

  it('renders LoadingSpinner, ErrorAlert, and EmptyState components', () => {
    const { rerender } = render(<LoadingSpinner message="Calculating forecast..." />);
    expect(screen.getByText('Calculating forecast...')).toBeInTheDocument();

    const mockRetry = vi.fn();
    rerender(<ErrorAlert title="Connection Failed" message="Backend offline" onRetry={mockRetry} />);
    expect(screen.getByText('Connection Failed')).toBeInTheDocument();
    expect(screen.getByText('Backend offline')).toBeInTheDocument();
    expect(screen.getByText('Retry Action')).toBeInTheDocument();

    rerender(<EmptyState title="No Records" description="Try clearing filters" />);
    expect(screen.getByText('No Records')).toBeInTheDocument();
    expect(screen.getByText('Try clearing filters')).toBeInTheDocument();
  });
});
