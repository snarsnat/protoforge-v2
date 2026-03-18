const { app, BrowserWindow, Menu, Tray, nativeImage, dialog, Notification } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const http = require('http');

// Keep a global reference of the window object
let mainWindow;
let backendProcess = null;
let tray = null;

// Configuration
const PORT = 8001;
const BACKEND_PATH = app.isPackaged 
  ? path.join(process.resourcesPath, 'backend')
  : path.join(__dirname, '..', 'backend');

const APP_PATH = app.isPackaged
  ? path.dirname(process.execPath)
  : path.join(__dirname, '..');

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    title: 'ProtoForge v2',
    icon: path.join(__dirname, 'build', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: false, // Allow local backend requests
    },
    backgroundColor: '#1e1e1e',
    show: false, // Don't show until ready
  });

  // Load the app
  const url = `http://localhost:${PORT}`;
  mainWindow.loadURL(url);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.focus();
  });

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Create menu
  createMenu();
}

function createMenu() {
  const template = [
    {
      label: 'ProtoForge',
      submenu: [
        {
          label: 'About ProtoForge',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About ProtoForge',
              message: 'ProtoForge v2.0.0',
              detail: 'AI-powered prototyping for software, hardware, and hybrid projects.\n\nMade by a 13-year-old.\n\nhttps://github.com/snarsnat/protoforge-v2',
            });
          },
        },
        { type: 'separator' },
        {
          label: 'Quit ProtoForge',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.quit();
          },
        },
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
        { role: 'reload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ],
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'GitHub Repository',
          click: async () => {
            const { shell } = require('electron');
            await shell.openExternal('https://github.com/snarsnat/protoforge-v2');
          },
        },
        {
          label: 'Report Issue',
          click: async () => {
            const { shell } = require('electron');
            await shell.openExternal('https://github.com/snarsnat/protoforge-v2/issues');
          },
        },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

function checkPython() {
  return new Promise((resolve) => {
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const check = spawn(pythonCmd, ['--version']);
    
    check.on('error', () => {
      resolve(false);
    });
    
    check.on('close', (code) => {
      resolve(code === 0);
    });
  });
}

function startBackend() {
  return new Promise((resolve, reject) => {
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const appPath = path.join(APP_PATH, 'backend', 'src', 'gateway', 'app.py');
    
    // Set up environment
    const env = {
      ...process.env,
      PYTHONPATH: BACKEND_PATH,
      PROTOFORGE_APP_PATH: APP_PATH,
    };

    // Start the Python backend
    backendProcess = spawn(pythonCmd, [appPath], {
      cwd: APP_PATH,
      env: env,
      stdio: ['pipe', 'pipe', 'pipe'],
    });

    backendProcess.stdout.on('data', (data) => {
      console.log(`Backend: ${data}`);
      
      // Check if server started successfully
      if (data.toString().includes('Uvicorn running')) {
        resolve(true);
      }
    });

    backendProcess.stderr.on('data', (data) => {
      console.error(`Backend Error: ${data}`);
    });

    backendProcess.on('close', (code) => {
      console.log(`Backend process exited with code ${code}`);
      if (mainWindow) {
        new Notification({
          title: 'ProtoForge Backend Stopped',
          body: `The backend server exited with code ${code}`,
        }).show();
      }
    });

    // Timeout if backend doesn't start
    setTimeout(() => {
      reject(new Error('Backend failed to start within 30 seconds'));
    }, 30000);
  });
}

function waitForServer(maxAttempts = 60) {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    
    const checkServer = () => {
      attempts++;
      
      const req = http.get(`http://localhost:${PORT}`, (res) => {
        if (res.statusCode === 200) {
          resolve(true);
        } else {
          retry();
        }
      });
      
      req.on('error', () => {
        retry();
      });
    };
    
    const retry = () => {
      if (attempts >= maxAttempts) {
        reject(new Error('Server failed to start'));
      } else {
        setTimeout(checkServer, 500);
      }
    };
    
    checkServer();
  });
}

async function setupApp() {
  // Check Python
  const hasPython = await checkPython();
  if (!hasPython) {
    dialog.showErrorBox(
      'Python Not Found',
      'ProtoForge requires Python 3.8+ to be installed.\n\nPlease install Python from https://python.org and try again.'
    );
    app.quit();
    return;
  }

  // Start backend
  try {
    await startBackend();
    await waitForServer();
    console.log('Backend server is ready!');
    
    // Show notification
    new Notification({
      title: 'ProtoForge Ready',
      body: 'Your AI prototyping studio is ready to use!',
    }).show();
    
    // Create window
    createWindow();
  } catch (error) {
    console.error('Failed to start backend:', error);
    dialog.showErrorBox(
      'Backend Error',
      `Failed to start the ProtoForge backend:\n\n${error.message}\n\nPlease check the console for details.`
    );
  }
}

// App lifecycle events
app.whenReady().then(() => {
  setupApp();
});

app.on('window-all-closed', () => {
  // Clean up backend process
  if (backendProcess) {
    backendProcess.kill('SIGTERM');
  }
  
  // On macOS, apps typically stay active until explicitly quit
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    setupApp();
  }
});

app.on('before-quit', () => {
  // Ensure backend is stopped
  if (backendProcess) {
    backendProcess.kill('SIGTERM');
    backendProcess = null;
  }
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  dialog.showErrorBox('ProtoForge Error', `An unexpected error occurred:\n\n${error.message}`);
});
