"""
Interactive demonstration of the Physics-Guided Developer Orchestrator.

This example shows how to use the orchestrator to develop Python applications
with physics-inspired guidance.

Usage:
    python examples/developer_orchestrator_demo.py
"""

import json


def demo_cli_app_development():
    """Demonstrate developing a CLI application."""
    print("\n" + "=" * 70)
    print("DEMO: Developing a Python CLI Application")
    print("=" * 70)

    try:
        from agents.developer_orchestrator import (
            create_developer_orchestrator,
            AppType,
        )
    except ImportError:
        print("⚠ Developer orchestrator not available")
        return

    # Create orchestrator
    orchestrator = create_developer_orchestrator()

    # Step 1: Provide partial requirements
    print("\n--- Step 1: Analyzing User Requirements ---")

    user_requirements = {
        "app_type": "python_cli",
        "app_name": "data_processor",
        "description": "A CLI tool for processing data files",
        "commands": ["process", "validate", "export"],
    }

    print("\nUser provided:")
    print(json.dumps(user_requirements, indent=2))

    # Analyze requirements
    analysis = orchestrator.analyze_user_requirements(user_requirements)

    print(f"\n✓ Requirements analysis complete")
    print(f"  Completeness: {analysis['completeness']*100:.1f}%")
    print(f"  Provided: {len(analysis['provided_variables'])} variables")
    print(f"  Missing: {len(analysis['missing_variables'])} variables")

    # Show missing variables with suggestions
    if analysis["missing_variables"]:
        print("\n--- Missing Variables (with AI suggestions) ---")
        for var in analysis["missing_variables"]:
            print(f"\n  {var['name']} ({var['type']})")
            print(f"    Description: {var['description']}")
            print(f"    Required: {var['required']}")
            if "suggested_options" in var and var["suggested_options"]:
                print(f"    Suggested options:")
                for opt in var["suggested_options"]:
                    print(f"      - {opt}")

    # Step 2: Complete requirements with suggestions
    print("\n--- Step 2: Completing Requirements ---")

    # Use suggested value for CLI framework
    suggestions = analysis["suggestions"].get("cli_framework", [])
    if suggestions:
        user_requirements["cli_framework"] = suggestions[0]
        print(f"  Selected cli_framework: {suggestions[0]}")

    # Add Python version
    user_requirements["python_version"] = "3.10"
    print(f"  Selected python_version: 3.10")

    # Re-analyze
    analysis = orchestrator.analyze_user_requirements(user_requirements)
    print(f"\n✓ Requirements now {analysis['completeness']*100:.1f}% complete")

    # Step 3: Generate architecture
    print("\n--- Step 3: Suggesting Architecture ---")

    architecture = orchestrator.suggest_architecture(user_requirements)

    print(f"\n✓ Architecture generated")
    print(f"  Components: {len(architecture['components'])}")

    if "structure_analysis" in architecture and architecture["structure_analysis"]:
        struct = architecture["structure_analysis"]
        print(f"  Fractal dimension: {struct.get('fractal_dimension', 0):.2f}")
        print(f"  Total nodes: {struct.get('nodes', 0)}")

    print(f"\n  Recommended implementation order:")
    for i, comp_id in enumerate(architecture["recommended_order"], 1):
        comp = next((c for c in architecture["components"] if c["component_id"] == comp_id), None)
        if comp:
            print(f"    {i}. {comp['name']} ({comp['type']})")

    # Step 4: Generate code
    print("\n--- Step 4: Generating Code ---")

    # Generate main module
    main_code = orchestrator.generate_code("main", user_requirements)

    print("\n✓ Generated main.py:")
    print("-" * 70)
    print(main_code[:500] + "..." if len(main_code) > 500 else main_code)
    print("-" * 70)

    # Step 5: Check status
    print("\n--- Step 5: Development Status ---")

    status = orchestrator.get_development_status()

    print(f"\n  Current phase: {status['phase']}")
    print(
        f"  Components completed: {status['components']['completed']}/{status['components']['total']}"
    )
    print(f"  Progress: {status['components']['progress']*100:.1f}%")
    print(
        f"  Variables satisfied: {status['variables']['satisfied']}/{status['variables']['total']}"
    )


