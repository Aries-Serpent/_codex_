# Codex AI Assistant - Product Requirements Document

A GitHub Spark application that integrates with the _Codex_ cognitive brain backend for advanced AI-powered code generation, analysis, and transformation with quantum-inspired decision-making.

**Experience Qualities**:
1. **Intelligent** - Leverages quantum superposition for parallel evaluation, providing faster and more accurate code generation than traditional sequential approaches
2. **Transparent** - Exposes cognitive brain metrics (k₁ factor, coherence, cache hits) to demonstrate the decision-making process and build user trust
3. **Professional** - Enterprise-grade interface with syntax highlighting, real-time status indicators, and comprehensive error handling for production use

**Complexity Level**: Complex Application (advanced functionality, likely with multiple views)
This is a sophisticated MLOps integration platform featuring quantum decision visualization, memory management dashboards, agent orchestration, physics simulations, and multi-stage code transformation pipelines with real-time metrics.

## Essential Features

### 1. Code Generation Interface
- **Functionality**: Accept natural language prompts and generate Python code using the Codex backend
- **Purpose**: Core feature enabling users to leverage quantum-enhanced AI for code creation
- **Trigger**: User enters prompt (min 10 chars) and clicks "Generate Code"
- **Progression**: Input validation → API call to /infer → Loading state → Display generated code with metrics → Copy/download options
- **Success criteria**: Generated code displays in Monaco Editor with syntax highlighting, metrics shown (k₁ ≤0.35, coherence, time), copy functionality works

### 2. Quantum Decision Visualizer
- **Functionality**: Canvas-based visualization of superposition states, wave function collapse, and coherence metrics
- **Purpose**: Demonstrate quantum advantage and cognitive brain decision-making process in real-time
- **Trigger**: API response includes quantum_metrics data
- **Progression**: Parse quantum data → Render superposition circles → Animate collapse → Update coherence bar → Display advantage metrics
- **Success criteria**: Smooth 60fps animations, circles sized by probability, coherence bar color-coded (green >0.65, yellow 0.50-0.65, red <0.50), quantum advantage displayed (target: 2.86x)

### 3. Memory Management Dashboard
- **Functionality**: Display short-term and long-term memory patterns with consolidation tracking
- **Purpose**: Visualize cognitive brain's hippocampus-cortex memory architecture and cache performance
- **Trigger**: User navigates to Memory tab or clicks memory metrics
- **Progression**: Fetch /status endpoint → Parse memory data → Render STM list → Display LTM patterns → Show consolidation timeline → Update cache hit rate
- **Success criteria**: STM shows last 5 interactions with timestamps, LTM table displays pattern IDs with compression ratios, cache hit rate ≥30%, consolidation events animated

### 4. Agent Orchestration Panel
- **Functionality**: Execute and monitor autonomous agent workflows with cross-paradigm collaboration visualization, real-time token flow tracking, custom workflow token creation, automatic dependency resolution, cascading execution monitoring, and orchestration chain management
- **Purpose**: Enable tokenized workflow execution with intelligent agent collaboration across physics paradigms, automated dependency-based triggering, visual cascade waterfall tracking, and complex multi-token workflows
- **Trigger**: User clicks workflow token button, creates custom token, builds orchestration chain, starts cascade execution, or dependencies automatically trigger execution
- **Progression**: Select workflow token (or create new/build chain) → View paradigm requirements and dependencies → Click execute → Auto-resolve dependencies → Watch token flow between agents → Monitor stage progress → View cross-paradigm collaboration graph → Dependents auto-trigger on completion with visual cascade effects → Track cascading execution with waterfall visualizer → Complete with success/failure notification
- **Success criteria**: All 6 pre-built workflows executable with dependency awareness (AUDIT_EXEC has no deps, DOC_GEN/HEAL depend on AUDIT_EXEC, ORGANIZE depends on DECIDE, REVIEW depends on both ORGANIZE and HEAL), auto-triggering when dependencies complete, custom token creation with dependency selection, orchestration chains persist via useKV, dependency graph visualizer shows token relationships with canvas-based rendering, chain builder validates for circular dependencies and suggests optimizations, real-time metrics show parallel execution opportunities and critical path length, tokens display priority levels (40-90 range), blocked tokens show waiting status with reason, cascade monitor displays execution waterfall with levels and parallel groups, animated energy flows between completing and triggering tokens, real-time execution timer and progress tracking, pause/resume/stop cascade controls

