/**
 * copymain.js - Post-build standalone server staging script for Azure App Service.
 * Ensures standalone Next.js server files, public directory, and static assets
 * are correctly placed in the root execution directory for Azure App Service.
 */

const fs = require('fs');
const path = require('path');

function copyRecursive(src, dest) {
  if (!fs.existsSync(src)) return;
  const stats = fs.statSync(src);
  if (stats.isDirectory()) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }
    fs.readdirSync(src).forEach((child) => {
      copyRecursive(path.join(src, child), path.join(dest, child));
    });
  } else {
    fs.copyFileSync(src, dest);
  }
}

const standaloneDir = path.join(__dirname, '.next', 'standalone');
if (fs.existsSync(standaloneDir)) {
  console.log('[copymain] Staging standalone Next.js build for Azure App Service...');
  copyRecursive(path.join(__dirname, 'public'), path.join(standaloneDir, 'public'));
  copyRecursive(path.join(__dirname, '.next', 'static'), path.join(standaloneDir, '.next', 'static'));
  console.log('[copymain] Standalone staging complete.');
}
