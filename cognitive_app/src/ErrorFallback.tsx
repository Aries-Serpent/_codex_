import { Alert, AlertTitle, AlertDescription } from "./components/ui/alert";
import { Button } from "./components/ui/button";
import type { FallbackProps } from "react-error-boundary";

import { AlertTriangleIcon, RefreshCwIcon } from "lucide-react";

/**
 * ErrorFallback component for displaying error boundaries in the application.
 * 
 * In development mode, errors are rethrown to leverage the development server's
 * more detailed error overlay and debugging tools. The "parent UI" refers to
 * the browser's development error dialog (Vite/React DevTools overlay) which
 * provides stack traces, source maps, and interactive debugging features.
 * 
 * In production, this component renders a user-friendly error page with
 * the option to reset the error boundary and retry.
 * 
 * @param error - The error that was caught by the error boundary
 * @param resetErrorBoundary - Function to reset the error boundary state
 */
export const ErrorFallback = ({ error, resetErrorBoundary }: FallbackProps) => {
  // When encountering an error in development mode, rethrow it and don't display the boundary.
  // Vite's development server error overlay (and React's dev tools) will handle showing a richer error dialog.
  if (import.meta.env.DEV) throw error;

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Alert variant="destructive" className="mb-6">
          <AlertTriangleIcon />
          <AlertTitle>This spark has encountered a runtime error</AlertTitle>
          <AlertDescription>
            Something unexpected happened while running the application. The error details are shown below. Contact the spark author and let them know about this issue.
          </AlertDescription>
        </Alert>
        
        <div className="bg-card border rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-sm text-muted-foreground mb-2">Error Details:</h3>
          <pre className="text-xs text-destructive bg-muted/50 p-3 rounded border overflow-auto max-h-32">
            {error.message}
          </pre>
        </div>
        
        <Button 
          onClick={resetErrorBoundary} 
          className="w-full"
          variant="outline"
        >
          <RefreshCwIcon />
          Try Again
        </Button>
      </div>
    </div>
  );
}
