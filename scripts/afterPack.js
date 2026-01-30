/**
 * electron-builder afterPack hook
 * Used to set up Python environment in the packaged application
 */
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

exports.default = async function(context) {
  const { appOutDir, packager } = context;
  const platform = packager.platform.name;
  
  console.log(`AfterPack: Setting up for ${platform}`);
  
  // Path to backend in resources
  const backendPath = path.join(appOutDir, 'resources', 'backend');
  
  if (!fs.existsSync(backendPath)) {
    console.log('Backend directory not found, skipping setup');
    return;
  }
  
  // Create data directory if it doesn't exist (to ensure backend can write)
  const dataPath = path.join(backendPath, 'data');
  if (!fs.existsSync(dataPath)) {
    fs.mkdirSync(dataPath, { recursive: true });
    console.log('Created backend/data directory');
  }

  // Create an empty app.log to ensure the file exists
  const logFile = path.join(dataPath, 'app.log');
  if (!fs.existsSync(logFile)) {
    fs.writeFileSync(logFile, '');
  }
  
  console.log('AfterPack completed');
};
