import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Plus, Sparkle, X, Lightning, Check } from '@phosphor-icons/react';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import { useKV } from '@github/spark/hooks';

interface CustomWorkflowToken {
  id: string;
  name: string;
  icon: string;
  description: string;
  paradigms: string[];
  stages: string[];
  color: string;
  createdAt: number;
}

const PARADIGM_OPTIONS = [
  { 
    id: 'chaos', 
    name: 'Chaos Theory', 
    icon: '🌀', 
    description: 'Detect instabilities and non-linear dynamics',
    color: 'oklch(0.50 0.25 30)'
  },
  { 
    id: 'fractal', 
    name: 'Fractal Analysis', 
    icon: '🔺', 
    description: 'Identify self-similar patterns and scaling',
    color: 'oklch(0.55 0.22 60)'
  },
  { 
    id: 'fluid', 
    name: 'Fluid Dynamics', 
    icon: '💧', 
    description: 'Optimize flow and continuity',
    color: 'oklch(0.60 0.20 220)'
  },
  { 
    id: 'electromagnetic', 
    name: 'Electromagnetic', 
    icon: '⚡', 
    description: 'Analyze fields and interactions',
    color: 'oklch(0.65 0.20 180)'
  },
  { 
    id: 'wave', 
    name: 'Wave Theory', 
    icon: '〰️', 
    description: 'Process oscillations and interference',
    color: 'oklch(0.70 0.18 250)'
  },
  { 
    id: 'relativity', 
    name: 'Relativity', 
    icon: '⏰', 
    description: 'Manage temporal dependencies',
    color: 'oklch(0.50 0.20 320)'
  },
];

const COLOR_GRADIENTS = [
  { name: 'Ocean', value: 'from-blue-500 to-cyan-500' },
  { name: 'Forest', value: 'from-green-500 to-emerald-500' },
  { name: 'Sunset', value: 'from-orange-500 to-red-500' },
  { name: 'Cosmic', value: 'from-purple-500 to-pink-500' },
  { name: 'Royal', value: 'from-indigo-500 to-violet-500' },
  { name: 'Neon', value: 'from-teal-500 to-cyan-500' },
  { name: 'Aurora', value: 'from-violet-500 to-fuchsia-500' },
  { name: 'Solar', value: 'from-yellow-500 to-orange-500' },
];

const EMOJI_OPTIONS = ['🚀', '⚡', '🔬', '🧬', '🔮', '🌟', '💎', '🎯', '🔥', '💫', '🌈', '🎨', '🔧', '🛠️', '⚙️', '🔍', '📊', '🎪', '🏆', '💡'];

interface CustomWorkflowTokenCreatorProps {
  onTokenCreated?: (token: CustomWorkflowToken) => void;
}

