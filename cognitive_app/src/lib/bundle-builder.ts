/**
 * Bundle Builder Framework - Mathematical Foundation Implementation
 * 
 * Based on energy-based optimization with explicit completeness guarantees.
 * Implements the bundle-as-state-vector model with UI projection operators.
 * 
 * Core equation: |B*⟩ = argmin_{|B⟩∈Ω} E(B)
 * Completeness: M̂_complete · M̂_map · M̂_src = 1
 * UI Projection: |C⟩ = P̂_UI |B⟩
 */

// ============================================================================
// TYPE DEFINITIONS - Bundle State Vector Components
// ============================================================================

/**
 * Agent configuration subspace |A⟩
 */
export interface AgentConfig {
  name: string;
  description: string;
  instructions: string;
  template: 'none' | 'research' | 'code' | 'data' | 'custom';
  capabilities: {
    create_documents_charts_code: boolean;
    create_images: boolean;
  };
}

/**
 * Knowledge configuration subspace |K⟩
 */
export interface KnowledgeConfig {
  specified_websites: string[];
  search_all_websites: boolean;
  only_use_specified_sources: boolean;
  reference_people_in_org: boolean;
  tie_break_rule: 'strict_over_web' | 'web_when_asked' | 'web_allowed';
}

/**
 * Suggested prompts subspace |P⟩
 */
export interface PromptConfig {
  title: string;
  message: string;
}

/**
 * Test suite subspace |T⟩
 */
export interface TestSuite {
  source_only: string[];
  format_contract: string[];
  abstention: string[];
  capabilities: string[];
}

/**
 * GUI state subspace |G⟩
 */
export interface GUIState {
  tabs: string[];
  preview: {
    show_ui_projection: boolean;
    show_measurements: boolean;
  };
  export: {
    format: 'zip' | 'json';
    include_manifest: boolean;
  };
}

/**
 * Complete bundle state vector |B⟩ = |A⟩ ⊕ |K⟩ ⊕ |P⟩ ⊕ |T⟩ ⊕ |G⟩
 */
export interface BundleState {
  bundle_version: string;
  agent: AgentConfig;
  knowledge: KnowledgeConfig;
  suggested_prompts: PromptConfig[];
  tests: TestSuite;
  gui: GUIState;
}

/**
 * Requirements state |R⟩ for entropy reduction
 */
export interface Requirements {
  domain: string;
  outputs: string[];
  sources: string[];
  tone: string;
  constraints: string[];
}

/**
 * Energy components for E(B) computation
 */
export interface EnergyComponents {
  missing: number;      // λ_miss · L_missing(B)
  ui_map: number;       // λ_map · L_ui_map(B)
  source: number;       // λ_src · L_source(B)
  format: number;       // λ_fmt · L_format(B)
  test_fail: number;    // λ_test · L_test_fail(B)
  utility: number;      // -λ_util · R_utility(B)
  total: number;
}

/**
 * Create Agent UI field mapping (UI projection output)
 */
export interface CreateAgentConfig {
  name: string;
  description: string;
  instructions: string;
  template: string;
  specified_websites: string[];
  search_all_websites: boolean;
  only_use_specified_sources: boolean;
  reference_people_in_org: boolean;
  create_documents_charts_code: boolean;
  create_images: boolean;
  suggested_prompts: Array<{ title: string; message: string }>;
}

// ============================================================================
// BUNDLE BUILDER - Core Optimization Engine
// ============================================================================

/**
 * BundleBuilder implements energy-based optimization for agent bundle creation.
 * 
 * Mathematical foundation:
 * 1. Bundle as state vector in Hilbert space H_B
 * 2. Energy minimization: find |B*⟩ = argmin E(B)
 * 3. Measurement operators for validation
 * 4. UI projection for installability
 */
export class BundleBuilder {
  // Energy weights (λ coefficients)
  private weights = {
    missing: 1.0,
    ui_map: 0.8,
    source: 0.7,
    format: 0.6,
    test_fail: 0.5,
    utility: 0.3,
  };

  // =========================================================================
  // ENERGY COMPUTATION - E(B) = Σ λᵢ·Lᵢ - λ_util·R_utility
  // =========================================================================

