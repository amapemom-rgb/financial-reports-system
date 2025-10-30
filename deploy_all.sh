#!/bin/bash
# Session 21: Master Deployment Script

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║         🚀 Session 21: Deploy & Test Upload Fix 🚀        ║"
echo "║                                                            ║"
echo "║  Bug #2 Fix: Signed URL Pattern for File Uploads          ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get repository root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "${REPO_ROOT}"

echo "Repository: ${REPO_ROOT}"
echo ""

# Check we're on the right branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: ${CURRENT_BRANCH}"
echo ""

# Check for Session 20 commits
echo "Checking for Session 20 changes..."
git log --oneline -5 | grep -E "(Session 20|upload)" || echo "⚠️  Warning: Session 20 commits not found in recent history"
echo ""

# Confirmation
read -p "Ready to deploy? This will build and deploy both services. (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "PHASE 1: Deploy Logic Agent (Backend)"
echo "════════════════════════════════════════════════════════════"
echo ""

bash deploy_logic_agent_v12.sh

echo ""
echo "════════════════════════════════════════════════════════════"
echo "PHASE 2: Deploy Web UI (Frontend)"
echo "════════════════════════════════════════════════════════════"
echo ""

bash deploy_web_ui_v10.sh

echo ""
echo "════════════════════════════════════════════════════════════"
echo "PHASE 3: Test Endpoints"
echo "════════════════════════════════════════════════════════════"
echo ""

bash test_upload_endpoints.sh

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║                   🎉 DEPLOYMENT COMPLETE! 🎉               ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "1. Open Web UI in browser"
echo "2. Test file upload with real files"
echo "3. Verify all 5 test cases:"
echo "   □ Small CSV file (< 1MB)"
echo "   □ Medium Excel file (1-5MB)"
echo "   □ Large multi-sheet Excel (10+ sheets)"
echo "   □ Invalid file type (should show error)"
echo "   □ Network error (disconnect during upload)"
echo ""
echo "4. After testing, document results in docs/SESSION_21_SUMMARY.md"
echo ""
echo "Happy testing! 🚀"
