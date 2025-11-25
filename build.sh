#!/bin/bash
echo "Ì∫Ä Starting QuantumNex build process..."

# Install dependencies
echo "Ì≥¶ Installing dependencies..."
npm install

# Build React app
echo "Ì¥® Building React app..."
if npm run build; then
    echo "‚úÖ Build completed successfully!"
    echo "Ì≥Å Build directory created: ./build"
    
    # Verify build
    if [ -d "./build" ] && [ -f "./build/index.html" ]; then
        echo "‚úÖ Build verification passed"
        exit 0
    else
        echo "‚ùå Build verification failed - missing build files"
        exit 1
    fi
else
    echo "‚ùå Build failed"
    exit 1
fi