  /**
   * Compute total energy E(B) for a bundle state
   */
  computeEnergy(bundle: BundleState): EnergyComponents {
    const missing = this.computeMissingLoss(bundle);
    const ui_map = this.computeUIMapLoss(bundle);
    const source = this.computeSourceLoss(bundle);
    const format = this.computeFormatLoss(bundle);
    const test_fail = this.computeTestFailLoss(bundle);
    const utility = this.computeUtilityReward(bundle);

    const total =
      this.weights.missing * missing +
      this.weights.ui_map * ui_map +
      this.weights.source * source +
      this.weights.format * format +
      this.weights.test_fail * test_fail -
      this.weights.utility * utility;

    return { missing, ui_map, source, format, test_fail, utility, total };
  }

  /**
   * L_missing(B) = Σ 1_{c_i ⊄ B} for required components c_i ∈ C
   */
  private computeMissingLoss(bundle: BundleState): number {
    let loss = 0;

    // Check required agent fields
    if (!bundle.agent.name) loss++;
    if (!bundle.agent.description) loss++;
    if (!bundle.agent.instructions) loss++;

    // Check minimum suggested prompts (require at least 2)
    if (bundle.suggested_prompts.length < 2) loss++;

    // Check knowledge configuration coherence
    if (
      bundle.knowledge.only_use_specified_sources &&
      bundle.knowledge.specified_websites.length === 0
    ) {
      loss++;
    }

    return loss;
  }

  /**
   * L_ui_map(B) = Σ d(Φ_f(B), f) for UI fields f ∈ F
   */
  private computeUIMapLoss(bundle: BundleState): number {
    let loss = 0;

    // Check name length constraints (UI typically has limits)
    if (bundle.agent.name.length > 100) loss += 0.5;
    if (bundle.agent.description.length > 500) loss += 0.5;

    // Check instructions formatting
    if (bundle.agent.instructions.length < 50) loss += 0.3;
    if (bundle.agent.instructions.length > 5000) loss += 0.7;

    // Check suggested prompts validity
    for (const prompt of bundle.suggested_prompts) {
      if (!prompt.title || prompt.title.length === 0) loss += 0.2;
      if (!prompt.message || prompt.message.length === 0) loss += 0.2;
    }

    return loss;
  }

  /**
   * L_source(B) = 1_{g_spec=1 ∧ |S_spec|=0} + 1_{conflict}
   */
  private computeSourceLoss(bundle: BundleState): number {
    let loss = 0;

    const { only_use_specified_sources, specified_websites, search_all_websites } =
      bundle.knowledge;

    // Strict sources without any specified = invalid
    if (only_use_specified_sources && specified_websites.length === 0) {
      loss += 1.0;
    }

    // Strict sources + search all websites = conflict (unless tie-break defined)
    if (
      only_use_specified_sources &&
      search_all_websites &&
      !bundle.agent.instructions.includes('tie-break')
    ) {
      loss += 0.8;
    }

    return loss;
  }

  /**
   * L_format(B) - Format compliance loss
   */
  private computeFormatLoss(bundle: BundleState): number {
    let loss = 0;

    // Check if instructions mention output format when needed
    const needsFormat =
      bundle.agent.capabilities.create_documents_charts_code ||
      bundle.tests.format_contract.length > 0;

    if (needsFormat && !bundle.agent.instructions.toLowerCase().includes('format')) {
      loss += 0.5;
    }

    return loss;
  }

  /**
   * L_test_fail(B) - Test validation loss
   */
  private computeTestFailLoss(bundle: BundleState): number {
    let loss = 0;

    // Penalize if source-only tests but no source constraints
    if (
      bundle.tests.source_only.length > 0 &&
      !bundle.knowledge.only_use_specified_sources
    ) {
      loss += 0.3;
    }

    // Penalize if capability tests but capabilities not enabled
    if (bundle.tests.capabilities.length > 0) {
      const capsEnabled =
        bundle.agent.capabilities.create_documents_charts_code ||
        bundle.agent.capabilities.create_images;
      if (!capsEnabled) loss += 0.4;
    }

    return loss;
  }

