#!/bin/bash
# Verify workflow compliance with Phase 2 standards

echo "🔍 Phase 2 Workflow Compliance Verification"
echo "=============================================="

workflows_dir=".github/workflows"
total=0
concurrency_ok=0
timeout_ok=0
both_ok=0

echo ""
echo "Checking $(find $workflows_dir -name "*.yml" -o -name "*.yaml" | wc -l) workflows..."
echo ""

for file in $(find $workflows_dir -name "*.yml" -o -name "*.yaml" | sort); do
  total=$((total + 1))
  
  # Check concurrency
  if grep -q "concurrency:" "$file" && grep -q "github.workflow.*github.head_ref.*github.ref" "$file" 2>/dev/null; then
    concurrency_ok=$((concurrency_ok + 1))
    concurrency_status="✅"
  else
    concurrency_status="❌"
  fi
  
  # Check timeout
  jobs_count=$(grep -c "^\s\s[a-z].*:" "$file" 2>/dev/null || echo 0)
  timeout_count=$(grep -c "timeout-minutes:" "$file" 2>/dev/null || echo 0)
  
  if [ "$jobs_count" -eq 0 ] || [ "$timeout_count" -gt 0 ]; then
    timeout_ok=$((timeout_ok + 1))
    timeout_status="✅"
  else
    timeout_status="⚠️"
  fi
  
  if [ "$concurrency_status" = "✅" ] && [ "$timeout_status" = "✅" ]; then
    both_ok=$((both_ok + 1))
  fi
done

echo ""
echo "📊 Results:"
echo "  Total workflows: $total"
echo "  ✅ With branch-scoped concurrency: $concurrency_ok / $total ($(( concurrency_ok * 100 / total ))%)"
echo "  ✅ With job timeouts: $timeout_ok / $total ($(( timeout_ok * 100 / total ))%)"
echo "  ✅ Fully compliant: $both_ok / $total ($(( both_ok * 100 / total ))%)"
echo ""

if [ "$both_ok" -eq "$total" ]; then
  echo "✅ ALL WORKFLOWS COMPLIANT"
  exit 0
else
  echo "⚠️  $(( total - both_ok )) workflows need attention"
  exit 1
fi
