#!/bin/bash
# migrate_agent.sh - Migrate agent to standard structure
# Usage: ./migrate_agent.sh <agent-name>

set -e

AGENT_NAME=$1
AGENT_DIR=".github/agents/$AGENT_NAME"
TEMPLATE_DIR=".github/agents/.template"

if [ -z "$AGENT_NAME" ]; then
    echo "Usage: $0 <agent-name>"
    exit 1
fi

if [ ! -d "$AGENT_DIR" ]; then
    echo "Error: Agent directory not found: $AGENT_DIR"
    exit 1
fi

echo "🔄 Migrating agent: $AGENT_NAME"
echo "================================"

# Create missing directories
mkdir -p "$AGENT_DIR/prompts"
mkdir -p "$AGENT_DIR/src"
mkdir -p "$AGENT_DIR/tests"
mkdir -p "$AGENT_DIR/config"

echo "✅ Created standard directories"

# Copy template files if they don't exist
if [ ! -f "$AGENT_DIR/CHANGELOG.md" ]; then
    cp "$TEMPLATE_DIR/CHANGELOG.md" "$AGENT_DIR/CHANGELOG.md"
    echo "✅ Added CHANGELOG.md"
fi

if [ ! -f "$AGENT_DIR/prompts/main.md" ]; then
    cp "$TEMPLATE_DIR/prompts/main.md" "$AGENT_DIR/prompts/"
    echo "✅ Added prompts/main.md"
fi

if [ ! -f "$AGENT_DIR/prompts/examples.md" ]; then
    cp "$TEMPLATE_DIR/prompts/examples.md" "$AGENT_DIR/prompts/"
    echo "✅ Added prompts/examples.md"
fi

if [ ! -f "$AGENT_DIR/prompts/advanced.md" ]; then
    cp "$TEMPLATE_DIR/prompts/advanced.md" "$AGENT_DIR/prompts/"
    echo "✅ Added prompts/advanced.md"
fi

if [ ! -f "$AGENT_DIR/config/agent_config.yaml" ]; then
    cp "$TEMPLATE_DIR/config/agent_config.yaml" "$AGENT_DIR/config/"
    echo "✅ Added config/agent_config.yaml"
fi

echo "✅ Migration complete for $AGENT_NAME"
echo "📝 Next steps:"
echo "   1. Customize prompts/main.md with agent-specific prompt"
echo "   2. Update config/agent_config.yaml with agent settings"
echo "   3. Ensure tests are in tests/ directory"
echo "   4. Update AGENT_REGISTRY.yaml"