  /**
   * R_utility(B) - Utility reward (negative loss)
   */
  private computeUtilityReward(bundle: BundleState): number {
    let reward = 0;

    // Reward for comprehensive instructions
    if (bundle.agent.instructions.length > 200) reward += 0.3;

    // Reward for good prompt coverage
    if (bundle.suggested_prompts.length >= 3) reward += 0.2;

    // Reward for test coverage
    const totalTests =
      bundle.tests.source_only.length +
      bundle.tests.format_contract.length +
      bundle.tests.abstention.length +
      bundle.tests.capabilities.length;
    if (totalTests >= 4) reward += 0.4;

    return reward;
  }

  // =========================================================================
  // MEASUREMENT OPERATORS - M̂ for validation
  // =========================================================================

  /**
   * M̂_complete(B) = 1 if L_missing(B) = 0, else 0
   */
  measureCompleteness(bundle: BundleState): 0 | 1 {
    return this.computeMissingLoss(bundle) === 0 ? 1 : 0;
  }

  /**
   * M̂_map(B) = 1 if P̂_UI|B⟩ is well-formed
   */
  measureUIMapping(bundle: BundleState): 0 | 1 {
    try {
      const projected = this.projectToUI(bundle);
      return projected && projected.name.length > 0 ? 1 : 0;
    } catch {
      return 0;
    }
  }

  /**
   * M̂_src(B) = 1 if L_source(B) = 0
   */
  measureSourceCoherence(bundle: BundleState): 0 | 1 {
    return this.computeSourceLoss(bundle) === 0 ? 1 : 0;
  }

  /**
   * Overall validity: M̂_complete · M̂_map · M̂_src = 1
   */
  measureValidity(bundle: BundleState): boolean {
    return (
      this.measureCompleteness(bundle) === 1 &&
      this.measureUIMapping(bundle) === 1 &&
      this.measureSourceCoherence(bundle) === 1
    );
  }

  // =========================================================================
  // UI PROJECTION OPERATOR - P̂_UI: H_B → H_CreateAgent
  // =========================================================================

  /**
   * Project bundle state to Create Agent UI configuration
   * |C⟩ = P̂_UI |B⟩
   */
  projectToUI(bundle: BundleState): CreateAgentConfig {
    return {
      name: bundle.agent.name,
      description: bundle.agent.description,
      instructions: bundle.agent.instructions,
      template: bundle.agent.template,
      specified_websites: bundle.knowledge.specified_websites,
      search_all_websites: bundle.knowledge.search_all_websites,
      only_use_specified_sources: bundle.knowledge.only_use_specified_sources,
      reference_people_in_org: bundle.knowledge.reference_people_in_org,
      create_documents_charts_code: bundle.agent.capabilities.create_documents_charts_code,
      create_images: bundle.agent.capabilities.create_images,
      suggested_prompts: bundle.suggested_prompts,
    };
  }

  // =========================================================================
  // OPTIMIZATION LOOP - Find |B*⟩ = argmin E(B)
  // =========================================================================

  /**
   * Optimize bundle from requirements through iterative energy minimization
   * 
   * Algorithm:
   * 1. Generate initial bundle |B₀⟩ from requirements |R⟩
   * 2. Compute energy E(B_t)
   * 3. If E(B_t) < ε and measurements pass, done
   * 4. Otherwise, find highest ΔE repair and apply
   * 5. Repeat from step 2
   */
  async optimizeBundle(
    requirements: Requirements,
    maxIterations: number = 10,
    energyThreshold: number = 0.1
  ): Promise<BundleState> {
    // Step 1: Initial synthesis
    let bundle = this.generateInitialBundle(requirements);

    // Step 2-5: Iterative repair
    for (let iteration = 0; iteration < maxIterations; iteration++) {
      const energy = this.computeEnergy(bundle);

      // Check termination
      if (energy.total < energyThreshold && this.measureValidity(bundle)) {
        console.log(`Converged in ${iteration} iterations, E=${energy.total.toFixed(3)}`);
        return bundle;
      }

      // Find and apply best repair
      bundle = this.repairBundle(bundle, energy);
    }

    console.warn(`Max iterations reached, final E=${this.computeEnergy(bundle).total.toFixed(3)}`);
    return bundle;
  }