export function CustomWorkflowTokenCreator({ onTokenCreated }: CustomWorkflowTokenCreatorProps) {
  const [customTokens, setCustomTokens] = useKV<CustomWorkflowToken[]>('custom-workflow-tokens', []);
  const [isOpen, setIsOpen] = useState(false);
  const [step, setStep] = useState(1);
  
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [icon, setIcon] = useState('🚀');
  const [selectedParadigms, setSelectedParadigms] = useState<string[]>([]);
  const [stages, setStages] = useState<string[]>(['']);
  const [selectedColor, setSelectedColor] = useState(COLOR_GRADIENTS[0].value);

  const resetForm = () => {
    setName('');
    setDescription('');
    setIcon('🚀');
    setSelectedParadigms([]);
    setStages(['']);
    setSelectedColor(COLOR_GRADIENTS[0].value);
    setStep(1);
  };

  const toggleParadigm = (paradigmId: string) => {
    setSelectedParadigms((current) =>
      current.includes(paradigmId)
        ? current.filter(id => id !== paradigmId)
        : [...current, paradigmId]
    );
  };

  const addStage = () => {
    setStages((current) => [...current, '']);
  };

  const updateStage = (index: number, value: string) => {
    setStages((current) => {
      const updated = [...current];
      updated[index] = value;
      return updated;
    });
  };

  const removeStage = (index: number) => {
    if (stages.length > 1) {
      setStages((current) => current.filter((_, i) => i !== index));
    }
  };

  const handleCreateToken = () => {
    if (!name.trim()) {
      toast.error('Token name is required');
      return;
    }
    
    if (selectedParadigms.length === 0) {
      toast.error('Select at least one paradigm');
      return;
    }
    
    const validStages = stages.filter(s => s.trim());
    if (validStages.length === 0) {
      toast.error('Add at least one stage');
      return;
    }

    const newToken: CustomWorkflowToken = {
      id: `CUSTOM_${Date.now()}`,
      name: name.trim(),
      icon,
      description: description.trim() || 'Custom workflow',
      paradigms: selectedParadigms,
      stages: validStages,
      color: selectedColor,
      createdAt: Date.now(),
    };

    setCustomTokens((current) => [...(current || []), newToken]);
    
    toast.success('Workflow token created!', {
      description: `${name} is ready to execute`,
    });

    if (onTokenCreated) {
      onTokenCreated(newToken);
    }

    setIsOpen(false);
    resetForm();
  };

  const deleteToken = (tokenId: string) => {
    setCustomTokens((current) => (current || []).filter(t => t.id !== tokenId));
    toast.info('Token deleted');
  };

  const canProceedToStep2 = name.trim() && description.trim();
  const canProceedToStep3 = selectedParadigms.length > 0;
  const canCreate = stages.filter(s => s.trim()).length > 0;

  return (
    <div className="space-y-4">
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogTrigger asChild>
          <Button 
            className="w-full bg-gradient-to-r from-primary to-secondary hover:opacity-90 transition-opacity"
            size="lg"
          >
            <Plus weight="bold" className="w-5 h-5 mr-2" />
            Create Custom Workflow Token
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-2xl">
              <Sparkle weight="duotone" className="w-6 h-6 text-accent" />
              Create Workflow Token
            </DialogTitle>
            <DialogDescription>
              Design a custom workflow with paradigm selection and execution stages
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 mt-4">
            <div className="flex items-center gap-2 mb-4">
              {[1, 2, 3, 4].map((s) => (
                <div key={s} className="flex items-center flex-1">
                  <div className={`flex items-center justify-center w-8 h-8 rounded-full font-semibold text-sm transition-all ${
                    step === s ? 'bg-accent text-accent-foreground scale-110' :
                    step > s ? 'bg-green-500 text-white' :
                    'bg-muted text-muted-foreground'
                  }`}>
                    {step > s ? <Check weight="bold" /> : s}
                  </div>
                  {s < 4 && (
                    <div className={`flex-1 h-1 mx-2 rounded-full transition-all ${
                      step > s ? 'bg-green-500' : 'bg-muted'
                    }`} />
                  )}
                </div>
              ))}
            </div>

            <AnimatePresence mode="wait">
              {step === 1 && (
                <motion.div
                  key="step1"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-4"
                >
                  <div>
                    <Label htmlFor="token-name" className="text-base font-semibold mb-2 block">
                      Token Name
                    </Label>
                    <Input
                      id="token-name"
                      placeholder="e.g., Smart Deploy, Data Pipeline, Health Check"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="text-lg"
                    />
                  </div>

                  <div>
                    <Label htmlFor="token-description" className="text-base font-semibold mb-2 block">
                      Description
                    </Label>
                    <Textarea
                      id="token-description"
                      placeholder="Describe what this workflow does..."
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      rows={3}
                    />
                  </div>

                  <div>
                    <Label className="text-base font-semibold mb-2 block">Icon</Label>
                    <div className="grid grid-cols-10 gap-2">
                      {EMOJI_OPTIONS.map((emoji) => (
                        <button
                          key={emoji}
                          onClick={() => setIcon(emoji)}
                          className={`text-2xl p-2 rounded-lg border-2 transition-all hover:scale-110 ${
                            icon === emoji ? 'border-accent bg-accent/10' : 'border-border'
                          }`}
                        >
                          {emoji}
                        </button>
                      ))}
                    </div>
                  </div>

                  <Button
                    onClick={() => setStep(2)}
                    disabled={!canProceedToStep2}
                    className="w-full"
                  >
                    Next: Select Paradigms
                  </Button>
                </motion.div>
              )}

              {step === 2 && (
                <motion.div
                  key="step2"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-4"
                >
                  <div>
                    <Label className="text-base font-semibold mb-3 block">
                      Select Physics Paradigms ({selectedParadigms.length} selected)
                    </Label>
                    <p className="text-sm text-muted-foreground mb-4">
                      Choose which physics paradigms will collaborate in this workflow
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {PARADIGM_OPTIONS.map((paradigm) => {
                        const isSelected = selectedParadigms.includes(paradigm.id);
                        return (
                          <motion.button
                            key={paradigm.id}
                            onClick={() => toggleParadigm(paradigm.id)}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className={`text-left p-4 rounded-lg border-2 transition-all ${
                              isSelected 
                                ? 'border-accent bg-accent/10 shadow-lg' 
                                : 'border-border hover:border-accent/50'
                            }`}
                          >
                            <div className="flex items-start gap-3">
                              <span className="text-3xl">{paradigm.icon}</span>
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-semibold">{paradigm.name}</span>
                                  {isSelected && (
                                    <Check weight="bold" className="w-4 h-4 text-accent" />
                                  )}
                                </div>
                                <p className="text-xs text-muted-foreground">{paradigm.description}</p>
                              </div>
                            </div>
                          </motion.button>
                        );
                      })}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button onClick={() => setStep(1)} variant="outline" className="flex-1">
                      Back
                    </Button>
                    <Button
                      onClick={() => setStep(3)}
                      disabled={!canProceedToStep3}
                      className="flex-1"
                    >
                      Next: Define Stages
                    </Button>
                  </div>
                </motion.div>
              )}

              {step === 3 && (
                <motion.div
                  key="step3"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-4"
                >
                  <div>
                    <Label className="text-base font-semibold mb-3 block">
                      Execution Stages
                    </Label>
                    <p className="text-sm text-muted-foreground mb-4">
                      Define the stages that agents will execute in sequence
                    </p>
                    <div className="space-y-3">
                      {stages.map((stage, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <Badge variant="outline" className="w-8 h-8 flex items-center justify-center">
                            {index + 1}
                          </Badge>
                          <Input
                            placeholder={`Stage ${index + 1} (e.g., Analyze, Process, Deploy)`}
                            value={stage}
                            onChange={(e) => updateStage(index, e.target.value)}
                            className="flex-1"
                          />
                          {stages.length > 1 && (
                            <Button
                              onClick={() => removeStage(index)}
                              variant="ghost"
                              size="icon"
                              className="text-destructive hover:text-destructive hover:bg-destructive/10"
                            >
                              <X weight="bold" className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      ))}
                    </div>
                    <Button
                      onClick={addStage}
                      variant="outline"
                      className="w-full mt-3"
                      disabled={stages.length >= 8}
                    >
                      <Plus weight="bold" className="w-4 h-4 mr-2" />
                      Add Stage {stages.length < 8 ? `(${stages.length}/8)` : '(Max reached)'}
                    </Button>
                  </div>

                  <div className="flex gap-2">
                    <Button onClick={() => setStep(2)} variant="outline" className="flex-1">
                      Back
                    </Button>
                    <Button
                      onClick={() => setStep(4)}
                      disabled={!canCreate}
                      className="flex-1"
                    >
                      Next: Customize
                    </Button>
                  </div>
                </motion.div>
              )}

              {step === 4 && (
                <motion.div
                  key="step4"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-4"
                >
                  <div>
                    <Label className="text-base font-semibold mb-3 block">
                      Color Theme
                    </Label>
                    <div className="grid grid-cols-4 gap-3">
                      {COLOR_GRADIENTS.map((gradient) => (
                        <button
                          key={gradient.value}
                          onClick={() => setSelectedColor(gradient.value)}
                          className={`relative p-4 rounded-lg border-2 transition-all hover:scale-105 ${
                            selectedColor === gradient.value ? 'border-accent' : 'border-border'
                          }`}
                        >
                          <div className={`h-12 rounded bg-gradient-to-r ${gradient.value}`} />
                          <p className="text-xs font-medium mt-2 text-center">{gradient.name}</p>
                          {selectedColor === gradient.value && (
                            <Check weight="bold" className="absolute top-2 right-2 w-4 h-4 text-accent" />
                          )}
                        </button>
                      ))}
                    </div>
                  </div>

                  <Card className="p-4 bg-muted/30">
                    <h4 className="font-semibold mb-3 flex items-center gap-2">
                      <Lightning weight="duotone" className="w-5 h-5 text-accent" />
                      Preview
                    </h4>
                    <Card className="p-4">
                      <div className="flex items-start justify-between mb-3">
                        <span className="text-3xl">{icon}</span>
                        <Badge variant="outline">Custom</Badge>
                      </div>
                      <h3 className="font-semibold text-lg mb-1">{name || 'Token Name'}</h3>
                      <p className="text-sm text-muted-foreground mb-3">{description || 'Description'}</p>
                      <div className="flex flex-wrap gap-1 mb-3">
                        {selectedParadigms.map(pId => {
                          const p = PARADIGM_OPTIONS.find(po => po.id === pId);
                          return p ? (
                            <Badge key={pId} variant="secondary" className="text-xs">
                              {p.icon} {p.name}
                            </Badge>
                          ) : null;
                        })}
                      </div>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <div className={`h-full w-3/4 bg-gradient-to-r ${selectedColor}`} />
                      </div>
                    </Card>
                  </Card>

                  <div className="flex gap-2">
                    <Button onClick={() => setStep(3)} variant="outline" className="flex-1">
                      Back
                    </Button>
                    <Button
                      onClick={handleCreateToken}
                      className="flex-1 bg-gradient-to-r from-primary to-secondary"
                    >
                      <Sparkle weight="duotone" className="w-4 h-4 mr-2" />
                      Create Token
                    </Button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </DialogContent>
      </Dialog>

      {(customTokens && customTokens.length > 0) && (
        <Card className="p-4">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <Badge variant="outline">{customTokens.length}</Badge>
            Your Custom Tokens
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {customTokens.map((token) => (
              <motion.div
                key={token.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
              >
                <Card className="p-3 relative group">
                  <Button
                    onClick={() => deleteToken(token.id)}
                    variant="ghost"
                    size="icon"
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity text-destructive hover:text-destructive hover:bg-destructive/10"
                  >
                    <X weight="bold" className="w-4 h-4" />
                  </Button>
                  <span className="text-2xl mb-2 block">{token.icon}</span>
                  <h4 className="font-semibold text-sm mb-1">{token.name}</h4>
                  <p className="text-xs text-muted-foreground mb-2 line-clamp-2">{token.description}</p>
                  <div className="flex flex-wrap gap-1">
                    {token.paradigms.slice(0, 2).map(pId => {
                      const p = PARADIGM_OPTIONS.find(po => po.id === pId);
                      return p ? (
                        <Badge key={pId} variant="secondary" className="text-xs">
                          {p.icon}
                        </Badge>
                      ) : null;
                    })}
                    {token.paradigms.length > 2 && (
                      <Badge variant="secondary" className="text-xs">
                        +{token.paradigms.length - 2}
                      </Badge>
                    )}
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