### 4a. Custom Workflow Token Creator
- **Functionality**: Multi-step wizard for creating custom workflow tokens with paradigm selection, stage definition, and visual customization
- **Purpose**: Enable users to design bespoke workflows that orchestrate specific combinations of physics paradigms for their unique use cases
- **Trigger**: User clicks "Create Custom Workflow Token" button in orchestrator panel
- **Progression**: Open dialog → Step 1: Enter name, description, select icon → Step 2: Select physics paradigms (multi-select from 6 options) → Step 3: Define execution stages (add/remove/reorder) → Step 4: Choose color gradient and preview → Create token → Token appears in orchestrator grid with "Custom" badge → Persist to useKV storage
- **Success criteria**: 4-step wizard with progress indicators and navigation, paradigm selection shows all 6 options (chaos, fractal, fluid, electromagnetic, wave, relativity) with icons and descriptions, stage editor allows 1-8 stages with text input, 8 color gradient presets available, live preview shows token appearance, custom tokens persist between sessions, tokens display in orchestrator grid alongside pre-built ones with "Custom" badge, delete button on hover removes custom tokens

### 4b. Workflow Templates Library
- **Functionality**: Curated library of pre-configured workflow token bundles organized by category (development, operations, data, security, quality, analytics) with search, filtering, and one-click installation
- **Purpose**: Accelerate workflow setup by providing production-ready token bundles for common use cases, reducing manual token creation effort
- **Trigger**: User views workflow orchestrator panel or searches for specific workflow templates
- **Progression**: Browse templates by category → Search/filter by name, tags, or description → View bundle details in dialog → Preview included tokens with paradigms and stages → Click "Install" → All tokens from bundle added to custom tokens collection → Confirmation toast → Tokens immediately available in orchestrator grid
- **Success criteria**: 6 pre-configured bundles available (Full-Stack Dev, MLOps Pipeline, Security Suite, DevOps Automation, Code Quality, Data Analytics), each bundle contains 3-4 tokens, category tabs for filtering (all/development/operations/data/security/quality/analytics), search bar filters by name/description/tags in real-time, popularity score displayed (82-95 range), complexity badges (beginner/intermediate/advanced) with color coding, bundle details dialog shows all included tokens with full specs, install button adds all tokens with unique IDs and timestamps, installed tokens persist via useKV and appear with custom badge, bundle cards show token count and popularity bar, responsive grid layout (1 col mobile, 2 col desktop)

### 4c. Orchestration Chain Builder
- **Functionality**: Multi-step workflow orchestration system allowing users to create chains of dependent workflow tokens with automatic execution order, dependency validation, and performance metrics
- **Purpose**: Enable complex automated workflows that span multiple tokens, with intelligent sequencing based on dependencies and parallel execution opportunities
- **Trigger**: User clicks "New Chain" in Chains tab, builds token sequence, and saves
- **Progression**: Open chain builder dialog → Enter chain name and description → Add tokens to chain (drag/reorder) → Toggle auto-execute → System validates for circular dependencies → View chain metrics (total stages, parallel opportunities, critical path) → Create chain → Execute chain triggers tokens in dependency order → Monitor cascading execution → View optimization suggestions
- **Success criteria**: Chain creation with token selection and ordering, circular dependency detection with error messages, auto-execute toggle for automatic triggering, chain metrics display (total stages, parallelizable tokens, critical path length, paradigms used), optimization suggestions (paradigm balance warnings, parallelization opportunities, length concerns), chains persist via useKV, chain execution respects dependencies and executes in correct order, visual progress tracking across entire chain, individual token status within chain context

