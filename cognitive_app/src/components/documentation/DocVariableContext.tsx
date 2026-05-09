/**
 * DocVariableContext — React context for `{{var}}` template interpolation
 * in documentation content.
 *
 * Usage:
 *
 *   <DocVariableProvider variables={{ version: '1.2.3', env: 'production' }}>
 *     <DocumentationViewer />
 *   </DocVariableProvider>
 *
 * Within Markdown, `{{version}}` and `{{env}}` will be substituted
 * with their respective values before rendering.
 *
 * Unknown variables are left as-is (`{{unknown}}` → `{{unknown}}`).
 */

import React, { createContext, useContext, useMemo } from 'react';

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

/**
 * The context value is a Map from variable name → substitution string.
 * Using a Map (vs plain object) allows O(1) lookup without prototype pollution.
 */
export const DocVariableContext = createContext<Map<string, string>>(
  new Map(),
);

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------

export interface DocVariableProviderProps {
  /**
   * Dictionary of variable substitutions.
   * Key: variable name (alphanumeric + underscore).
   * Value: replacement string (HTML-safe; rendered as-is, not escaped).
   */
  variables: Record<string, string>;
  children: React.ReactNode;
}

/**
 * Provides `{{var}}` template substitution to all descendant
 * `<DocumentationContent>` components.
 *
 * The `variables` prop is accepted as a plain object for ergonomics.
 * Re-creates the internal Map whenever the `variables` reference changes,
 * so callers should memoize the object when it is constructed inline:
 *
 *   const vars = useMemo(() => ({ version: '1.0' }), []);
 *   <DocVariableProvider variables={vars}>...</DocVariableProvider>
 */
export const DocVariableProvider: React.FC<DocVariableProviderProps> = ({
  variables,
  children,
}) => {
  const varMap = useMemo(
    () => new Map(Object.entries(variables)),
    // variables is the stable reference provided by the caller
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [variables],
  );

  return (
    <DocVariableContext.Provider value={varMap}>
      {children}
    </DocVariableContext.Provider>
  );
};

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

/**
 * Returns the current variable map.
 *
 *   const vars = useDocVariables();
 *   const value = vars.get('version') ?? '(unknown)';
 */
export function useDocVariables(): Map<string, string> {
  return useContext(DocVariableContext);
}

// ---------------------------------------------------------------------------
// Utility
// ---------------------------------------------------------------------------

/**
 * Applies `{{var}}` substitutions to an arbitrary string using the
 * given variable map.  Useful for pre-processing outside of React render.
 *
 * Unknown variables are left unchanged.
 */
export function applyVariables(
  text: string,
  variables: Map<string, string>,
): string {
  if (variables.size === 0) return text;
  return text.replace(/\{\{(\w+)\}\}/g, (_, key: string) => {
    return variables.get(key) ?? `{{${key}}}`;
  });
}
