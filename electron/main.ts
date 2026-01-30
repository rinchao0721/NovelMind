import { app, BrowserWindow, ipcMain, dialog, shell } from 'electron'
import { spawn, exec, ChildProcess } from 'child_process'
import path from 'path'
import fs from 'fs'
import net from 'net'
import { fileURLToPath } from 'url'
import log from 'electron-log/main'

// Initialize logger
log.initialize()
log.info('App starting...')

// Disable security warnings in development
// These warnings are useful but noisy in dev mode where 'unsafe-eval' is required by Vite
if (process.env.VITE_DEV_SERVER_URL) {
  process.env['ELECTRON_DISABLE_SECURITY_WARNINGS'] = 'true'
}

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// 环境变量
process.env.DIST = path.join(__dirname, '../dist')
process.env.VITE_PUBLIC = app.isPackaged
  ? process.env.DIST
  : path.join(__dirname, '../public')

let mainWindow: BrowserWindow | null = null
let backendProcess: ChildProcess | null = null

// 后端服务器端口 (Dynamic)
let BACKEND_PORT = 5001

// 获取空闲端口
const getFreePort = (): Promise<number> => {
  return new Promise((resolve, reject) => {
    const server = net.createServer()
    server.listen(0, '127.0.0.1', () => {
      const port = (server.address() as net.AddressInfo).port
      server.close(() => resolve(port))
    })
    server.on('error', reject)
  })
}

// 创建主窗口
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    icon: path.join(__dirname, '../resources/icons/icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    },
    show: false,
    titleBarStyle: 'hiddenInset',
    frame: true
  })

  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow?.show()
    log.info('Main window shown')
  })

  // 开发环境加载本地服务器，生产环境加载打包文件
  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL)
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(process.env.DIST!, 'index.html'))
  }

  // 外部链接用默认浏览器打开
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  mainWindow.on('closed', () => {
    mainWindow = null
    log.info('Main window closed')
  })
}

// 启动 Python 后端
async function startBackend() {
  const isDev = !!process.env.VITE_DEV_SERVER_URL
  let backendPath = ''
  let executable = ''
  let args: string[] = []
  let spawnOptions: any = {
    env: {
      ...process.env,
      APP_PORT: String(BACKEND_PORT),
      PYTHONUNBUFFERED: '1' // Ensure output is flushed immediately
    },
    stdio: ['pipe', 'pipe', 'pipe'], // We will pipe stdout/stderr manually
    windowsHide: true // 💡 隐藏控制台窗口
  }

  if (isDev) {
    // Dev mode: use uv run python from source
    backendPath = path.join(__dirname, '../backend')
    
    if (!fs.existsSync(backendPath)) {
      console.error(`[Backend Error] Directory not found: ${backendPath}`)
      log.error(`Backend directory not found: ${backendPath}`)
      return
    }

    executable = process.platform === 'win32' ? 'uv.exe' : 'uv'
    args = ['run', 'python', 'main.py']
    
    // Enable shell in dev on Windows to find uv in PATH
    if (process.platform === 'win32') {
      spawnOptions.shell = true
    }
    
    log.info(`Development mode: Starting backend using ${executable} in ${backendPath}`)
  } else {
    // Production mode
    const resourcesPath = app.isPackaged ? process.resourcesPath : path.join(__dirname, '../')
    backendPath = path.join(resourcesPath, 'backend', 'novelmind')

    // Executable name based on OS (created by PyInstaller)
    const exeName = process.platform === 'win32' ? 'novelmind.exe' : 'novelmind'
    const bundledExe = path.join(backendPath, exeName)
    const internalPath = path.join(backendPath, '_internal')

    // Detailed debug logging for production
    log.info(`=== Backend Path Debug (Production) ===`)
    log.info(`Resources path: ${resourcesPath}`)
    log.info(`Backend path: ${backendPath}`)
    log.info(`Exe path: ${bundledExe}`)
    log.info(`Exe exists: ${fs.existsSync(bundledExe)}`)
    log.info(`_internal exists: ${fs.existsSync(internalPath)}`)
    
    // List backend folder contents for debugging
    if (fs.existsSync(path.join(resourcesPath, 'backend'))) {
      try {
        const backendFiles = fs.readdirSync(path.join(resourcesPath, 'backend'))
        log.info(`Backend folder contents: ${backendFiles.join(', ')}`)
        
        if (fs.existsSync(backendPath)) {
          const novelmindFiles = fs.readdirSync(backendPath)
          log.info(`Novelmind folder contents: ${novelmindFiles.join(', ')}`)
        }
      } catch (e: any) {
        log.error(`Failed to list backend files: ${e.message}`)
      }
    } else {
      log.error(`Backend folder not found at: ${path.join(resourcesPath, 'backend')}`)
    }

    if (fs.existsSync(bundledExe)) {
      executable = bundledExe
      args = []
      log.info(`Production mode: Found bundled executable: ${executable}`)
    } else {
      // Fallback to python script (legacy)
      log.warn('[Backend] Bundled executable not found, falling back to python script')
      log.warn('[Backend] This fallback likely will not work in packaged app')
      executable = process.platform === 'win32' ? 'python' : 'python3'
      args = ['main.py']
    }
    
    log.info(`Production mode: Starting backend from: ${backendPath}`)
  }

  spawnOptions.cwd = backendPath

  try {
    backendProcess = spawn(executable, args, spawnOptions)

    // Setup dedicated logging for backend
    const userDataPath = app.getPath('userData')
    const logFilePath = path.join(userDataPath, 'app.log')
    const logStream = fs.createWriteStream(logFilePath, { flags: 'a' })
    
    log.info(`Backend logs redirected to: ${logFilePath}`)

    // Write start marker
    const startMsg = `\n--- Backend Session Started at ${new Date().toISOString()} (Port: ${BACKEND_PORT}) ---\n`
    logStream.write(startMsg)

    // Pipe stdout/stderr to file
    backendProcess.stdout?.pipe(logStream)
    backendProcess.stderr?.pipe(logStream)

    // Also log errors to electron-log for visibility in main log
    backendProcess.stderr?.on('data', (data) => {
      const msg = data.toString().trim()
      // Optional: Filter out non-critical info messages if they appear in stderr
      if (msg) {
        log.debug(`[Backend Stderr] ${msg}`) 
      }
    })

    backendProcess.stdout?.on('data', () => {
        // Minimal console output for dev feedback if needed
        if (isDev) {
            // process.stdout.write(data) 
        }
    })

    backendProcess.on('error', (err) => {
      const msg = `Failed to start backend: ${err.message}`
      console.error(msg)
      log.error(msg)
      logStream.write(`[Launch Error] ${msg}\n`)
      dialog.showErrorBox('Backend Error', msg)
    })

    backendProcess.on('close', (code) => {
      const msg = `Backend process exited with code ${code}`
      log.info(msg)
      logStream.write(`[Exit] ${msg}\n`)
      logStream.end()
      backendProcess = null
    })
  } catch (e: any) {
    console.error(`Exception starting backend: ${e.message}`)
    log.error(`Exception starting backend: ${e.message}`)
  }
}

