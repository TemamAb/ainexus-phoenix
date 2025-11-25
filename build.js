const { execSync } = require('child_process');
const fs = require('fs');

console.log('Ì∫Ä Building QuantumNex Dashboard...');

try {
  // Run React build
  execSync('npm run build', { stdio: 'inherit' });
  console.log('‚úÖ Build completed successfully!');
  
  // Check if build directory exists
  if (fs.existsSync('./build')) {
    console.log('Ì≥Å Build directory verified');
    process.exit(0);
  } else {
    console.log('‚ùå Build directory not found');
    process.exit(1);
  }
} catch (error) {
  console.error('‚ùå Build failed:', error);
  process.exit(1);
}
