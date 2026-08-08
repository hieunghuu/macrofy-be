#!/bin/bash
# Run code review on the meal optimizer
# Usage: ./scripts/run_code_review.sh

set -e

echo "========================================"
echo "Meal Optimizer Code Review"
echo "========================================"
echo ""

FILES=(
  "app/services/lp_meal_optimizer.py"
  "app/services/lp_weights_service.py"
  "app/schemas/lp_weights.py"
  "tests/test_lp_meal_optimizer.py"
)

echo "Files to review:"
for f in "${FILES[@]}"; do
  echo "  - $f"
done
echo ""

# Run the agent
echo "Starting code review agent..."
echo ""

# Use Claude Code to invoke the agent
claude --agent "meal-optimizer-reviewer" <<'EOF'
Review the meal optimizer implementation. Check:
1. LP formulation correctness
2. OR-Tools API usage
3. Edge cases and error handling
4. Test coverage

Files:
- app/services/lp_meal_optimizer.py
- app/services/lp_weights_service.py
- app/schemas/lp_weights.py
- tests/test_lp_meal_optimizer.py

Run the tests first: python -m pytest tests/test_lp_meal_optimizer.py -v
EOF

echo ""
echo "========================================"
echo "Code review complete"
echo "========================================"