### 4d. Dependency Graph Visualizer
- **Functionality**: Interactive canvas-based graph showing workflow token dependencies as a directed acyclic graph (DAG) with levels, connections, and real-time execution status
- **Purpose**: Provide visual understanding of token relationships, execution order, and identify bottlenecks or optimization opportunities
- **Trigger**: User navigates to Graph tab in orchestrator panel
- **Progression**: Graph calculates token levels based on dependencies → Renders nodes in circular/hierarchical layout → Draws dependency arrows between tokens → Highlights executing/completed tokens → User clicks node to see details → Hover shows connections → Displays execution flow in real-time
- **Success criteria**: Canvas-based graph with SVG overlays, automatic layout calculation (level-based positioning), dependency arrows with directional indicators, node status colors (idle/executing/completed), animated pulse on active nodes, click to highlight dependencies and dependents, detail panel shows selected token info (dependencies, paradigms, priority, stages), legend for status colors, responsive sizing, smooth animations for state changes, no overlapping nodes

### 4e. Cascading Execution Monitor
- **Functionality**: Real-time visualization of automatic cascading workflow execution with level-based layout, parallel execution tracking, and animated energy flows between completing and triggering tokens
- **Purpose**: Watch automatic execution as tokens complete their dependencies, showcasing the intelligent dependency resolution and parallel execution capabilities of the orchestration engine
- **Trigger**: User clicks "Start Cascade" button with workflow tokens selected
- **Progression**: Calculate execution levels and parallel groups → Start cascade execution → Execute level 0 tokens (no dependencies) → Monitor progress per token → Auto-trigger level 1+ tokens as dependencies complete → Display energy flow animations between tokens → Show real-time execution timer → Track completion count → Display success metrics on completion
- **Success criteria**: Execution organized by depth levels with clear visual separation, parallel tokens at same level execute simultaneously, status indicators show waiting/ready/executing/completed/failed states, animated energy bolts travel from completed tokens to dependents, auto-trigger badges appear on triggered tokens, real-time execution timer with millisecond precision, pause/resume functionality maintains execution state, stop button cancels cascade, progress bar tracks overall completion percentage, stage-level progress for executing tokens, dependency indicators show which tokens are blocking, completion metrics display total time and token count, responsive grid layout (1-3 columns based on viewport), level labels with parallel token count badges

### 4f. Cascade Waterfall Visualizer
- **Functionality**: Canvas-based animated waterfall visualization showing cascading token execution with particle effects, pulsing animations, and flowing energy between nodes as dependencies complete
- **Purpose**: Provide dramatic, engaging visualization of the cascade execution flow, making dependency relationships and automatic triggering immediately apparent
- **Trigger**: User starts cascade execution or views Cascade tab while tokens are executing
- **Progression**: Calculate waterfall layout with tokens arranged by depth → Render nodes as animated circles with token icons → Draw dependency connections → Animate executing tokens with pulse rings → Show energy particles flowing from completed tokens to dependents → Update node status colors in real-time → Display completion checkmarks
- **Success criteria**: Canvas rendering with SVG overlay for nodes and text, automatic hierarchical layout (depth-based vertical positioning), horizontal spacing for parallel tokens, animated pulse rings on executing tokens (expanding circles fading out), energy particle effects traveling along dependency paths when tokens complete, status color coding (gray waiting, blue ready, cyan executing, green completed, red failed), smooth 60fps animations, node icons displayed in center, token names below nodes, legend showing status meanings, responsive canvas sizing, proper depth separation with arrow indicators between levels

### 5. Code Transformation Pipeline
- **Functionality**: Multi-stage ingestion (ingest → analyze → transform → verify) with visual progress tracking
- **Purpose**: Transform uploaded Python code with tier-based complexity (A/B/C) and real-time feedback
- **Trigger**: User uploads .py file, .zip, or provides Git URL
- **Progression**: File upload → Validation → Start pipeline → Track stage progress (0-100%) → Display ETAs → Show errors with diagnostics → Complete with transformed code
- **Success criteria**: Drag-drop works, pipeline stages animate (connecting arrows), progress bars accurate, errors show stack traces with retry option, diff viewer displays changes

