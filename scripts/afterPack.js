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
    console.log('Backend directory not found, skipping Python setup');
    return;
  }
  
  // Create a startup script that handles Python environment
  if (platform === 'windows') {
    // Create a batch file to check/install Python dependencies
    const setupScript = `@echo off
echo Setting up NovelMind backend...

REM Check if uv is available
where uv >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Using uv to manage dependencies...
    cd /d "%~dp0"
    uv sync
    exit /b 0
)

REM Fallback to pip
echo Installing dependencies with pip...
python -m pip install -r requirements.txt
exit /b 0
`;
    fs.writeFileSync(path.join(backendPath, 'setup.bat'), setupScript);
  }
  
  // Create requirements.txt from pyproject.toml for fallback
  const pyprojectPath = path.join(backendPath, 'pyproject.toml');
  if (fs.existsSync(pyprojectPath)) {
    const pyproject = fs.readFileSync(pyprojectPath, 'utf8');
    
    // Extract dependencies (simplified parsing)
    const depsMatch = pyproject.match(/dependencies\s*=\s*\[([\s\S]*?)\]/);
    if (depsMatch) {
      const deps = depsMatch[1]
        .split('\n')
        .map(line => line.trim().replace(/[",]/g, ''))
        .filter(line => line && !line.startsWith('#'));
      
      const requirementsPath = path.join(backendPath, 'requirements.txt');
      fs.writeFileSync(requirementsPath, deps.join('\n'));
      console.log('Created requirements.txt from pyproject.toml');
    }
  }
  
  console.log('AfterPack completed');
};