// 停止后端
function stopBackend() {
  if (backendProcess) {
    log.info(`Stopping backend process (PID: ${backendProcess.pid})...`)
    
    try {
      if (process.platform === 'win32' && backendProcess.pid) {
        // Windows: 使用 taskkill /T /F 强制杀死进程树
        exec(`taskkill /pid ${backendProcess.pid} /T /F`, (err, _, stderr) => {
          if (err) {
            // 忽略 "没有找到进程" 的错误 (可能是已经退出了)
            if (!stderr.includes('not found')) {
              log.error(`Failed to kill backend tree: ${err.message}`)
            }
          } else {
            log.info('Backend process tree stopped successfully')
          }
        })
      } else {
        // Unix: 发送 SIGTERM
        backendProcess.kill()
      }
    } catch (e: any) {
      log.error(`Error stopping backend: ${e.message}`)
    }
    
    backendProcess = null
  }
}

// IPC 处理器
function setupIpcHandlers() {
  // 打开文件选择对话框
  ipcMain.handle('dialog:openFile', async (_, options) => {
    log.info('IPC: dialog:openFile')
    const result = await dialog.showOpenDialog(mainWindow!, {
      properties: ['openFile'],
      filters: options?.filters || [
        { name: 'Novels', extensions: ['txt', 'docx', 'epub', 'mobi'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    })
    return result
  })

  // 打开文件夹选择对话框
  ipcMain.handle('dialog:openDirectory', async () => {
    log.info('IPC: dialog:openDirectory')
    const result = await dialog.showOpenDialog(mainWindow!, {
      properties: ['openDirectory']
    })
    return result
  })

  // 保存文件对话框
  ipcMain.handle('dialog:saveFile', async (_, options) => {
    log.info('IPC: dialog:saveFile')
    const result = await dialog.showSaveDialog(mainWindow!, {
      filters: options?.filters || [
        { name: 'JSON', extensions: ['json'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    })
    return result
  })

  // 获取应用路径
  ipcMain.handle('app:getPath', (_, name) => {
    return app.getPath(name)
  })

  // 获取应用版本
  ipcMain.handle('app:getVersion', () => {
    return app.getVersion()
  })

  // 获取后端端口
  ipcMain.handle('app:getBackendPort', () => {
    return BACKEND_PORT
  })

  // 打开日志文件夹 (Enhanced)
  ipcMain.handle('log:openFolder', () => {
    const mainLogPath = log.transports.file.getFile().path
    const logDir = path.dirname(mainLogPath)
    
    // Try to copy backend logs to this folder if they are elsewhere (e.g. dev mode)
    if (process.env.VITE_DEV_SERVER_URL) {
      const backendLogPath = path.join(__dirname, '../backend/data/app.log')
      if (fs.existsSync(backendLogPath)) {
        try {
          const dest = path.join(logDir, 'backend-dev.log')
          fs.copyFileSync(backendLogPath, dest)
          log.info(`Copied backend log to ${dest}`)
        } catch (e) {
          log.error(`Failed to copy backend log: ${e}`)
        }
      }
    }

    shell.showItemInFolder(mainLogPath)
    return mainLogPath
  })

  // 最小化窗口
  ipcMain.on('window:minimize', () => {
    mainWindow?.minimize()
  })

  // 最大化/还原窗口
  ipcMain.on('window:maximize', () => {
    if (mainWindow?.isMaximized()) {
      mainWindow.unmaximize()
    } else {
      mainWindow?.maximize()
    }
  })

  // 关闭窗口
  ipcMain.on('window:close', () => {
    mainWindow?.close()
  })
}

// 应用事件处理
app.whenReady().then(async () => {
  setupIpcHandlers()
  
  // 1. 立即分配端口 (极快)
  try {
    BACKEND_PORT = await getFreePort()
    log.info(`Allocated backend port: ${BACKEND_PORT}`)
  } catch (e) {
    log.error(`Failed to allocate port, falling back to 5001: ${e}`)
    BACKEND_PORT = 5001
  }

  // 2. 异步启动后端 (不阻塞 UI)
  startBackend()
  
  // 3. 立即创建窗口 (秒开)
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  stopBackend()
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  stopBackend()
})