### 6. Physics Paradigm Simulator
- **Functionality**: Interactive demonstrations of 6 physics paradigms with real-time collaboration visualization
- **Purpose**: Showcase physics-inspired optimization techniques and visualize cross-paradigm agent collaboration
- **Trigger**: User selects paradigm from dropdown, clicks workflow token, or hovers over paradigm in collaboration graph
- **Progression**: Select paradigm → Load parameter panel → View active agents → Adjust values → Render Canvas visualization (WebGL) → Compute results → Watch token transfers → Display interpretation → Export data
- **Success criteria**: 60fps rendering, dynamic parameter panels per paradigm, results table with units, presets load correctly ("Butterfly Effect", "Laminar Flow", etc.), collaboration graph shows connections between active paradigms with animated token flows

### 7. Workflow Token Flow Visualizer
- **Functionality**: Real-time stream of token transfers between agents with paradigm context
- **Purpose**: Provide transparency into how workflows execute across distributed agents
- **Trigger**: Workflow token execution begins
- **Progression**: Workflow starts → Tokens generated → Stream displays transfers with source/destination → Show paradigm context → Animate in-flight tokens → Mark completed transfers → Display latency metrics → Auto-scroll recent activity
- **Success criteria**: Transfers appear in real-time, show agent names and paradigms, in-flight tokens animate, completed transfers marked green, metrics update (total transfers, active count, avg latency), auto-clear old transfers after 5s

### 8. Cross-Paradigm Collaboration Graph
- **Functionality**: Circular network graph showing agent paradigms and their active connections
- **Purpose**: Visualize how different physics paradigms collaborate on complex workflows
- **Trigger**: Agents become active or workflow execution begins
- **Progression**: Parse active agents → Group by paradigm → Calculate positions in circle → Draw connecting lines → Animate connection strength → Highlight on hover → Show agent details → Update metrics
- **Success criteria**: Paradigms positioned in circle, active connections drawn with animated dash lines, hover shows agent list, connection opacity reflects collaboration strength, metrics display (active connections, paradigms collaborating, active agents)

## Edge Case Handling

- **API Timeout** - Show "Request taking longer than expected" after 30s, keep loading state, retry button appears after 60s
- **Rate Limiting (429)** - Display banner with remaining quota, countdown to reset, upgrade link, disable submit button temporarily
- **Invalid Code Output** - Parse check generated code, show "Code validation failed" with syntax errors, offer regeneration with different parameters
- **WebSocket Disconnect** - Fallback to polling (5s intervals), show offline indicator, attempt reconnection every 30s
- **Large File Uploads** - Validate size <10MB, show progress bar for uploads >1MB, reject with helpful message if too large
- **Empty Prompt** - Disable submit until 10+ characters entered, show character counter with validation states
- **Concurrent Requests** - Queue additional requests, show "Processing previous request..." message, max queue depth of 3
- **Memory Overflow** - Display warning if STM >50 entries, suggest clearing cache, auto-consolidate to LTM
- **No Active Agents** - Display "Waiting for agents to activate" message in collaboration graph, disable workflow execution until agents available
- **Token Transfer Failure** - Show failed transfer in red, provide retry option, log failure to console with diagnostic info
- **Paradigm Overload** - If single paradigm handles >80% of tokens, display warning suggesting workflow rebalancing
- **Custom Token Validation** - Prevent token creation with empty name/stages, show inline validation errors, disable "Create" button until all required fields valid
- **Duplicate Custom Token** - Allow duplicate names but generate unique IDs with timestamp, show creation timestamp in token metadata
- **Max Custom Tokens** - No hard limit enforced, but UI may become crowded - consider pagination or filtering if user creates >20 custom tokens
- **Template Bundle Already Installed** - Allow re-installation of bundles (generates new unique IDs), show confirmation toast indicating tokens were added again
- **Empty Template Search** - Display "No templates match your search" message with package icon when no results found
- **Large Bundle Installation** - For bundles with 4+ tokens, show loading state during installation, batch add tokens in single useKV update for performance
- **Circular Dependencies** - Detect circular dependencies during chain creation, show error with tokens involved, prevent chain creation until resolved
- **Dependency Blocking** - Show "Blocked" status on tokens with unsatisfied dependencies, display tooltip with specific tokens blocking execution
- **Chain Execution Failure** - If any token in chain fails, show failure notification, option to retry failed token or entire chain, log error details
- **Empty Dependency Graph** - Show "No dependencies defined" message when all tokens are independent, suggest adding dependencies for automation
- **Graph Layout Overflow** - For graphs with 15+ tokens, implement zoom and pan controls, minimap for navigation