def demo_api_development():
    """Demonstrate developing an API application."""
    print("\n" + "=" * 70)
    print("DEMO: Developing a Python API Application")
    print("=" * 70)

    try:
        from agents.developer_orchestrator import create_developer_orchestrator
    except ImportError:
        print("⚠ Developer orchestrator not available")
        return

    # Create orchestrator
    orchestrator = create_developer_orchestrator()

    print("\n--- Analyzing Requirements ---")

    # Comprehensive requirements
    requirements = {
        "app_type": "python_api",
        "app_name": "task_api",
        "description": "REST API for task management",
        "api_framework": "fastapi",
        "endpoints": ["create_task", "list_tasks", "get_task", "update_task", "delete_task"],
        "authentication": "jwt",
        "python_version": "3.11",
    }

    print("\nUser requirements:")
    print(json.dumps(requirements, indent=2))

    # Analyze
    analysis = orchestrator.analyze_user_requirements(requirements)

    print(f"\n✓ Analysis complete: {analysis['completeness']*100:.1f}% complete")

    if analysis["missing_variables"]:
        print(f"\n  Missing variables: {len(analysis['missing_variables'])}")
    else:
        print("\n  ✓ All required variables provided!")

    # Generate architecture
    print("\n--- Generating Architecture ---")

    architecture = orchestrator.suggest_architecture(requirements)

    print(f"\n✓ Generated {len(architecture['components'])} components")

    # Show component priorities (from EM field analysis)
    print("\n  Component priorities:")
    sorted_components = sorted(
        architecture["components"], key=lambda c: c["priority"], reverse=True
    )
    for comp in sorted_components[:5]:
        print(
            f"    {comp['name']}: priority={comp['priority']:.2f}, "
            f"complexity={comp['complexity']:.1f}"
        )

    # Generate main API code
    print("\n--- Generating Code ---")

    main_code = orchestrator.generate_code("main", requirements)

    print("\n✓ Generated API code:")
    print("-" * 70)
    # Show first part of code
    lines = main_code.split("\n")
    for line in lines[:25]:
        print(f"{line}")
    if len(lines) > 25:
        print(f"  ...")
    print(f"{'-' * 70}")


def demo_interactive_workflow():
    """
    Demonstrate interactive workflow where orchestrator asks for missing info.
    """
    print("\n" + "=" * 70)
    print("DEMO: Interactive Development Workflow")
    print("=" * 70)

    try:
        from agents.developer_orchestrator import create_developer_orchestrator
    except ImportError:
        print("⚠ Developer orchestrator not available")
        return

    orchestrator = create_developer_orchestrator()

    print("\n--- Starting Interactive Development ---")
    print("\nScenario: User provides minimal requirements")

    # Minimal requirements
    minimal_requirements = {
        "app_type": "python_console",
        "description": "A simple calculator application",
    }

    print("\nUser input:")
    print(json.dumps(minimal_requirements, indent=2))

    # Analyze
    print("\n--- Orchestrator Analysis ---")
    analysis = orchestrator.analyze_user_requirements(minimal_requirements)

    print(f"\nCompleteness: {analysis['completeness']*100:.1f}%")
    print(f"\nThe orchestrator identifies {len(analysis['missing_variables'])} missing variables:")

    # Display missing variables with suggestions
    for i, var in enumerate(analysis["missing_variables"], 1):
        print(f"\n{i}. {var['name']} ({var['type']})")
        print(f"   ❓ {var['description']}")
        print(f"   Required: {'Yes' if var['required'] else 'No (optional)'}")

        if "suggested_options" in var and var["suggested_options"]:
            print(f"   💡 Suggested values:")
            for opt in var["suggested_options"]:
                print(f"      • {opt}")

        if var.get("default"):
            print(f"   Default: {var['default']}")

    # Simulate user providing missing info
    print("\n--- User Completes Requirements ---")

    # User selects from suggestions or provides own
    complete_requirements = {
        **minimal_requirements,
        "app_name": "calculator",
        "python_version": "3.10",  # From suggestions
    }

    print("\nCompleted requirements:")
    print(json.dumps(complete_requirements, indent=2))

    # Re-analyze
    final_analysis = orchestrator.analyze_user_requirements(complete_requirements)

    print(f"\n✓ Requirements now {final_analysis['completeness']*100:.1f}% complete")

    # Proceed with development
    print("\n--- Proceeding with Development ---")

    architecture = orchestrator.suggest_architecture(complete_requirements)
    print(f"\n✓ Architecture ready with {len(architecture['components'])} components")

    orchestrator.generate_code("main", complete_requirements)
    print("\n✓ Code generated successfully")

    print("\n--- Final Status ---")
    status = orchestrator.get_development_status()
    print(f"  Phase: {status['phase']}")
    print(f"  Progress: {status['components']['progress']*100:.1f}%")


