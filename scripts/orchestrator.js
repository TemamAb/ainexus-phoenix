const { spawn } = require('child_process');
const express = require('express');

console.log('Ì∫Ä AINEXUS 96-Module Platform - Starting...');

// Start Python Flask app
const pythonApp = spawn('python', ['core/app.py'], {
  stdio: 'inherit',
  env: { ...process.env, PORT: process.env.PORT || 10000 }
});

// Start JavaScript modules loader
const jsModules = spawn('node', ['scripts/load-js-modules.js'], {
  stdio: 'inherit'
});

pythonApp.on('error', (err) => {
  console.log('‚ùå Python app failed:', err);
});

jsModules.on('error', (err) => {
  console.log('‚ùå JS modules failed:', err);
});

console.log('‚úÖ Both Python and JavaScript runtimes started');
console.log('Ìºê AINEXUS Platform initializing 96 modules...');