## Design Direction

The design should evoke **cutting-edge AI sophistication** combined with **scientific precision**. Visual language should feel like a quantum computing interface meets a professional development tool - sleek dark backgrounds with vibrant accent gradients, technical data visualizations, and subtle particle effects suggesting quantum superposition. The interface should inspire confidence through clarity while maintaining an air of advanced technology.

## Color Selection

**Quantum-Inspired Gradient Palette with High Contrast**

- **Primary Color**: Deep Purple `oklch(0.45 0.18 295)` - Represents quantum superposition, conveys innovation and advanced AI capabilities, used for primary CTAs and quantum visualizations
- **Secondary Colors**: 
  - Vibrant Indigo `oklch(0.50 0.20 280)` - Supporting quantum theme, used for secondary actions and accents
  - Electric Blue `oklch(0.60 0.15 250)` - Technology and precision, used for data visualizations and active states
  - Deep Slate `oklch(0.25 0.02 250)` - Dark UI backgrounds, cards, and panels
- **Accent Color**: Neon Cyan `oklch(0.75 0.15 195)` - High-visibility highlight for CTAs, success states, and important metrics (cache hits, quantum advantage indicators)
- **Foreground/Background Pairings**:
  - Background Dark `oklch(0.15 0.02 260)`: Light text `oklch(0.95 0 0)` - Ratio 13.8:1 ✓
  - Primary Purple `oklch(0.45 0.18 295)`: White text `oklch(1 0 0)` - Ratio 6.2:1 ✓
  - Accent Cyan `oklch(0.75 0.15 195)`: Dark text `oklch(0.15 0.02 260)` - Ratio 9.5:1 ✓
  - Card Slate `oklch(0.25 0.02 250)`: Light text `oklch(0.92 0 0)` - Ratio 11.4:1 ✓

## Font Selection

Typography should convey **technical precision** and **modern sophistication** - crisp, monospaced fonts for code and data paired with a clean geometric sans-serif for UI text, suggesting both scientific accuracy and contemporary design.

**Typographic Hierarchy**:
- H1 (App Title): "Space Grotesk" Bold / 32px / tight letter-spacing (-0.02em) / Purple gradient text
- H2 (Section Headers): "Space Grotesk" SemiBold / 24px / normal tracking / Cyan accent
- H3 (Component Labels): "Space Grotesk" Medium / 18px / normal / Light gray
- Body Text: "Inter" Regular / 15px / line-height 1.6 / Off-white
- Code: "JetBrains Mono" Regular / 14px / line-height 1.5 / Syntax highlighted
- Metrics/Data: "JetBrains Mono" Medium / 13px / tabular-nums / Cyan accent
- Buttons: "Space Grotesk" SemiBold / 15px / uppercase / tracking 0.05em

## Animations

Animations should emphasize **quantum state transitions**, **cognitive processing**, and **distributed agent collaboration** - superposition circles that pulse and converge during collapse, smooth metric updates that suggest real-time computation, animated token flows showing work distribution across paradigms, and subtle particle effects on interaction that reinforce the quantum theme. Balance includes: functional micro-interactions (200ms) for immediate feedback on buttons and inputs, dramatic centerpiece animations (500-800ms) for quantum visualizations, token transfers, and pipeline progress, network graph animations (1.5s) for paradigm connections appearing/disappearing, and ambient motion (2-4s loops) for idle state indicators suggesting active cognitive processing and energy flows between collaborating agents.

