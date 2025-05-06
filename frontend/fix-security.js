#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('Running security fixes for frontend dependencies...');

// Resolve the PrismJS vulnerability in react-syntax-highlighter
try {
  const nodeModulesPath = path.join(__dirname, 'node_modules');
  const prismjsPath = path.join(nodeModulesPath, 'refractor/node_modules/prismjs');
  
  if (fs.existsSync(prismjsPath)) {
    console.log('Updating vulnerable PrismJS dependency...');
    execSync('npm install prismjs@1.30.0 --save=false', { stdio: 'inherit' });
    
    // Copy the newer version over the vulnerable one
    const safeVersion = path.join(nodeModulesPath, 'prismjs');
    if (fs.existsSync(safeVersion)) {
      execSync(`cp -r ${safeVersion}/* ${prismjsPath}/`, { stdio: 'inherit' });
      console.log('✅ PrismJS vulnerability patched');
    }
  }
} catch (error) {
  console.error('❌ Failed to patch PrismJS:', error.message);
}

// Add any other security fixes here

console.log('Security checks complete'); 