const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  app: {
    getVersion: () => ipcRenderer.invoke('app:getVersion'),
    getEnvironment: () => ipcRenderer.invoke('app:getEnvironment'),
  },
  window: {
    minimize: () => ipcRenderer.invoke('window:minimize'),
    maximize: () => ipcRenderer.invoke('window:maximize'),
    close: () => ipcRenderer.invoke('window:close'),
    isMaximized: () => ipcRenderer.invoke('window:isMaximized'),
  },
  clipboard: {
    writeText: async (text) => {
      await ipcRenderer.invoke('clipboard:writeText', text);
    },
    readText: () => ipcRenderer.invoke('clipboard:readText'),
  },
});
