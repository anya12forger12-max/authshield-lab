const { app, BrowserWindow, ipcMain, Menu, shell } = require('electron');
const path = require('path');

const isDev = process.env.NODE_ENV === 'development' || process.env.ELECTRON_DEV === 'true';
const VITE_DEV_SERVER_URL = 'http://localhost:5173';

let mainWindow = null;

const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });

  function createWindow() {
    mainWindow = new BrowserWindow({
      width: 1400,
      height: 900,
      minWidth: 900,
      minHeight: 600,
      show: false,
      title: 'AuthShield Lab',
      icon: path.join(__dirname, '..', 'public', 'icon.png'),
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        sandbox: true,
        preload: path.join(__dirname, 'preload.js'),
      },
    });

    mainWindow.once('ready-to-show', () => {
      mainWindow.show();
    });

    if (isDev) {
      mainWindow.loadURL(VITE_DEV_SERVER_URL);
      mainWindow.webContents.openDevTools({ mode: 'detach' });
    } else {
      mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'));
    }

    mainWindow.on('closed', () => {
      mainWindow = null;
    });

    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });
  }

  app.whenReady().then(() => {
    createWindow();
    buildMenu();

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
      }
    });
  });

  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
      app.quit();
    }
  });

  function buildMenu() {
    const template = [
      {
        label: 'File',
        submenu: [
          { role: 'quit', label: 'Quit AuthShield Lab' },
        ],
      },
      {
        label: 'Edit',
        submenu: [
          { role: 'undo' },
          { role: 'redo' },
          { type: 'separator' },
          { role: 'cut' },
          { role: 'copy' },
          { role: 'paste' },
          { role: 'selectAll' },
        ],
      },
      {
        label: 'View',
        submenu: [
          { role: 'reload', label: 'Reload' },
          { role: 'forceReload', label: 'Force Reload' },
          { role: 'toggleDevTools', label: 'Toggle Developer Tools' },
          { type: 'separator' },
          { role: 'resetZoom', label: 'Reset Zoom' },
          { role: 'zoomIn', label: 'Zoom In' },
          { role: 'zoomOut', label: 'Zoom Out' },
          { type: 'separator' },
          { role: 'togglefullscreen', label: 'Toggle Fullscreen' },
        ],
      },
      {
        label: 'Window',
        submenu: [
          { role: 'minimize', label: 'Minimize' },
          { role: 'zoom', label: 'Zoom' },
          { role: 'close', label: 'Close' },
        ],
      },
      {
        label: 'Help',
        submenu: [
          {
            label: 'AuthShield Lab Documentation',
            click: () => shell.openExternal('https://authshieldlab.dev/docs'),
          },
          {
            label: 'Report Issue',
            click: () => shell.openExternal('https://github.com/authshieldlab/issues'),
          },
          { type: 'separator' },
          {
            label: 'About AuthShield Lab',
            click: () => {
              if (mainWindow) {
                mainWindow.webContents.send('show-about');
              }
            },
          },
        ],
      },
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  }

  ipcMain.handle('app:getVersion', () => app.getVersion());
  ipcMain.handle('app:getEnvironment', () => (isDev ? 'development' : 'production'));

  ipcMain.handle('window:minimize', () => {
    if (mainWindow) mainWindow.minimize();
  });

  ipcMain.handle('window:maximize', () => {
    if (mainWindow) {
      if (mainWindow.isMaximized()) {
        mainWindow.unmaximize();
      } else {
        mainWindow.maximize();
      }
    }
  });

  ipcMain.handle('window:close', () => {
    if (mainWindow) mainWindow.close();
  });

  ipcMain.handle('window:isMaximized', () => {
    return mainWindow ? mainWindow.isMaximized() : false;
  });
}
