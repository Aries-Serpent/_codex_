"""
Interactive planning components for the audit dashboard.

This module provides HTML/CSS/JavaScript generation for interactive
planning features including phase selection, capability grouping,
and intelligent component dependency suggestions.
"""

import html as html_module
from typing import Any


def generate_planning_css() -> str:
    """Generate CSS for interactive planning section."""
    return """
        /* Interactive Planning Section */
        .planning-section {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 8px;
            padding: 25px;
            margin: 30px 0;
            border: 2px solid #0366d6;
        }
        
        .planning-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .planning-header h2 {
            margin: 0;
            color: #0366d6;
            font-size: 24px;
        }
        
        .planning-description {
            margin-bottom: 20px;
            padding: 15px;
            background: rgba(255,255,255,0.7);
            border-radius: 6px;
            color: #24292e;
        }
        
        .planning-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .planning-card {
            background: white;
            border-radius: 6px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #0366d6;
        }
        
        .planning-card.dependencies {
            border-left-color: #f97316;
            opacity: 0.95;
        }
        
        .planning-card h3 {
            font-size: 15px;
            margin-bottom: 12px;
            color: #24292e;
            border-bottom: 1px solid #e1e4e8;
            padding-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .checkbox-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
            max-height: 250px;
            overflow-y: auto;
        }
        
        .checkbox-item {
            display: flex;
            align-items: flex-start;
            gap: 8px;
            padding: 6px;
            border-radius: 4px;
            transition: background 0.2s;
            font-size: 13px;
        }
        
        .checkbox-item:hover {
            background: #f6f8fa;
        }
        
        .checkbox-item input[type="checkbox"] {
            width: 16px;
            height: 16px;
            cursor: pointer;
            margin-top: 2px;
            flex-shrink: 0;
        }
        
        .checkbox-item label {
            cursor: pointer;
            flex: 1;
            line-height: 1.4;
        }
        
        .checkbox-item .score {
            color: #586069;
            font-size: 11px;
        }
        
        .action-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 10px 20px;
            border-radius: 6px;
            border: none;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        
        .btn-primary {
            background: #0366d6;
            color: white;
        }
        
        .btn-primary:hover {
            background: #0256c7;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(3,102,214,0.3);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #218838;
        }
        
        .generated-prompt {
            background: #fff;
            border: 2px solid #28a745;
            border-radius: 6px;
            padding: 20px;
            margin-top: 20px;
            display: none;
        }
        
        .generated-prompt.show {
            display: block;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .generated-prompt h3 {
            color: #28a745;
            margin-bottom: 15px;
            font-size: 18px;
        }
        
        .generated-prompt pre {
            background: #f6f8fa;
            border: 1px solid #e1e4e8;
            border-radius: 4px;
            padding: 15px;
            overflow-x: auto;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 12px;
            line-height: 1.6;
            white-space: pre-wrap;
            max-height: 500px;
            overflow-y: auto;
        }
        
        .copy-button {
            background: #28a745;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            margin-top: 10px;
            transition: background 0.2s;
        }
        
        .copy-button:hover {
            background: #218838;
        }
        
        .copy-button.copied {
            background: #155724;
        }
        
        .dependency-note {
            background: #fff3cd;
            border-left: 3px solid #ffc107;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            font-size: 12px;
            color: #856404;
        }
"""