## Component Selection

- **Components**: 
  - `Card` with dark variant for all major sections (Code Editor, Metrics Panel, Quantum Visualizer)
  - `Textarea` for prompt input with character counter integration
  - `Button` with loading states for primary actions, icon variants for secondary actions
  - `Tabs` for navigation between Code, Memory, Agents, Physics sections
  - `Progress` for pipeline stages and loading states
  - `Table` for memory patterns and execution history
  - `Dialog` for file upload, settings, error details
  - `Badge` for status indicators (idle/active/error, cache hits)
  - `Tooltip` for metric explanations and help text
  - `Separator` for visual section breaks
  - Monaco Editor (external) for syntax-highlighted code display
- **Customizations**: 
  - Canvas-based quantum visualizer (no Shadcn equivalent)
  - Custom gradient header with animated particle background
  - WebGL physics simulator canvas
  - Split-pane diff viewer with synchronized scrolling
  - SVG-based collaboration graph with animated connections
  - Token flow stream with real-time updates and auto-scrolling
  - Circular network layout for paradigm visualization
- **States**: 
  - Buttons: default (purple gradient), hover (lighter + lift), active (pressed + scale 0.98), disabled (gray + reduced opacity), loading (spinner + pulse)
  - Inputs: default (subtle border), focus (cyan glow + border), error (red border + shake), success (green checkmark)
  - Cards: default (slate background), hover (subtle lift on interactive cards), active (cyan border for selected agents)
- **Icon Selection**: 
  - Phosphor Icons throughout: `Code`, `Brain`, `Lightning`, `Database`, `Atom`, `ChartLine`, `FileCode`, `Play`, `Stop`, `ArrowsClockwise`, `Check`, `X`, `Copy`, `Download`, `Upload`, `GitBranch`, `ArrowRight`, `Circle`, `CheckCircle`, `Plus`, `Sparkle`, `BookOpen`, `MagnifyingGlass`, `Package`, `Star`, `TrendUp`, `Link`, `Warning`
  - Emojis for agent types: 🤖 (workflow), ⚛️ (quantum), 🔬 (physics), 🔗 (collaboration)
  - Workflow tokens: 🔍 (audit), 📚 (docs), 🔧 (heal), ⚛️ (decide), 🗂️ (organize), ✅ (review)
  - Physics paradigms: 🌀 (chaos), 🔺 (fractal), 💧 (fluid), ⚡ (electromagnetic), 〰️ (wave), ⏰ (relativity)
  - Custom token icon picker: 20 emoji options (🚀, ⚡, 🔬, 🧬, 🔮, 🌟, 💎, 🎯, 🔥, 💫, 🌈, 🎨, 🔧, 🛠️, ⚙️, 🔍, 📊, 🎪, 🏆, 💡)
  - Template bundle categories: 🏗️ (full-stack dev), 🤖 (MLOps), 🔒 (security), ⚙️ (DevOps), ✨ (code quality), 📈 (analytics)
- **Spacing**: 
  - Container padding: `p-6` (24px) for cards, `p-8` (32px) for main sections
  - Component gaps: `gap-4` (16px) for related elements, `gap-6` (24px) for section separation
  - Button padding: `px-6 py-3` for primary, `px-4 py-2` for secondary
  - Grid gaps: `gap-4` for dense layouts (metrics), `gap-6` for breathing room (cards)
- **Mobile**: 
  - Single column layout <768px
  - Collapsible sidebar navigation becomes bottom tabs
  - Quantum visualizer canvas scales to screen width (min 320px)
  - Tables become vertically stacked cards with labels
  - Split diff view becomes tabbed (Original/Transformed toggle)
  - Reduced padding (p-4 instead of p-6)
  - Sticky header with hamburger menu
  - Touch-optimized buttons (min 44px touch targets)
