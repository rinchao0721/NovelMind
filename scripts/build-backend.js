const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// 确定当前平台
const isWin = process.platform === 'win32';

// 后端目录
const backendDir = path.join(__dirname, '..', 'backend');

// 尝试查找虚拟环境 Python
const venvPythonWin = path.join(backendDir, '.venv', 'Scripts', 'python.exe');
const venvPythonNix = path.join(backendDir, '.venv', 'bin', 'python');

let pythonCmd;

if (isWin && fs.existsSync(venvPythonWin)) {
    pythonCmd = venvPythonWin;
} else if (!isWin && fs.existsSync(venvPythonNix)) {
    pythonCmd = venvPythonNix;
} else {
    // 回退到系统 Python
    pythonCmd = isWin ? 'python' : 'python3';
    console.log('[Build] Virtual environment python not found, falling back to system python:', pythonCmd);
}

console.log(`[Build] Platform: ${process.platform}`);
console.log(`[Build] Using Python: ${pythonCmd}`);

// 构建 PyInstaller 命令
// 注意：在 Windows 上使用 spawn 需要 shell: true 才能正确解析路径中的空格等，
// 但在 Linux 上直接运行文件路径通常不需要 shell: true，除非是命令别名。
// 为了简单，我们统一使用 shell: true，但要注意参数转义（这里参数简单，没问题）。

const args = ['-m', 'PyInstaller', 'novelmind.spec', '--noconfirm', '--clean'];

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
