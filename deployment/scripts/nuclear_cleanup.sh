#!/bin/bash
echo "Ì∑π NUCLEAR DUPLICATION CLEANUP STARTING..."

# 1. REMOVE THE GHOST ai-nexus-v5.0 ENTIRELY
echo "=== REMOVING ai-nexus-v5.0 GHOST ==="
if [ -d "ai-nexus-v5.0" ]; then
    echo "Ì∫Æ DELETING: ai-nexus-v5.0/ (source of duplication)"
    rm -rf ai-nexus-v5.0/
    echo "‚úÖ ai-nexus-v5.0 REMOVED"
else
    echo "‚úÖ ai-nexus-v5.0 already gone"
fi

# 2. REMOVE DUPLICATE MODULES FROM CORRUPTED DIRECTORIES
echo "=== CLEANING DUPLICATE DIRECTORIES ==="
for dir in advanced_ai core_foundation competitive_edge; do
    if [ -d "$dir" ]; then
        echo "Ì∑π Cleaning $dir/ duplicates..."
        find "$dir" -name "*.py" -o -name "*.js" -o -name "*.sol" 2>/dev/null | while read file; do
            if [ -f "$file" ]; then
                base_file=$(basename "$file")
                if find ./src -name "$base_file" 2>/dev/null | grep -q .; then
                    echo "‚ùå REMOVING DUPLICATE: $file"
                    rm "$file"
                fi
            fi
        done
        echo "‚úÖ $dir cleaned"
    else
        echo "‚úÖ $dir not found"
    fi
done

# 3. REMOVE ROOT-LEVEL DUPLICATES
echo "=== CLEANING ROOT LEVEL DUPLICATES ==="
for file in *.py *.js *.sol 2>/dev/null; do
    if [ -f "$file" ] && find ./src -name "$file" 2>/dev/null | grep -q .; then
        echo "‚ùå REMOVING ROOT DUPLICATE: $file"
        rm "$file"
    fi
done

echo "‚úÖ DUPLICATION CLEANUP COMPLETE"
