const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getAppPath: () => ipcRenderer.invoke('get-app-path'),
  getVersion: () => ipcRenderer.invoke('get-version'),
  
  // Notifications
  sendNotification: (title, body) => {
    ipcRenderer.send('show-notification', { title, body });
  },
  
  // Platform info
  getPlatform: () => process.platform,
  
  // Open external links
  openExternal: (url) => {
    ipcRenderer.send('open-external', url);
  },
});

// Handle IPC from main process
ipcRenderer.on('backend-status', (event, status) => {
  console.log('Backend status:', status);
});