def generate_planning_javascript() -> str:
    """Generate JavaScript for interactive planning functionality."""
    return r"""
    <script>
        // Component dependency mapping
        const COMPONENT_DEPENDENCIES = {
            'detector': ['scripts/space_traversal/detectors/', 'tests/space_traversal/', 'docs/capabilities/'],
            'database': ['db/migrations/', 'src/codex_ml/db/', 'tests/db/'],
            'cli': ['src/codex_ml/cli.py', 'tests/cli/', 'docs/cli/'],
            'workflow': ['.github/workflows/', 'docs/ci-cd/'],
            'api': ['src/codex_ml/api/', 'tests/api/', 'docs/api/'],
            'tests': ['tests/', 'pytest.ini', '.coveragerc'],
            'docs': ['docs/', 'README.md', 'mkdocs.yml']
        };
        
        // Auto-update dependencies based on selections
        function updateDependencies() {
            const capabilities = Array.from(document.querySelectorAll('#capabilitySelection input:checked'))
                .map(cb => cb.value);
            const aspects = Array.from(document.querySelectorAll('#aspectSelection input:checked'))
                .map(cb => cb.value);
            
            // Auto-select related components
            const dependencies = new Set();
            
            capabilities.forEach(cap => {
                // Most capabilities need a detector
                if (cap.includes('detector') || cap.includes('lifecycle') || cap.includes('safeguards')) {
                    dependencies.add('detector');
                }
                // Database-related capabilities
                if (cap.includes('database') || cap.includes('store') || cap.includes('cache')) {
                    dependencies.add('database');
                }
                // CLI-related capabilities
                if (cap.includes('cli') || cap.includes('command')) {
                    dependencies.add('cli');
                }
            });
            
            // Based on aspects, suggest components
            if (aspects.includes('tests')) {
                dependencies.add('tests');
            }
            if (aspects.includes('documentation')) {
                dependencies.add('docs');
            }
            
            // Update UI to show suggestions
            updateDependencySuggestions(Array.from(dependencies));
        }
        
        function updateDependencySuggestions(suggestions) {
            const container = document.getElementById('dependencySuggestions');
            if (!container) return;
            
            if (suggestions.length === 0) {
                container.innerHTML = '<p style="color: #586069; font-style: italic;">Select capabilities to see component suggestions</p>';
                return;
            }
            
            let html = '';
            suggestions.forEach(component => {
                const paths = COMPONENT_DEPENDENCIES[component] || [];
                // Create safe ID using hash of component name to avoid XSS and selector issues
                const componentId = 'comp_' + Array.from(component).reduce((hash, char) => {
                    return ((hash << 5) - hash) + char.charCodeAt(0) | 0;
                }, 0).toString(36).replace('-', 'n');
                // Check if already selected using data attribute
                const existingCheckbox = document.querySelector(`input[data-component="${CSS.escape(component)}"]`);
                const checked = existingCheckbox?.checked ? 'checked' : '';
                // Escape component and paths for display
                const escapedComponent = sanitizeHTML(component);
                const escapedPaths = paths.slice(0, 2).map(p => sanitizeHTML(p)).join(', ');
                const moreText = paths.length > 2 ? '...' : '';
                
                html += `
                    <div class="checkbox-item">
                        <input type="checkbox" id="${componentId}" data-component="${sanitizeHTML(component)}" value="${escapedComponent}" ${checked} onchange="updateDependencies()">
                        <label for="${componentId}">
                            <strong>${escapedComponent}</strong>
                            <div class="score">Affects: ${escapedPaths}${moreText}</div>
                        </label>
                    </div>
                `;
            });
            container.innerHTML = html;
        }
        
        // Sanitize HTML to prevent XSS
        function sanitizeHTML(str) {
            if (typeof str !== 'string') return '';
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }
        
        function generateNextSteps() {
            // Gather and sanitize selections
            const phases = Array.from(document.querySelectorAll('#phaseSelection input:checked'))
                .map(cb => sanitizeHTML(cb.value));
            const capabilities = Array.from(document.querySelectorAll('#capabilitySelection input:checked'))
                .map(cb => sanitizeHTML(cb.value));
            const aspects = Array.from(document.querySelectorAll('#aspectSelection input:checked'))
                .map(cb => sanitizeHTML(cb.value));
            const components = Array.from(document.querySelectorAll('#componentSelection input:checked'))
                .map(cb => sanitizeHTML(cb.value));
            
            if (phases.length === 0 && capabilities.length === 0) {
                alert('Please select at least one phase or capability');
                return;
            }
            
            // Generate prompt
            let prompt = `# Next Steps: Capability Improvement Plan\\n\\n`;
            prompt += `**Generated**: ${new Date().toISOString().split('T')[0]}\\n`;
            prompt += `**Objective**: Improve selected capabilities to high maturity (≥0.85)\\n\\n`;
            
            if (phases.length > 0) {
                prompt += `## Selected Phases\\n`;
                phases.forEach(phase => {
                    prompt += `- ${phase}\\n`;
                });
                prompt += `\\n`;
            }
            
            if (capabilities.length > 0) {
                prompt += `## Target Capabilities\\n`;
                capabilities.forEach(cap => {
                    prompt += `- ${cap}\\n`;
                });
                prompt += `\\n`;
            }
            
            if (aspects.length > 0) {
                prompt += `## Focus Aspects\\n`;
                aspects.forEach(aspect => {
                    prompt += `- ${aspect.charAt(0).toUpperCase() + aspect.slice(1)}\\n`;
                });
                prompt += `\\n`;
            }
            
            if (components.length > 0) {
                prompt += `## Components to Update\\n`;
                components.forEach(component => {
                    const paths = COMPONENT_DEPENDENCIES[component] || [];
                    prompt += `### ${component.charAt(0).toUpperCase() + component.slice(1)}\\n`;
                    paths.forEach(path => {
                        prompt += `- \`${path}\`\\n`;
                    });
                });
                prompt += `\\n`;
            }
            
            prompt += `## Execution Steps\\n\\n`;
            prompt += `For each selected capability:\\n\\n`;
            
            if (aspects.includes('functionality')) {
                prompt += `1. **Implement Functionality**\\n`;
                prompt += `   - Add missing functions and features\\n`;
                prompt += `   - Ensure all required patterns are present\\n`;
                prompt += `   - Target functionality score: 1.0\\n\\n`;
            }
            
            if (aspects.includes('tests')) {
                prompt += `2. **Create Comprehensive Tests**\\n`;
                prompt += `   - Write unit tests (target: 15+ test cases per capability)\\n`;
                prompt += `   - Add integration tests\\n`;
                prompt += `   - Test edge cases and error handling\\n`;
                prompt += `   - Target test score: 0.85+\\n\\n`;
            }
            
            if (aspects.includes('documentation')) {
                prompt += `3. **Write Documentation**\\n`;
                prompt += `   - Create capability-specific docs\\n`;
                prompt += `   - Add usage examples\\n`;
                prompt += `   - Include keywords for detector recognition\\n`;
                prompt += `   - Target documentation score: 0.85+\\n\\n`;
            }
            
            if (aspects.includes('safeguards')) {
                prompt += `4. **Add Safeguards**\\n`;
                prompt += `   - Input validation and bounds checking\\n`;
                prompt += `   - Error handling and graceful degradation\\n`;
                prompt += `   - Add safeguard keywords in comments\\n`;
                prompt += `   - Target safeguards score: 0.85+\\n\\n`;
            }
            
            if (aspects.includes('consistency')) {
                prompt += `5. **Ensure Consistency**\\n`;
                prompt += `   - Follow repository coding standards\\n`;
                prompt += `   - Use consistent naming conventions\\n`;
                prompt += `   - Maintain deterministic behavior\\n`;
                prompt += `   - Target consistency score: 0.85+\\n\\n`;
            }
            
            prompt += `## Validation\\n\\n`;
            prompt += `After implementation:\\n`;
            prompt += `1. Run audit: \`python scripts/space_traversal/audit_runner.py run\`\\n`;
            prompt += `2. Verify scores: Check \`audit_artifacts/capabilities_scored.json\`\\n`;
            prompt += `3. Confirm all selected capabilities reach ≥0.85\\n`;
            prompt += `4. Review evidence files for completeness\\n\\n`;
            
            prompt += `## Expected Outcomes\\n\\n`;
            if (capabilities.length > 0) {
                prompt += `- ${capabilities.length} capabilities improved to high maturity\\n`;
            }
            prompt += `- All selected aspects score ≥0.85\\n`;
            prompt += `- Comprehensive test coverage added\\n`;
            prompt += `- Complete documentation in place\\n`;
            prompt += `- Repository maturity increased\\n`;
            
            // Display prompt
            document.getElementById('promptContent').textContent = prompt;
            document.getElementById('generatedPrompt').classList.add('show');
            document.getElementById('generatedPrompt').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        
        function resetSelections() {
            document.querySelectorAll('.checkbox-item input[type="checkbox"]').forEach(cb => {
                cb.checked = false;
            });
            document.getElementById('generatedPrompt').classList.remove('show');
            updateDependencies();
        }
        
        function copyPrompt() {
            const content = document.getElementById('promptContent').textContent;
            navigator.clipboard.writeText(content).then(() => {
                const btn = event.target;
                btn.textContent = '✅ Copied!';
                btn.classList.add('copied');
                setTimeout(() => {
                    btn.textContent = '📋 Copy to Clipboard';
                    btn.classList.remove('copied');
                }, 2000);
            }).catch(err => {
                alert('Failed to copy: ' + err);
            });
        }
        
        // Add event listeners after page loads
        document.addEventListener('DOMContentLoaded', function() {
            // Auto-update dependencies when selections change
            document.querySelectorAll('#capabilitySelection input, #aspectSelection input').forEach(cb => {
                cb.addEventListener('change', updateDependencies);
            });
            
            // Initial update
            updateDependencies();
        });
    </script>
"""


