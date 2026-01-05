import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  BookOpen, 
  MagnifyingGlass, 
  Package, 
  Star, 
  TrendUp, 
  Lightning, 
  Download,
  CheckCircle,
  ArrowRight,
  Sparkle
} from '@phosphor-icons/react';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import { useKV } from '@github/spark/hooks';

interface WorkflowToken {
  id: string;
  name: string;
  icon: string;
  description: string;
  paradigms: string[];
  stages: string[];
  color: string;
  createdAt?: number;
}

interface TokenBundle {
  id: string;
  name: string;
  description: string;
  category: 'development' | 'operations' | 'data' | 'security' | 'quality' | 'analytics';
  tokens: WorkflowToken[];
  icon: string;
  popularity: number;
  tags: string[];
  complexity: 'beginner' | 'intermediate' | 'advanced';
}

const TEMPLATE_BUNDLES: TokenBundle[] = [
  {
    id: 'full-stack-dev',
    name: 'Full-Stack Development Suite',
    description: 'Complete workflow bundle for end-to-end application development',
    category: 'development',
    icon: '🏗️',
    popularity: 95,
    complexity: 'intermediate',
    tags: ['frontend', 'backend', 'testing', 'deployment'],
    tokens: [
      {
        id: 'SCAFFOLD',
        name: 'Project Scaffold',
        icon: '🏗️',
        description: 'Initialize project structure',
        paradigms: ['fractal', 'fluid'],
        stages: ['Analyze', 'Generate', 'Configure'],
        color: 'from-blue-500 to-cyan-500',
      },
      {
        id: 'API_BUILD',
        name: 'API Builder',
        icon: '🔌',
        description: 'Generate API endpoints',
        paradigms: ['electromagnetic', 'wave'],
        stages: ['Design', 'Implement', 'Document'],
        color: 'from-green-500 to-emerald-500',
      },
      {
        id: 'TEST_GEN',
        name: 'Test Generator',
        icon: '🧪',
        description: 'Create comprehensive tests',
        paradigms: ['chaos', 'fractal', 'wave'],
        stages: ['Analyze', 'Generate', 'Validate'],
        color: 'from-purple-500 to-pink-500',
      },
      {
        id: 'DEPLOY_PREP',
        name: 'Deploy Prepare',
        icon: '🚀',
        description: 'Optimize for deployment',
        paradigms: ['relativity', 'fluid'],
        stages: ['Optimize', 'Package', 'Verify'],
        color: 'from-orange-500 to-red-500',
      },
    ],
  },
  {
    id: 'mlops-pipeline',
    name: 'MLOps Pipeline',
    description: 'Machine learning operations and model lifecycle management',
    category: 'data',
    icon: '🤖',
    popularity: 88,
    complexity: 'advanced',
    tags: ['ml', 'data-science', 'training', 'deployment'],
    tokens: [
      {
        id: 'DATA_PREP',
        name: 'Data Preparation',
        icon: '📊',
        description: 'Clean and transform datasets',
        paradigms: ['fluid', 'wave'],
        stages: ['Clean', 'Transform', 'Validate'],
        color: 'from-teal-500 to-cyan-500',
      },
      {
        id: 'MODEL_TRAIN',
        name: 'Model Training',
        icon: '🎯',
        description: 'Train ML models',
        paradigms: ['chaos', 'relativity', 'electromagnetic'],
        stages: ['Initialize', 'Train', 'Evaluate'],
        color: 'from-indigo-500 to-purple-500',
      },
      {
        id: 'HYPEROPT',
        name: 'Hyperparameter Optimization',
        icon: '⚙️',
        description: 'Optimize model parameters',
        paradigms: ['wave', 'chaos', 'fractal'],
        stages: ['Search', 'Test', 'Select'],
        color: 'from-violet-500 to-fuchsia-500',
      },
      {
        id: 'MODEL_DEPLOY',
        name: 'Model Deployment',
        icon: '🚀',
        description: 'Deploy trained models',
        paradigms: ['relativity', 'electromagnetic'],
        stages: ['Package', 'Deploy', 'Monitor'],
        color: 'from-orange-500 to-amber-500',
      },
    ],
  },
  {
    id: 'security-audit',
    name: 'Security & Compliance Suite',
    description: 'Comprehensive security scanning and compliance checking',
    category: 'security',
    icon: '🔒',
    popularity: 92,
    complexity: 'intermediate',
    tags: ['security', 'audit', 'compliance', 'vulnerability'],
    tokens: [
      {
        id: 'VULN_SCAN',
        name: 'Vulnerability Scanner',
        icon: '🔍',
        description: 'Detect security vulnerabilities',
        paradigms: ['chaos', 'fractal'],
        stages: ['Scan', 'Analyze', 'Prioritize'],
        color: 'from-red-500 to-rose-500',
      },
      {
        id: 'COMPLIANCE_CHECK',
        name: 'Compliance Checker',
        icon: '✅',
        description: 'Verify regulatory compliance',
        paradigms: ['wave', 'electromagnetic'],
        stages: ['Audit', 'Verify', 'Report'],
        color: 'from-green-500 to-emerald-500',
      },
      {
        id: 'SEC_PATCH',
        name: 'Security Patcher',
        icon: '🛡️',
        description: 'Apply security patches',
        paradigms: ['relativity', 'fluid'],
        stages: ['Detect', 'Apply', 'Verify'],
        color: 'from-blue-500 to-cyan-500',
      },
    ],
  },
  {
    id: 'devops-automation',
    name: 'DevOps Automation',
    description: 'Automated CI/CD pipelines and infrastructure management',
    category: 'operations',
    icon: '⚙️',
    popularity: 90,
    complexity: 'intermediate',
    tags: ['ci-cd', 'automation', 'infrastructure', 'monitoring'],
    tokens: [
      {
        id: 'CI_PIPELINE',
        name: 'CI Pipeline',
        icon: '🔄',
        description: 'Continuous integration workflow',
        paradigms: ['fluid', 'wave'],
        stages: ['Build', 'Test', 'Integrate'],
        color: 'from-blue-500 to-indigo-500',
      },
      {
        id: 'CD_DEPLOY',
        name: 'CD Deployment',
        icon: '🚀',
        description: 'Continuous deployment automation',
        paradigms: ['relativity', 'electromagnetic'],
        stages: ['Stage', 'Deploy', 'Verify'],
        color: 'from-green-500 to-teal-500',
      },
      {
        id: 'INFRA_PROVISION',
        name: 'Infrastructure Provisioning',
        icon: '🏗️',
        description: 'Provision cloud resources',
        paradigms: ['fractal', 'fluid'],
        stages: ['Plan', 'Provision', 'Configure'],
        color: 'from-purple-500 to-violet-500',
      },
      {
        id: 'MONITOR_ALERT',
        name: 'Monitoring & Alerts',
        icon: '📡',
        description: 'System monitoring setup',
        paradigms: ['wave', 'electromagnetic', 'chaos'],
        stages: ['Configure', 'Monitor', 'Alert'],
        color: 'from-orange-500 to-red-500',
      },
    ],
  },
  {
    id: 'code-quality',
    name: 'Code Quality & Refactoring',
    description: 'Maintain code health with automated analysis and improvements',
    category: 'quality',
    icon: '✨',
    popularity: 85,
    complexity: 'beginner',
    tags: ['refactoring', 'linting', 'formatting', 'optimization'],
    tokens: [
      {
        id: 'LINT_FIX',
        name: 'Lint & Fix',
        icon: '🔧',
        description: 'Automated code linting',
        paradigms: ['wave', 'fluid'],
        stages: ['Analyze', 'Fix', 'Verify'],
        color: 'from-yellow-500 to-orange-500',
      },
      {
        id: 'REFACTOR',
        name: 'Smart Refactor',
        icon: '♻️',
        description: 'Intelligent code refactoring',
        paradigms: ['fractal', 'chaos', 'relativity'],
        stages: ['Map', 'Transform', 'Test'],
        color: 'from-green-500 to-emerald-500',
      },
      {
        id: 'OPTIMIZE',
        name: 'Performance Optimizer',
        icon: '⚡',
        description: 'Optimize code performance',
        paradigms: ['electromagnetic', 'wave'],
        stages: ['Profile', 'Optimize', 'Benchmark'],
        color: 'from-purple-500 to-pink-500',
      },
    ],
  },
  {
    id: 'data-analytics',
    name: 'Data Analytics Workflow',
    description: 'End-to-end data analysis and visualization pipeline',
    category: 'analytics',
    icon: '📈',
    popularity: 82,
    complexity: 'intermediate',
    tags: ['analytics', 'visualization', 'reporting', 'insights'],
    tokens: [
      {
        id: 'DATA_EXTRACT',
        name: 'Data Extraction',
        icon: '📥',
        description: 'Extract data from sources',
        paradigms: ['fluid', 'electromagnetic'],
        stages: ['Connect', 'Extract', 'Load'],
        color: 'from-blue-500 to-cyan-500',
      },
      {
        id: 'ANALYZE',
        name: 'Statistical Analysis',
        icon: '📊',
        description: 'Perform statistical analysis',
        paradigms: ['wave', 'chaos', 'fractal'],
        stages: ['Clean', 'Analyze', 'Model'],
        color: 'from-indigo-500 to-purple-500',
      },
      {
        id: 'VISUALIZE',
        name: 'Data Visualization',
        icon: '📉',
        description: 'Generate visualizations',
        paradigms: ['fractal', 'wave'],
        stages: ['Transform', 'Render', 'Export'],
        color: 'from-green-500 to-teal-500',
      },
      {
        id: 'REPORT_GEN',
        name: 'Report Generator',
        icon: '📄',
        description: 'Create automated reports',
        paradigms: ['fluid', 'relativity'],
        stages: ['Compile', 'Format', 'Distribute'],
        color: 'from-orange-500 to-amber-500',
      },
    ],
  },
];

