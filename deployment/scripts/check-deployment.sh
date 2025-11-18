#!/bin/bash
echo "Ì∫Ä AI-NEXUS Phoenix Deployment Verifier"
echo "======================================="

echo "1. Checking local files..."
files=("app.py" "requirements.txt" "runtime.txt" "README.md")
for file in "${files}"; do
    if [ -f "$file" ]; then
        echo "   ‚úÖ $file"
    else
        echo "   ‚ùå $file"
    fi
done

echo "2. Checking Git status..."
git status --short

echo "3. Checking remote..."
git remote -v

echo ""
echo "4. Next steps:"
echo "   - Wait for Render auto-deploy (2-3 min)"
echo "   - Visit: https://ainexus-phoenix.onrender.com"
echo "   - Check: https://ainexus-phoenix.onrender.com/health"
echo ""
echo "5. If deployment fails:"
echo "   - Check Render build logs"
echo "   - Verify all files are in GitHub repo"
echo "   - Ensure requirements.txt is correct"
