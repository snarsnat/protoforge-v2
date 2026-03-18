const { app, BrowserWindow, Menu, dialog, Notification } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const http = require('http');

// Keep a global reference of the window object
let mainWindow = null;
let backendProcess = null;

// Configuration
const PORT = 8001;

// Get the correct paths for packaged vs development
function getAppPaths() {
  const isDev = !app.isPackaged;
  
  if (isDev) {
    // Development: go up from desktop/ to protoforge-v2/
    return {
      rootPath: path.join(__dirname, '..'),
      backendPath: path.join(__dirname, '..', 'backend'),
    };
  } else {
    // Packaged: resources are in Contents/Resources/
    return {
      rootPath: path.dirname(process.execPath),
      backendPath: path.join(process.resourcesPath, 'backend'),
    };
  }
}

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
      webSecurity: false,
    },
    backgroundColor: '#1e1e1e',
    show: false,
  });

  // Load the app
  const url = `http://localhost:${PORT}`;
  console.log('Loading URL:', url);
  mainWindow.loadURL(url);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    console.log('Window ready to show');
    mainWindow.show();
    mainWindow.focus();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

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
          click: () => app.quit(),
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
    
    check.on('error', () => resolve(false));
    check.on('close', (code) => resolve(code === 0));
  });
}

function startBackend(paths) {
  return new Promise((resolve, reject) => {
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const appPath = path.join(paths.backendPath, 'src', 'gateway', 'app.py');
    
    console.log('Starting backend...');
    console.log('  Python:', pythonCmd);
    console.log('  App path:', appPath);
    console.log('  Root path:', paths.rootPath);
    console.log('  Backend path:', paths.backendPath);
    
    // Check if app.py exists
    if (!fs.existsSync(appPath)) {
      reject(new Error(`Backend app not found at: ${appPath}`));
      return;
    }
    
    // Set up environment
    const env = {
      ...process.env,
      PYTHONPATH: paths.backendPath,
      PROTOFORGE_APP_PATH: paths.rootPath,
      PYTHONUNBUFFERED: '1',
    };

    // Start the Python backend
    backendProcess = spawn(pythonCmd, [appPath], {
      cwd: paths.rootPath,
      env: env,
      stdio: ['pipe', 'pipe', 'pipe'],
    });

    let started = false;
    let errorMessage = '';

    backendProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log('Backend:', output);
      
      // Check for successful startup
      if (output.includes('Uvicorn running') || output.includes('Application startup complete')) {
        started = true;
        resolve(true);
      }
    });

    backendProcess.stderr.on('data', (data) => {
      const error = data.toString();
      console.error('Backend Error:', error);
      errorMessage += error;
      
      // Check for common errors
      if (error.includes('ModuleNotFoundError') || error.includes('ImportError')) {
        reject(new Error(`Python module not found. Please run:\n\ncd "${paths.rootPath}"\npip3 install -r requirements.txt\n\n${error}`));
      }
    });

    backendProcess.on('close', (code) => {
      console.log(`Backend process exited with code ${code}`);
      if (!started) {
        reject(new Error(`Backend exited with code ${code}\n\n${errorMessage || 'Check console for details'}`));
      }
    });

    // Timeout after 60 seconds
    setTimeout(() => {
      if (!started) {
        reject(new Error('Backend failed to start within 60 seconds. Check console for errors.'));
      }
    }, 60000);
  });
}

function waitForServer(maxAttempts = 120) {
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
      
      req.on('error', () => retry());
    };
    
    const retry = () => {
      if (attempts >= maxAttempts) {
        reject(new Error('Server failed to start after 60 seconds'));
      } else {
        setTimeout(checkServer, 500);
      }
    };
    
    checkServer();
  });
}

async function setupApp() {
  const paths = getAppPaths();
  
  console.log('=== ProtoForge Desktop App ===');
  console.log('Mode:', app.isPackaged ? 'Production' : 'Development');
  console.log('Root path:', paths.rootPath);
  console.log('Backend path:', paths.backendPath);
  
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
    await startBackend(paths);
    console.log('Backend started successfully!');
    
    await waitForServer();
    console.log('Server is ready!');
    
    // Show notification
    new Notification({
      title: 'ProtoForge Ready',
      body: 'Your AI prototyping studio is ready to use!',
    }).show();
    
    createWindow();
  } catch (error) {
    console.error('Failed to start backend:', error);
    
    let errorMsg = `Failed to start the ProtoForge backend:\n\n${error.message}`;
    
    // Add helpful tips based on error
    if (error.message.includes('ModuleNotFoundError') || error.message.includes('pip')) {
      errorMsg += '\n\nTo fix this:\n1. Open Terminal\n2. Run: cd ' + paths.rootPath + '\n3. Run: pip3 install -r requirements.txt\n4. Try opening ProtoForge again';
    } else if (error.message.includes('within')) {
      errorMsg += '\n\nThe backend is taking too long to start. This could be because:\n- Python dependencies are missing\n- Port 8001 is already in use\n- There\'s an error in the backend code\n\nCheck the console (Cmd+Option+I) for details.';
    }
    
    dialog.showErrorBox('ProtoForge Backend Error', errorMsg);
    
    // Keep app open so user can see error and check console
    // Don't quit immediately
  }
}

// App lifecycle events
app.whenReady().then(() => {
  setupApp();
});

app.on('window-all-closed', () => {
  // Clean up backend process
  if (backendProcess) {
    console.log('Killing backend process...');
    backendProcess.kill('SIGTERM');
    backendProcess = null;
  }
  
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
  if (backendProcess) {
    backendProcess.kill('SIGTERM');
    backendProcess = null;
  }
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});
