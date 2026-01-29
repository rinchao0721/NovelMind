import { contextBridge, ipcRenderer } from 'electron'

// 暴露安全的 API 给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 对话框
  openFile: (options?: { filters?: Array<{ name: string; extensions: string[] }> }) =>
    ipcRenderer.invoke('dialog:openFile', options),
  openDirectory: () => ipcRenderer.invoke('dialog:openDirectory'),
  saveFile: (options?: { filters?: Array<{ name: string; extensions: string[] }> }) =>
    ipcRenderer.invoke('dialog:saveFile', options),

  // 应用信息
  getPath: (name: string) => ipcRenderer.invoke('app:getPath', name),
  getVersion: () => ipcRenderer.invoke('app:getVersion'),
  getBackendPort: () => ipcRenderer.invoke('app:getBackendPort'),
  openLogFolder: () => ipcRenderer.invoke('log:openFolder'),

  // 窗口控制
  minimize: () => ipcRenderer.send('window:minimize'),
  maximize: () => ipcRenderer.send('window:maximize'),
  close: () => ipcRenderer.send('window:close'),

  // 平台信息
  platform: process.platform
})

// 类型声明
declare global {
  interface Window {
    electronAPI: {
      openFile: (options?: { filters?: Array<{ name: string; extensions: string[] }> }) => Promise<Electron.OpenDialogReturnValue>
      openDirectory: () => Promise<Electron.OpenDialogReturnValue>
      saveFile: (options?: { filters?: Array<{ name: string; extensions: string[] }> }) => Promise<Electron.SaveDialogReturnValue>
      getPath: (name: string) => Promise<string>
      getVersion: () => Promise<string>
      getBackendPort: () => Promise<number>
      openLogFolder: () => Promise<string>
      minimize: () => void
      maximize: () => void
      close: () => void
      platform: NodeJS.Platform
    }
  }
}