  /**
   * Generate initial bundle from requirements (fast prior)
   */
  private generateInitialBundle(req: Requirements): BundleState {
    return {
      bundle_version: '1.0',
      agent: {
        name: `${req.domain} Agent`,
        description: `Agent for ${req.domain} with ${req.outputs.join(', ')} capabilities`,
        instructions: `Mission: ${req.outputs.join(', ')}.\nTone: ${req.tone}.\nConstraints: ${req.constraints.join(', ')}.`,
        template: 'none',
        capabilities: {
          create_documents_charts_code: req.outputs.includes('documents'),
          create_images: req.outputs.includes('images'),
        },
      },
      knowledge: {
        specified_websites: req.sources,
        search_all_websites: req.sources.length === 0,
        only_use_specified_sources: req.sources.length > 0,
        reference_people_in_org: false,
        tie_break_rule: 'strict_over_web',
      },
      suggested_prompts: [
        {
          title: `${req.domain} query`,
          message: `Using available sources, provide ${req.outputs[0] || 'analysis'}.`,
        },
      ],
      tests: {
        source_only: [],
        format_contract: [],
        abstention: [],
        capabilities: [],
      },
      gui: {
        tabs: ['Describe', 'Configure', 'Preview', 'Export'],
        preview: { show_ui_projection: true, show_measurements: true },
        export: { format: 'json', include_manifest: true },
      },
    };
  }

  /**
   * Apply highest-ΔE repair to bundle
   */
  private repairBundle(bundle: BundleState, energy: EnergyComponents): BundleState {
    const repairs: Array<() => BundleState> = [];

    // Repair missing components
    if (energy.missing > 0) {
      if (!bundle.agent.name) {
        repairs.push(() => ({ ...bundle, agent: { ...bundle.agent, name: 'New Agent' } }));
      }
      if (bundle.suggested_prompts.length < 2) {
        repairs.push(() => ({
          ...bundle,
          suggested_prompts: [
            ...bundle.suggested_prompts,
            { title: 'Example query', message: 'Provide example output.' },
          ],
        }));
      }
      if (
        bundle.knowledge.only_use_specified_sources &&
        bundle.knowledge.specified_websites.length === 0
      ) {
        repairs.push(() => ({
          ...bundle,
          knowledge: { ...bundle.knowledge, only_use_specified_sources: false },
        }));
      }
    }

    // Apply first available repair (greedy)
    if (repairs.length > 0) {
      return repairs[0]();
    }

    return bundle;
  }

  // =========================================================================
  // EXPORT / IMPORT
  // =========================================================================

  /**
   * Export bundle as JSON manifest
   */
  exportManifest(bundle: BundleState): string {
    return JSON.stringify(bundle, null, 2);
  }

  /**
   * Import bundle from JSON manifest
   */
  importManifest(json: string): BundleState {
    return JSON.parse(json) as BundleState;
  }
}

// ============================================================================
// FACTORY FUNCTIONS
// ============================================================================

/**
 * Create bundle builder with custom energy weights
 */
export function createBundleBuilder(customWeights?: Partial<typeof BundleBuilder.prototype.weights>): BundleBuilder {
  const builder = new BundleBuilder();
  if (customWeights) {
    Object.assign(builder['weights'], customWeights);
  }
  return builder;
}

/**
 * Create empty bundle template
 */
export function createEmptyBundle(): BundleState {
  return {
    bundle_version: '1.0',
    agent: {
      name: '',
      description: '',
      instructions: '',
      template: 'none',
      capabilities: {
        create_documents_charts_code: false,
        create_images: false,
      },
    },
    knowledge: {
      specified_websites: [],
      search_all_websites: false,
      only_use_specified_sources: false,
      reference_people_in_org: false,
      tie_break_rule: 'strict_over_web',
    },
    suggested_prompts: [],
    tests: {
      source_only: [],
      format_contract: [],
      abstention: [],
      capabilities: [],
    },
    gui: {
      tabs: ['Describe', 'Configure', 'Preview', 'Export'],
      preview: { show_ui_projection: true, show_measurements: true },
      export: { format: 'json', include_manifest: true },
    },
  };
}
