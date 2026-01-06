interface CodeEditorProps {
  code: string;
  language?: string;
}

export function CodeEditor({ code, language = 'python' }: CodeEditorProps) {
  return (
    <div className="relative">
      <pre className="bg-muted/50 border border-border rounded-lg p-4 overflow-x-auto">
        <code className={`language-${language} text-sm font-mono leading-relaxed`}>
          {code}
        </code>
      </pre>
    </div>
  );
}