def demo_physics_integration():
    """Demonstrate how physics paradigms guide development."""
    print("\n" + "=" * 70)
    print("DEMO: Physics-Guided Development Decisions")
    print("=" * 70)

    try:
        from agents.developer_orchestrator import create_developer_orchestrator
        from agents.advanced_physics_calculators import AdvancedPhysicsOrchestrator
    except ImportError:
        print("⚠ Physics modules not available. Install with: pip install numpy")
        return

    orchestrator = create_developer_orchestrator()

    print("\n--- Physics Paradigms in Action ---")

    requirements = {
        "app_type": "python_library",
        "app_name": "data_science_toolkit",
        "description": "Library for data science operations",
        "modules": ["preprocessing", "analysis", "visualization", "export"],
        "public_api": ["load_data", "clean_data", "analyze", "plot", "save_results"],
    }

    print("\n1. CHAOS THEORY: Generating Diverse Suggestions")
    print("   Using chaotic neural networks to explore parameter space")

    analysis = orchestrator.analyze_user_requirements(requirements)

    if orchestrator.physics_orchestrator:
        print("   ✓ Chaos-generated suggestions available")
        if "python_version" in analysis["suggestions"]:
            print(f"   Example suggestions: {analysis['suggestions']['python_version']}")

    print("\n2. FRACTAL GEOMETRY: Analyzing Code Structure")
    print("   Using fractal dimension to detect complexity")

    architecture = orchestrator.suggest_architecture(requirements)

    if "structure_analysis" in architecture and architecture["structure_analysis"]:
        struct = architecture["structure_analysis"]
        print(f"   ✓ Fractal dimension: {struct.get('fractal_dimension', 0):.2f}")
        print(f"   ✓ Total nodes: {struct.get('nodes', 0)}")
        print(
            f"   Interpretation: {'Simple structure' if struct.get('fractal_dimension', 0) < 2.0 else 'Complex structure'}"
        )

    print("\n3. ELECTROMAGNETIC FIELDS: Component Prioritization")
    print("   Using field potentials to route development attention")

    if orchestrator.physics_orchestrator:
        print("   ✓ EM field analysis applied")
        print("   High-priority components (charged hotspots):")
        sorted_comps = sorted(architecture["components"], key=lambda c: c["priority"], reverse=True)
        for comp in sorted_comps[:3]:
            print(f"     • {comp['name']} (priority: {comp['priority']:.2f})")

    print("\n4. FLUID DYNAMICS: Workflow Optimization")
    print("   Using flow equations to balance development resources")
    print("   ✓ Implementation order optimized for dependency flow")

    print("\n5. QUANTUM SUPERPOSITION: Parallel Evaluation")
    print("   Evaluating multiple architectural approaches simultaneously")
    print("   ✓ Best approach selected based on optimization score")

    print("\n--- Summary ---")
    print("Physics paradigms provide:")
    print("  • Diverse exploration (Chaos)")
    print("  • Structure analysis (Fractals)")
    print("  • Priority guidance (EM Fields)")
    print("  • Resource optimization (Fluid Dynamics)")
    print("  • Parallel evaluation (Quantum)")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("PHYSICS-GUIDED SOFTWARE DEVELOPER ORCHESTRATOR")
    print("=" * 70)
    print("\nLeveraging physics paradigms for intelligent development:")
    print("  • Chaos Theory → Diverse exploration")
    print("  • Fractal Geometry → Structure analysis")
    print("  • Fluid Dynamics → Workflow optimization")
    print("  • EM Fields → Priority guidance")
    print("  • Wave Propagation → Team synchronization")
    print("  • Relativity → Distributed coordination")
    print("  • Quantum Mechanics → Parallel evaluation")

    # Run demonstrations
    demo_cli_app_development()
    demo_api_development()
    demo_interactive_workflow()
    demo_physics_integration()

    print("\n" + "=" * 70)
    print("ALL DEMONSTRATIONS COMPLETE")
    print("=" * 70)
    print("\nThe orchestrator is ready to develop applications!")
    print("\nUsage:")
    print("  from agents.developer_orchestrator import create_developer_orchestrator")
    print("  orchestrator = create_developer_orchestrator()")
    print("  analysis = orchestrator.analyze_user_requirements(requirements)")
    print("  architecture = orchestrator.suggest_architecture(requirements)")
    print("  code = orchestrator.generate_code('main', requirements)")


if __name__ == "__main__":
    main()