def generate_planning_html(gaps_and_plans: dict[str, Any]) -> str:
    """Generate interactive planning HTML section."""
    if not gaps_and_plans or not (gaps_and_plans.get("gaps") or gaps_and_plans.get("plans")):
        return ""
    
    gaps = gaps_and_plans.get("gaps", {})
    plans = gaps_and_plans.get("plans", {})
    phases = plans.get("phases", [])
    low_maturity = gaps.get("low_maturity", [])
    
    html = """
        <div class="planning-section">
            <div class="planning-header">
                <h2>🎯 Interactive Planning Tool</h2>
            </div>
            <div class="planning-description">
                <strong>Craft Your Next Steps:</strong> Select phases, capabilities, and aspects to generate a customized improvement plan. 
                The tool will automatically suggest related components (detectors, database, CLI, etc.) based on your selections.
            </div>
            
            <div class="planning-grid">
                <!-- Phase Selection -->
                <div class="planning-card">
                    <h3>📅 Select Phases</h3>
                    <div class="checkbox-group" id="phaseSelection">
"""
    
    # Add phase checkboxes
    if phases:
        for i, phase in enumerate(phases[:5], 1):
            escaped_phase = html_module.escape(phase)
            phase_id = f"phase{i}"
            checked = ' checked' if i == 1 else ''
            html += f"""                        <div class="checkbox-item">
                            <input type="checkbox" id="{phase_id}" value="{escaped_phase}"{checked}>
                            <label for="{phase_id}">{escaped_phase}</label>
                        </div>
"""
    else:
        html += """                        <div class="checkbox-item">
                            <input type="checkbox" id="phase1" value="Phase 1" checked>
                            <label for="phase1">Phase 1: Low to Medium Maturity</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="phase2" value="Phase 2">
                            <label for="phase2">Phase 2: Medium to High Maturity</label>
                        </div>
"""
    
    html += """                    </div>
                </div>
                
                <!-- Capability Selection -->
                <div class="planning-card">
                    <h3>🎯 Low Maturity Capabilities</h3>
                    <div class="checkbox-group" id="capabilitySelection">
"""
    
    # Add capability checkboxes
    if low_maturity:
        for i, cap in enumerate(low_maturity[:12], 1):
            cap_id = cap.get("explain", {}).get("id", f"cap{i}")
            cap_score = cap.get("explain", {}).get("score", 0)
            components_info = cap.get("components", {})
            
            # Create tooltip showing component scores
            tooltip_parts = []
            for comp_name, score in components_info.items():
                if score < 0.85:
                    tooltip_parts.append(f"{comp_name}: {score:.2f}")
            tooltip = " | ".join(tooltip_parts[:3])
            
            escaped_id = html_module.escape(str(cap_id))
            escaped_display = html_module.escape(cap_id)
            escaped_tooltip = html_module.escape(tooltip) if tooltip else ""
            
            html += f"""                        <div class="checkbox-item">
                            <input type="checkbox" id="cap_{i}" value="{escaped_id}" onchange="updateDependencies()">
                            <label for="cap_{i}">
                                {escaped_display}
                                <div class="score">Score: {cap_score:.2f} | {escaped_tooltip}</div>
                            </label>
                        </div>
"""
    else:
        html += """                        <p style="color: #586069; font-style: italic; padding: 10px;">
                            No low maturity capabilities found. All capabilities are performing well!
                        </p>
"""
    
    html += """                    </div>
                </div>
                
                <!-- Aspect Selection -->
                <div class="planning-card">
                    <h3>🔧 Focus Aspects</h3>
                    <div class="checkbox-group" id="aspectSelection">
                        <div class="checkbox-item">
                            <input type="checkbox" id="aspect_tests" value="tests" checked onchange="updateDependencies()">
                            <label for="aspect_tests">Tests & Coverage</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="aspect_docs" value="documentation" checked onchange="updateDependencies()">
                            <label for="aspect_docs">Documentation</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="aspect_functionality" value="functionality" onchange="updateDependencies()">
                            <label for="aspect_functionality">Functionality</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="aspect_safeguards" value="safeguards" onchange="updateDependencies()">
                            <label for="aspect_safeguards">Safeguards</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="aspect_consistency" value="consistency" onchange="updateDependencies()">
                            <label for="aspect_consistency">Consistency</label>
                        </div>
                    </div>
                </div>
                
                <!-- Component Dependencies (Auto-suggested) -->
                <div class="planning-card dependencies">
                    <h3>🔗 Related Components</h3>
                    <div class="dependency-note">
                        💡 Auto-suggested based on your selections
                    </div>
                    <div class="checkbox-group" id="componentSelection">
                        <div id="dependencySuggestions">
                            <p style="color: #586069; font-style: italic;">Select capabilities to see component suggestions</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="generateNextSteps()">
                    ✨ Generate Next Steps Prompt
                </button>
                <button class="btn btn-secondary" onclick="resetSelections()">
                    🔄 Reset Selections
                </button>
                <button class="btn btn-success" onclick="window.print()">
                    🖨️ Print Dashboard
                </button>
            </div>
            
            <div class="generated-prompt" id="generatedPrompt">
                <h3>📋 Generated Next Steps Prompt</h3>
                <pre id="promptContent"></pre>
                <button class="copy-button" onclick="copyPrompt()">📋 Copy to Clipboard</button>
            </div>
        </div>
"""
    
    return html
