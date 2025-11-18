#!/bin/bash
echo "í·ª Testing pip installation with requirements.txt..."

# Test install in dry-run mode
if python -m pip install -r requirements.txt --dry-run > /dev/null 2>&1; then
    echo "âœ… requirements.txt is valid - all packages can be installed"
else
    echo "âŒ Some packages may have installation issues"
    echo "í´§ Checking individual packages..."
    
    # Test critical packages individually
    for pkg in web3 numpy pandas flask requests; do
        if python -m pip install "$pkg" --dry-run > /dev/null 2>&1; then
            echo "âœ… $pkg - Installable"
        else
            echo "âŒ $pkg - May have issues"
        fi
    done
fi
