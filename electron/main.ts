import { app, BrowserWindow, ipcMain, dialog, shell } from 'electron'
import { spawn, ChildProcess } from 'child_process'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'
import log from 'electron-log/main'

// Initialize logger
log.initialize()
log.info('App starting...')

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// 环境变量
process.env.DIST = path.join(__dirname, '../dist')
process.env.VITE_PUBLIC = app.isPackaged
  ? process.env.DIST
  : path.join(__dirname, '../public')

let mainWindow: BrowserWindow | null = null
let backendProcess: ChildProcess | null = null

// 后端服务器端口
const BACKEND_PORT = 5001

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
function startBackend() {
  if (process.env.VITE_DEV_SERVER_URL) {
    // 开发环境：后端由 npm script 单独启动
    log.info('Development mode: Backend should be started separately')
    return
  }

  const backendPath = app.isPackaged
    ? path.join(process.resourcesPath, 'backend')
    : path.join(__dirname, '../backend')

  const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3'

  log.info(`Starting backend from: ${backendPath}`)

  backendProcess = spawn(pythonExecutable, ['main.py'], {
    cwd: backendPath,
    env: {
      ...process.env,
      APP_PORT: String(BACKEND_PORT)
    },
    stdio: ['pipe', 'pipe', 'pipe']
  })

  backendProcess.stdout?.on('data', (data) => {
    const msg = data.toString().trim()
    console.log(`Backend: ${msg}`)
    log.info(`[Backend] ${msg}`)
  })

  backendProcess.stderr?.on('data', (data) => {
    const msg = data.toString().trim()
    console.error(`Backend Error: ${msg}`)
    log.error(`[Backend Error] ${msg}`)
  })

  backendProcess.on('close', (code) => {
    log.info(`Backend process exited with code ${code}`)
    backendProcess = null
  })
}

// 停止后端
function stopBackend() {
  if (backendProcess) {
    log.info('Stopping backend process...')
    backendProcess.kill()
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
app.whenReady().then(() => {
  setupIpcHandlers()
  startBackend()
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