const CATEGORY_INFO = {
  development: { label: 'Development', color: 'from-blue-500 to-cyan-500', icon: '💻' },
  operations: { label: 'Operations', color: 'from-orange-500 to-red-500', icon: '⚙️' },
  data: { label: 'Data & ML', color: 'from-purple-500 to-pink-500', icon: '🤖' },
  security: { label: 'Security', color: 'from-red-500 to-rose-500', icon: '🔒' },
  quality: { label: 'Quality', color: 'from-green-500 to-emerald-500', icon: '✨' },
  analytics: { label: 'Analytics', color: 'from-indigo-500 to-violet-500', icon: '📈' },
};

const COMPLEXITY_COLORS = {
  beginner: 'bg-green-500/20 text-green-500 border-green-500',
  intermediate: 'bg-yellow-500/20 text-yellow-500 border-yellow-500',
  advanced: 'bg-red-500/20 text-red-500 border-red-500',
};

export function WorkflowTemplatesLibrary() {
  const [, setCustomTokens] = useKV<WorkflowToken[]>('custom-workflow-tokens', []);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedBundle, setSelectedBundle] = useState<TokenBundle | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const filteredBundles = TEMPLATE_BUNDLES.filter(bundle => {
    const matchesSearch = 
      bundle.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      bundle.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      bundle.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || bundle.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  }).sort((a, b) => b.popularity - a.popularity);

  const handleInstallBundle = (bundle: TokenBundle) => {
    const newTokens = bundle.tokens.map(token => ({
      ...token,
      id: `${bundle.id}_${token.id}_${Date.now()}`,
      createdAt: Date.now(),
    }));

    setCustomTokens((current) => [...(current || []), ...newTokens]);

    toast.success(`${bundle.name} installed!`, {
      description: `${newTokens.length} workflow tokens added to your collection`,
    });

    setIsDialogOpen(false);
    setSelectedBundle(null);
  };

  const handleViewDetails = (bundle: TokenBundle) => {
    setSelectedBundle(bundle);
    setIsDialogOpen(true);
  };

  return (
    <div className="space-y-6">
      <Card className="p-6 bg-gradient-to-br from-card via-card to-[oklch(0.28_0.03_260)]">
        <div className="flex items-center gap-3 mb-6">
          <div className="flex items-center justify-center w-12 h-12 bg-accent/20 backdrop-blur-sm rounded-lg">
            <BookOpen weight="duotone" className="w-7 h-7 text-accent" />
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-accent">Workflow Templates Library</h2>
            <p className="text-sm text-muted-foreground">
              Pre-configured token bundles for common workflows
            </p>
          </div>
        </div>

        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <MagnifyingGlass 
              weight="bold" 
              className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" 
            />
            <Input
              placeholder="Search templates by name, description, or tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="w-full">
          <TabsList className="grid grid-cols-7 w-full mb-6">
            <TabsTrigger value="all" className="text-xs">
              All
            </TabsTrigger>
            {Object.entries(CATEGORY_INFO).map(([key, info]) => (
              <TabsTrigger key={key} value={key} className="text-xs flex items-center gap-1">
                <span>{info.icon}</span>
                <span className="hidden lg:inline">{info.label}</span>
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent value={selectedCategory} className="mt-0">
            <AnimatePresence mode="wait">
              {filteredBundles.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="text-center py-12"
                >
                  <Package weight="duotone" className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No templates match your search</p>
                </motion.div>
              ) : (
                <motion.div
                  key={selectedCategory}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="grid grid-cols-1 md:grid-cols-2 gap-4"
                >
                  {filteredBundles.map((bundle, index) => {
                    const categoryInfo = CATEGORY_INFO[bundle.category];
                    return (
                      <motion.div
                        key={bundle.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        whileHover={{ scale: 1.02 }}
                      >
                        <Card className="p-5 h-full flex flex-col cursor-pointer hover:border-accent/50 transition-all">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-3">
                              <span className="text-4xl">{bundle.icon}</span>
                              <div>
                                <h3 className="font-semibold text-lg">{bundle.name}</h3>
                                <div className="flex items-center gap-2 mt-1">
                                  <Badge 
                                    variant="outline" 
                                    className={`text-xs ${COMPLEXITY_COLORS[bundle.complexity]}`}
                                  >
                                    {bundle.complexity}
                                  </Badge>
                                  <div className="flex items-center gap-1">
                                    <Star weight="fill" className="w-3 h-3 text-yellow-500" />
                                    <span className="text-xs font-medium">{bundle.popularity}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>

                          <p className="text-sm text-muted-foreground mb-3 flex-1">
                            {bundle.description}
                          </p>

                          <div className="space-y-3">
                            <div className="flex items-center gap-2">
                              <Badge variant="secondary" className="text-xs">
                                <Package weight="bold" className="w-3 h-3 mr-1" />
                                {bundle.tokens.length} tokens
                              </Badge>
                              <div className="h-1 flex-1 bg-muted rounded-full overflow-hidden">
                                <div 
                                  className={`h-full bg-gradient-to-r ${categoryInfo.color}`}
                                  style={{ width: `${bundle.popularity}%` }}
                                />
                              </div>
                            </div>

                            <div className="flex flex-wrap gap-1">
                              {bundle.tags.slice(0, 3).map(tag => (
                                <Badge key={tag} variant="outline" className="text-xs">
                                  {tag}
                                </Badge>
                              ))}
                              {bundle.tags.length > 3 && (
                                <Badge variant="outline" className="text-xs">
                                  +{bundle.tags.length - 3}
                                </Badge>
                              )}
                            </div>

                            <div className="flex gap-2 pt-2">
                              <Button
                                onClick={() => handleViewDetails(bundle)}
                                variant="outline"
                                className="flex-1"
                                size="sm"
                              >
                                <Sparkle weight="duotone" className="w-4 h-4 mr-2" />
                                Details
                              </Button>
                              <Button
                                onClick={() => handleInstallBundle(bundle)}
                                className={`flex-1 bg-gradient-to-r ${categoryInfo.color}`}
                                size="sm"
                              >
                                <Download weight="bold" className="w-4 h-4 mr-2" />
                                Install
                              </Button>
                            </div>
                          </div>
                        </Card>
                      </motion.div>
                    );
                  })}
                </motion.div>
              )}
            </AnimatePresence>
          </TabsContent>
        </Tabs>
      </Card>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh]">
          {selectedBundle && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-3 text-2xl">
                  <span className="text-4xl">{selectedBundle.icon}</span>
                  <div>
                    <div className="flex items-center gap-2">
                      {selectedBundle.name}
                      <Badge 
                        variant="outline" 
                        className={`text-xs ${COMPLEXITY_COLORS[selectedBundle.complexity]}`}
                      >
                        {selectedBundle.complexity}
                      </Badge>
                    </div>
                  </div>
                </DialogTitle>
                <DialogDescription className="text-base">
                  {selectedBundle.description}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-6 mt-4">
                <div className="flex items-center gap-6 p-4 bg-muted/30 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Package weight="duotone" className="w-5 h-5 text-accent" />
                    <div>
                      <div className="text-2xl font-bold">{selectedBundle.tokens.length}</div>
                      <div className="text-xs text-muted-foreground">Tokens</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <TrendUp weight="duotone" className="w-5 h-5 text-accent" />
                    <div>
                      <div className="text-2xl font-bold">{selectedBundle.popularity}</div>
                      <div className="text-xs text-muted-foreground">Popularity</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Lightning weight="duotone" className="w-5 h-5 text-accent" />
                    <div>
                      <div className="text-2xl font-bold">
                        {selectedBundle.tokens.reduce((acc, t) => acc + t.paradigms.length, 0)}
                      </div>
                      <div className="text-xs text-muted-foreground">Paradigms</div>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <Lightning weight="duotone" className="w-5 h-5 text-accent" />
                    Included Workflow Tokens
                  </h4>
                  <ScrollArea className="h-[400px] pr-4">
                    <div className="space-y-3">
                      {selectedBundle.tokens.map((token, index) => (
                        <motion.div
                          key={token.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                        >
                          <Card className="p-4">
                            <div className="flex items-start gap-3">
                              <span className="text-3xl">{token.icon}</span>
                              <div className="flex-1">
                                <h5 className="font-semibold mb-1">{token.name}</h5>
                                <p className="text-sm text-muted-foreground mb-3">
                                  {token.description}
                                </p>
                                
                                <div className="space-y-2">
                                  <div>
                                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                                      Paradigms
                                    </span>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                      {token.paradigms.map(paradigm => (
                                        <Badge key={paradigm} variant="secondary" className="text-xs capitalize">
                                          {paradigm}
                                        </Badge>
                                      ))}
                                    </div>
                                  </div>

                                  <div>
                                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                                      Execution Stages
                                    </span>
                                    <div className="flex items-center gap-1 mt-1">
                                      {token.stages.map((stage, idx) => (
                                        <div key={stage} className="flex items-center gap-1">
                                          <Badge variant="outline" className="text-xs">
                                            {stage}
                                          </Badge>
                                          {idx < token.stages.length - 1 && (
                                            <ArrowRight weight="bold" className="w-3 h-3 text-muted-foreground" />
                                          )}
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                </div>
                              </div>
                              <CheckCircle weight="duotone" className="w-5 h-5 text-accent flex-shrink-0" />
                            </div>
                          </Card>
                        </motion.div>
                      ))}
                    </div>
                  </ScrollArea>
                </div>

                <div className="flex gap-2 pt-4 border-t">
                  <Button
                    onClick={() => setIsDialogOpen(false)}
                    variant="outline"
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={() => handleInstallBundle(selectedBundle)}
                    className={`flex-1 bg-gradient-to-r ${CATEGORY_INFO[selectedBundle.category].color}`}
                  >
                    <Download weight="bold" className="w-4 h-4 mr-2" />
                    Install Bundle ({selectedBundle.tokens.length} tokens)
                  </Button>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
