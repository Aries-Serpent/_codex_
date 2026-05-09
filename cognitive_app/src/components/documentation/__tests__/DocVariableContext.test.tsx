/**
 * Tests for DocVariableContext — {{var}} template interpolation.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import {
  DocVariableProvider,
  DocVariableContext,
  useDocVariables,
  applyVariables,
} from '../DocVariableContext';

// ---------------------------------------------------------------------------
// applyVariables utility
// ---------------------------------------------------------------------------

describe('applyVariables', () => {
  it('returns the text unchanged when no variables', () => {
    const vars = new Map<string, string>();
    expect(applyVariables('Hello {{world}}', vars)).toBe('Hello {{world}}');
  });

  it('substitutes a known variable', () => {
    const vars = new Map([['name', 'Alice']]);
    expect(applyVariables('Hello {{name}}!', vars)).toBe('Hello Alice!');
  });

  it('substitutes multiple variables', () => {
    const vars = new Map([
      ['a', 'X'],
      ['b', 'Y'],
    ]);
    expect(applyVariables('{{a}} + {{b}}', vars)).toBe('X + Y');
  });

  it('leaves unknown variables unchanged', () => {
    const vars = new Map([['known', 'value']]);
    expect(applyVariables('{{known}} {{unknown}}', vars)).toBe('value {{unknown}}');
  });

  it('handles the same variable appearing multiple times', () => {
    const vars = new Map([['x', '42']]);
    expect(applyVariables('{{x}} and {{x}}', vars)).toBe('42 and 42');
  });

  it('returns unchanged text when variables map is empty', () => {
    const vars = new Map<string, string>();
    expect(applyVariables('no vars here', vars)).toBe('no vars here');
  });
});

// ---------------------------------------------------------------------------
// Context default value
// ---------------------------------------------------------------------------

describe('DocVariableContext default', () => {
  it('defaults to an empty Map', () => {
    let capturedMap: Map<string, string> | null = null;

    const Consumer: React.FC = () => {
      capturedMap = React.useContext(DocVariableContext);
      return null;
    };

    render(<Consumer />);
    expect(capturedMap).toBeInstanceOf(Map);
    expect((capturedMap as unknown as Map<string, string>).size).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// DocVariableProvider
// ---------------------------------------------------------------------------

describe('DocVariableProvider', () => {
  it('provides variables to children via context', () => {
    let capturedMap: Map<string, string> | null = null;

    const Consumer: React.FC = () => {
      capturedMap = React.useContext(DocVariableContext);
      return null;
    };

    render(
      <DocVariableProvider variables={{ version: '2.0.0', env: 'test' }}>
        <Consumer />
      </DocVariableProvider>,
    );

    expect(capturedMap).toBeInstanceOf(Map);
    expect((capturedMap as unknown as Map<string, string>).get('version')).toBe('2.0.0');
    expect((capturedMap as unknown as Map<string, string>).get('env')).toBe('test');
  });

  it('renders children', () => {
    render(
      <DocVariableProvider variables={{}}>
        <span data-testid="child">hello</span>
      </DocVariableProvider>,
    );
    expect(screen.getByTestId('child')).toBeTruthy();
  });
});

// ---------------------------------------------------------------------------
// useDocVariables hook
// ---------------------------------------------------------------------------

describe('useDocVariables', () => {
  it('returns an empty map outside a provider', () => {
    let result: Map<string, string> | null = null;

    const Consumer: React.FC = () => {
      result = useDocVariables();
      return null;
    };
    render(<Consumer />);
    expect(result).toBeInstanceOf(Map);
    expect((result as unknown as Map<string, string>).size).toBe(0);
  });

  it('returns the provider map inside a provider', () => {
    let result: Map<string, string> | null = null;

    const Consumer: React.FC = () => {
      result = useDocVariables();
      return null;
    };

    render(
      <DocVariableProvider variables={{ key: 'val' }}>
        <Consumer />
      </DocVariableProvider>,
    );

    expect((result as unknown as Map<string, string>).get('key')).toBe('val');
  });
});
