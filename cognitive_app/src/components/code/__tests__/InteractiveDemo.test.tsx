import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { InteractiveDemo } from '../InteractiveDemo';

describe('InteractiveDemo', () => {
  const defaultProps = {
    script: 'console.log("Hello, World!");',
    language: 'javascript' as const,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render with initial script', () => {
    render(<InteractiveDemo {...defaultProps} />);
    
    expect(screen.getByDisplayValue('console.log("Hello, World!");')).toBeInTheDocument();
  });

  it('should render language badge', () => {
    render(<InteractiveDemo {...defaultProps} />);
    
    expect(screen.getByText('javascript')).toBeInTheDocument();
  });

  it('should show idle status initially', () => {
    render(<InteractiveDemo {...defaultProps} />);
    
    expect(screen.getByText(/idle/i)).toBeInTheDocument();
  });

  it('should allow editing script', () => {
    render(<InteractiveDemo {...defaultProps} />);
    
    const textarea = screen.getByDisplayValue('console.log("Hello, World!");');
    fireEvent.change(textarea, { target: { value: 'console.log("Updated");' } });
    
    expect(screen.getByDisplayValue('console.log("Updated");')).toBeInTheDocument();
  });

  it('should update script when prop changes', () => {
    const { rerender } = render(<InteractiveDemo {...defaultProps} />);
    
    expect(screen.getByDisplayValue('console.log("Hello, World!");')).toBeInTheDocument();
    
    rerender(<InteractiveDemo script="console.log('New');" language="javascript" />);
    
    expect(screen.getByDisplayValue("console.log('New');")).toBeInTheDocument();
  });

  it('should support Python language', () => {
    render(<InteractiveDemo script='print("Hello")' language="python" />);
    
    expect(screen.getByText('python')).toBeInTheDocument();
  });

  it('should support TypeScript language', () => {
    render(<InteractiveDemo script="const x: number = 5;" language="typescript" />);
    
    expect(screen.getByText('typescript')).toBeInTheDocument();
  });

  it('should support Bash language', () => {
    render(<InteractiveDemo script="echo 'test'" language="bash" />);
    
    expect(screen.getByText('bash')).toBeInTheDocument();
  });

  it('should have Run button', () => {
    render(<InteractiveDemo {...defaultProps} />);
    
    const runButton = screen.getByRole('button', { name: /run/i });
    expect(runButton).toBeInTheDocument();
  });

  it('should have Clear button', () => {
    render(<InteractiveDemo {...defaultProps} />);
    
    const clearButton = screen.getByRole('button', { name: /clear/i });
    expect(clearButton).toBeInTheDocument();
  });

  it('should render tabs for Output and Errors', () => {
    render(<InteractiveDemo {...defaultProps} />);
    
    expect(screen.getByText('Output')).toBeInTheDocument();
    expect(screen.getByText('Errors')).toBeInTheDocument();
  });

  it('should call onExecute callback when provided', async () => {
    const onExecute = vi.fn();
    render(<InteractiveDemo {...defaultProps} onExecute={onExecute} />);
    
    const runButton = screen.getByRole('button', { name: /run/i });
    fireEvent.click(runButton);
    
    await waitFor(() => {
      expect(onExecute).toHaveBeenCalled();
    }, { timeout: 6000 });
  });
});
