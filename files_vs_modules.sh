#!/bin/bash

echo "Ì≥Å FILES vs Ì∑© MODULES ANALYSIS"
echo "=========================================="

# Count ALL files (including non-module files)
echo "Ì≥Å TOTAL FILES IN REPOSITORY:"
total_files=$(find . -type f | wc -l)
echo "All files: $total_files"

# Count code files only (potential modules)
echo ""
echo "Ì≤ª CODE FILES (Potential Modules):"
code_files=$(find . -type f \( -name "*.js" -o -name "*.py" -o -name "*.sol" -o -name "*.json" -o -name "*.md" -o -name "*.txt" -o -name "*.yaml" -o -name "*.yml" \) | wc -l)
echo "Code/config files: $code_files"

# Count executable modules only
echo ""
echo "Ì∑© EXECUTABLE MODULES (Core Logic):"
executable_modules=$(find . -type f \( -name "*.js" -o -name "*.py" -o -name "*.sol" \) | grep -v -E "(test|__pycache__|node_modules|.git|config|.json|.md|.txt)" | wc -l)
echo "Executable modules: $executable_modules"

# Count test files
echo ""
echo "Ì∑™ TEST FILES:"
test_files=$(find . -type f \( -name "*.test.js" -o -name "*test*.py" -o -name "*Test*.py" \) | wc -l)
echo "Test files: $test_files"

# Count config files
echo ""
echo "‚öôÔ∏è CONFIGURATION FILES:"
config_files=$(find . -type f \( -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "config.js" -o -name "*.config.js" \) | wc -l)
echo "Config files: $config_files"

# Count documentation files
echo ""
echo "Ì≥ö DOCUMENTATION FILES:"
doc_files=$(find . -type f \( -name "*.md" -o -name "*.txt" -o -name "README*" -o -name "*.rst" \) | wc -l)
echo "Documentation: $doc_files"

# Show breakdown
echo ""
echo "Ì≥ä BREAKDOWN:"
echo "Ì≥Å Total files: $total_files"
echo "Ì≤ª Code/config files: $code_files"
echo "Ì∑© Executable modules: $executable_modules"
echo "Ì∑™ Test files: $test_files"
echo "‚öôÔ∏è Config files: $config_files"
echo "Ì≥ö Documentation: $doc_files"
echo "Ì≥¶ Other files: $((total_files - code_files))"

# Show what's counted as "modules" vs "files"
echo ""
echo "Ì¥ç MODULE VS FILE DEFINITION:"
echo "Ì∑© MODULES = .js, .py, .sol files (excluding tests/config)"
echo "Ì≥Å FILES = Everything in repository (including docs, configs, tests)"

