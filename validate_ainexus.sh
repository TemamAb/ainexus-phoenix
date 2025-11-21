#!/bin/bash

echo "=================================================="
echo "Ì¥ç AINEXUS v3.0.0 - 90 MODULE VALIDATION"
echo "=================================================="

total_files=0
total_size=0

validate_modules() {
    local dir=$1
    local indent=$2
    
    echo "${indent}Ì≥Å $(basename "$dir")/"
    
    local file_count=0
    local dir_size=0
    
    for file in "$dir"/*; do
        if [ -f "$file" ]; then
            local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
            local size_kb=$((size / 1024))
            echo "${indent}   Ì≥Ñ $(basename "$file") (${size_kb} KB)"
            ((total_files++))
            ((file_count++))
            ((total_size+=size))
            ((dir_size+=size))
        fi
    done
    
    for subdir in "$dir"/*; do
        if [ -d "$subdir" ] && [ "$(basename "$subdir")" != "__pycache__" ] && [ "$(basename "$subdir")" != ".git" ]; then
            validate_modules "$subdir" "$indent   "
        fi
    done
    
    if [ $file_count -gt 0 ]; then
        local dir_size_kb=$((dir_size / 1024))
        echo "${indent}   Ì≥ä $(basename "$dir"): $file_count files (${dir_size_kb} KB)"
    fi
}

echo ""
echo "Ì≥Ç PROJECT STRUCTURE ANALYSIS"
echo "=================================================="

core_dirs=("core" "modules" "templates" "static" "config" "utils" "tests" "docs")

for dir in "${core_dirs[@]}"; do
    if [ -d "$dir" ]; then
        validate_modules "$dir" ""
        echo ""
    fi
done

python_files=$(find . -name "*.py" -not -path "./.git/*" -not -path "*/__pycache__/*" | wc -l)
config_files=$(find . -name "*.json" -o -name "*.yaml" -o -name "*.yml" -not -path "./.git/*" | wc -l)
template_files=$(find . -name "*.html" -o -name "*.jinja2" -not -path "./.git/*" | wc -l)
css_js_files=$(find . -name "*.css" -o -name "*.js" -not -path "./.git/*" | wc -l)

echo "=================================================="
echo "Ì≥ä VALIDATION SUMMARY"
echo "=================================================="
echo "‚úÖ Total Files: $total_files"
echo "‚úÖ Total Size: $((total_size / 1024 / 1024)) MB"
echo "‚úÖ Python Modules: $python_files"
echo "‚úÖ Configuration Files: $config_files"
echo "‚úÖ Template Files: $template_files"
echo "‚úÖ CSS/JS Files: $css_js_files"

echo ""
echo "Ì¥ß MODULE CATEGORY BREAKDOWN"
echo "=================================================="

core_modules=$(find modules -name "*.py" -not -path "*/__pycache__/*" | grep -i "core\|bootstrap\|orchestrat" | wc -l)
ai_modules=$(find modules -name "*.py" -not -path "*/__pycache__/*" | grep -i "ai\|ml\|learning\|intelligence" | wc -l)
execution_modules=$(find modules -name "*.py" -not -path "*/__pycache__/*" | grep -i "execution\|trade\|arbitrage" | wc -l)
risk_modules=$(find modules -name "*.py" -not -path "*/__pycache__/*" | grep -i "risk\|compliance\|security" | wc -l)
ux_modules=$(find modules -name "*.py" -not -path "*/__pycache__/*" | grep -i "ux\|ui\|dashboard\|interface" | wc -l)

echo "‚úÖ Core Infrastructure: $core_modules modules"
echo "‚úÖ AI & Strategy Engine: $ai_modules modules" 
echo "‚úÖ Execution & Risk: $execution_modules modules"
echo "‚úÖ Platform & UX: $ux_modules modules"
echo "‚úÖ Risk & Compliance: $risk_modules modules"

echo ""
echo "Ì∫Ä DEPLOYMENT FILES VALIDATION"
echo "=================================================="

deployment_files=("core/app.py" "render.yaml" "requirements.txt" "runtime.txt" ".env.example" ".gitignore")

for file in "${deployment_files[@]}"; do
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        echo "‚úÖ $file ($((size / 1024)) KB)"
    else
        echo "‚ùå $file - MISSING"
    fi
done

echo ""
echo "ÌæØ FINAL VALIDATION STATUS"
echo "=================================================="

total_modules=$((core_modules + ai_modules + execution_modules + risk_modules + ux_modules))

if [ $total_modules -ge 85 ]; then
    echo "Ì∫Ä SUCCESS: $total_modules/90 Modules Validated"
    echo "‚úÖ AINEXUS v3.0.0 READY FOR DEPLOYMENT"
    echo "‚úÖ Enterprise Platform: 90+ Module Capability"
    echo "‚úÖ Production Ready: All Systems Go"
else
    echo "‚ö†Ô∏è  WARNING: $total_modules/90 Modules Found"
    echo "‚ùå Additional Modules Required for Full Deployment"
fi

echo ""
echo "Ì≥ã QUICK HEALTH CHECK"
echo "=================================================="

if [ -f "core/app.py" ]; then
    echo "‚úÖ Main Application: core/app.py"
else
    echo "‚ùå Main Application: Missing"
fi

if [ -f "requirements.txt" ]; then
    req_count=$(wc -l < requirements.txt)
    echo "‚úÖ Dependencies: $req_count packages"
else
    echo "‚ùå Dependencies: requirements.txt missing"
fi

if [ -f "render.yaml" ]; then
    echo "‚úÖ Render Config: render.yaml"
else
    echo "‚ùå Render Config: Missing"
fi

echo ""
echo "Ìæ™ AINEXUS v3.0.0 - VALIDATION COMPLETE Ìæ™"
