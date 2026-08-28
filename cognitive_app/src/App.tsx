import { useState } from 'react';
import { Code, Brain, Atom, Database, Lightning, ChartLine, Play, BookOpen } from '@phosphor-icons/react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CodeGenerator } from '@/components/code/CodeGenerator';
import { InteractiveDemo } from '@/components/code/InteractiveDemo';
import { QuantumVisualizer } from '@/components/quantum/QuantumVisualizer';
import { QuantumDecisionEngine } from '@/components/quantum/QuantumDecisionEngine';
import { MemoryManagementDashboard } from '@/components/quantum/MemoryManagementDashboard';
import { AgentOrchestrationPanel } from '@/components/quantum/AgentOrchestrationPanel';
import { MetricsDashboard } from '@/components/quantum/MetricsDashboard';
import { ApiClient } from '@/components/cli';
import { XtermTerminal } from '@/components/cli/XtermTerminal';
import { DocumentationViewer } from '@/components/documentation';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [generatedCode, setGeneratedCode] = useState<string>('print("Hello from Codex AI!")');

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="relative border-b border-border bg-gradient-to-r from-[oklch(0.45_0.18_295)] via-[oklch(0.50_0.20_280)] to-[oklch(0.75_0.15_195)] overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="particle absolute w-1 h-1 bg-white rounded-full"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 3}s`,
              }}
            />
          ))}
        </div>
        <div className="relative container mx-auto px-6 py-8">
          <div className="flex items-center gap-4">
            <div className="flex items-center justify-center w-12 h-12 bg-white/10 backdrop-blur-sm rounded-lg">
              <Brain weight="duotone" className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white tracking-tight">
                Codex AI Assistant
              </h1>
              <p className="text-white/80 text-sm mt-1">
                Quantum-Enhanced Code Generation Platform
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-9 max-w-5xl mx-auto mb-8">
            <TabsTrigger value="dashboard" className="flex items-center gap-2">
              <ChartLine weight="duotone" className="w-4 h-4" />
              <span className="hidden sm:inline">Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="code" className="flex items-center gap-2">
              <Code weight="duotone" className="w-4 h-4" />
              <span className="hidden sm:inline">Code</span>
            </TabsTrigger>
            <TabsTrigger value="demo" className="flex items-center gap-2">
              <Play weight="duotone" className="w-4 h-4" />
              <span className="hidden sm:inline">Demo</span>
            </TabsTrigger>
            <TabsTrigger value="quantum" className="flex items-center gap-2">
              <Atom weight="duotone" className="w-4 h-4" />
              <span className="hidden sm:inline">Quantum</span>
            </TabsTrigger>
            <TabsTrigger value="memory" className="flex items-center gap-2">
              <Database weight="duotone" className="w-4 h-4" />
              <span className="hidden sm:inline">Memory</span>
            </TabsTrigger>
            <TabsTrigger value="agents" className="flex items-center gap-2">
              <Lightning weight="duotone" className="w-4 h-4" />
              <span className="hidden sm:inline">Agents</span>
            </TabsTrigger>
            <TabsTrigger value="physics" className="flex items-center gap-2">
              <span>🔬</span>
              <span className="hidden sm:inline">Physics</span>
            </TabsTrigger>
            <TabsTrigger value="cli" className="flex items-center gap-2">
              <span>💻</span>
              <span className="hidden sm:inline">CLI</span>
            </TabsTrigger>
            <TabsTrigger value="docs" className="flex items-center gap-2">
              <BookOpen weight="duotone" className="w-4 h-4" />
              <span className="hidden sm:inline">Docs</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard">
            <MetricsDashboard />
          </TabsContent>

          <TabsContent value="code">
            <CodeGenerator onCodeGenerated={setGeneratedCode} />
          </TabsContent>

          <TabsContent value="demo">
            <Card className="p-6">
              <h2 className="text-2xl font-semibold mb-4 text-accent">
                Interactive Code Demo
              </h2>
              <p className="text-muted-foreground mb-4">
                Test and execute generated code in real-time with resource monitoring.
              </p>
              <InteractiveDemo
                script={generatedCode || 'print("Hello from Codex AI!")'}
                language="python"
                onExecute={(result) => {
                  console.log('Execution result:', result);
                }}
              />
            </Card>
          </TabsContent>

          <TabsContent value="quantum">
            <Card className="p-6">
              <h2 className="text-2xl font-semibold mb-4 text-accent">
                Quantum Decision Visualizer
              </h2>
              <QuantumVisualizer />
            </Card>
          </TabsContent>

          <TabsContent value="memory">
            <MemoryManagementDashboard />
          </TabsContent>

          <TabsContent value="agents">
            <AgentOrchestrationPanel />
          </TabsContent>

          <TabsContent value="physics">
            <QuantumDecisionEngine />
          </TabsContent>

          <TabsContent value="cli">
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
              <XtermTerminal />
              <ApiClient />
            </div>
          </TabsContent>

          <TabsContent value="docs">
            <DocumentationViewer />
          </TabsContent>
        </Tabs>
      </main>

      <footer className="border-t border-border mt-16">
        <div className="container mx-auto px-6 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <span>Powered by</span>
              <span className="gradient-text font-semibold">_Codex_ Cognitive Brain</span>
            </div>
            <div className="flex items-center gap-4">
              <span>Level 4 MLOps Certified</span>
              <span>•</span>
              <span>2.86x Quantum Advantage</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
