import { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { MotionConfig, motion } from 'framer-motion';
import { DocumentationContent } from '../../src/components/documentation/DocumentationContent';
import { MermaidDiagram } from '../../src/components/documentation/MermaidDiagram';
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '../../src/components/ui/resizable';
import '../../src/index.css';

export default function Fixture() {
  const [chart, setChart] = useState('graph TD; Alpha-->Beta');
  const [animate, setAnimate] = useState(false);
  const markdown = [
    '# Synthetic documentation',
    '',
    '| Dependency | Status |',
    '| --- | --- |',
    '| marked | rendered |',
    '',
    '`synthetic code` and $x^2$',
    '',
    '[unsafe](javascript:alert%281%29)',
    '',
    '<script>window.fixtureUnsafe = true</script>',
    '<span onclick="window.fixtureUnsafe = true">safe text</span>',
  ].join('\n');

  return (
    <main className="p-4">
      {(['horizontal', 'vertical', 'legacy', 'precedence'] as const).map((variant) => (
        <section key={variant} aria-label={`${variant} panels`} style={{ width: 600, height: 240 }}>
          <ResizablePanelGroup
            orientation={variant === 'legacy' ? undefined : variant === 'vertical' ? 'vertical' : 'horizontal'}
            direction={variant === 'legacy' || variant === 'precedence' ? 'vertical' : undefined}
          >
            <ResizablePanel id={`${variant}-first`} defaultSize="40%" minSize="10%">First</ResizablePanel>
            <ResizableHandle withHandle aria-label={`Resize ${variant}`} />
            <ResizablePanel id={`${variant}-second`} defaultSize="60%" minSize="10%">Second</ResizablePanel>
          </ResizablePanelGroup>
        </section>
      ))}
      <DocumentationContent markdown={markdown} />
      <section aria-label="Mermaid fixture">
        <button onClick={() => setChart('graph TD; Gamma-->Delta')}>Change chart</button>
        <button onClick={() => setChart('not a valid diagram')}>Invalid chart</button>
        <MermaidDiagram chart={chart} />
      </section>
      <MotionConfig reducedMotion="user">
        <button onClick={() => setAnimate(!animate)}>Animate fixture</button>
        <motion.div
          data-testid="motion-fixture"
          className="h-4 w-4 bg-red-500"
          initial={false}
          animate={{ x: animate ? 120 : 0, opacity: animate ? 0.5 : 1 }}
          transition={{ duration: 0.8 }}
        />
      </MotionConfig>
    </main>
  );
}

const root = document.getElementById('root');
if (!root) throw new Error('Missing fixture root');
createRoot(root).render(<Fixture />);
