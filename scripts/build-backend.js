const { spawn, spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// 确定当前平台
const isWin = process.platform === 'win32';

// 后端目录
const backendDir = path.join(__dirname, '..', 'backend');

let pythonCmd;
let useUv = false;

// 检查 uv 是否可用
try {
    const uvCheck = spawnSync('uv', ['--version'], { shell: true, stdio: 'ignore' });
    if (uvCheck.status === 0) {
        useUv = true;
    }
} catch (e) {
    // ignore
}

if (useUv) {
    pythonCmd = 'uv';
    console.log('[Build] Found uv, using it to run build command');
} else {
    // 尝试查找虚拟环境 Python
    const venvPythonWin = path.join(backendDir, '.venv', 'Scripts', 'python.exe');
    const venvPythonNix = path.join(backendDir, '.venv', 'bin', 'python');

    if (isWin && fs.existsSync(venvPythonWin)) {
        pythonCmd = venvPythonWin;
    } else if (!isWin && fs.existsSync(venvPythonNix)) {
        pythonCmd = venvPythonNix;
    } else {
        // 回退到系统 Python
        pythonCmd = isWin ? 'python' : 'python3';
        console.log('[Build] Virtual environment python not found, falling back to system python:', pythonCmd);
    }
}

console.log(`[Build] Platform: ${process.platform}`);
console.log(`[Build] Using Command: ${pythonCmd}`);

// 构建 PyInstaller 命令

const specFile = path.join(backendDir, 'novelmind.spec');
console.log(`[Build] Spec file path: ${specFile}`);

let args = ['-m', 'PyInstaller', specFile, '--noconfirm', '--clean'];

if (useUv) {
    args = ['run', 'python', ...args];
}

const child = spawn(pythonCmd, args, {
    cwd: backendDir,
    stdio: 'inherit',
    shell: true
});

child.on('close', (code) => {
    if (code !== 0) {
        console.error(`[Build] Process exited with code ${code}`);
        process.exit(code);
    }
});

child.on('error', (err) => {
    console.error('[Build] Failed to start process:', err);
    process.exit(1);
});
