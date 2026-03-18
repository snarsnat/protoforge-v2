const { app, BrowserWindow, Menu, dialog, Notification } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const http = require('http');
const os = require('os');

let mainWindow = null;
let backendProcess = null;
let setupWindow = null;

const PORT = 8001;

// Get user data directory for storing Python deps
function getUserDataPath() {
  return path.join(app.getPath('appData'), 'ProtoForge');
}

function getAppPaths() {
  const isDev = !app.isPackaged;
  const userDataPath = getUserDataPath();
  
  if (isDev) {
    return {
      rootPath: path.join(__dirname, '..'),
      backendPath: path.join(__dirname, '..', 'backend'),
      resourcesPath: path.join(__dirname, '..'),
      venvPath: path.join(userDataPath, 'venv'),
    };
  } else {
    const resourcesPath = process.resourcesPath;
    return {
      rootPath: path.dirname(process.execPath),
      backendPath: path.join(resourcesPath, 'backend'),
      resourcesPath: resourcesPath,
      venvPath: path.join(userDataPath, 'venv'),
    };
  }
}

function createSetupWindow() {
  setupWindow = new BrowserWindow({
    width: 600,
    height: 400,
    resizable: false,
    closable: false,
    title: 'ProtoForge Setup',
    webPreferences: { nodeIntegration: false, contextIsolation: true },
  });
  
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body { 
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
          background: #1e1e1e; color: #fff; 
          display: flex; flex-direction: column; 
          align-items: center; justify-content: center; 
          height: 100vh; margin: 0; padding: 20px;
        }
        h1 { color: #ff3e00; margin-bottom: 10px; }
        p { color: #aaa; text-align: center; line-height: 1.5; }
        .progress { 
          width: 100%; max-width: 400px; height: 4px; 
          background: #333; border-radius: 2px; margin: 20px 0;
          overflow: hidden;
        }
        .bar { 
          height: 100%; background: #ff3e00; 
          width: 0%; transition: width 0.3s;
        }
        .log { 
          font-family: monospace; font-size: 11px; 
          color: #888; max-height: 150px; overflow-y: auto;
          background: #111; padding: 10px; border-radius: 4px;
          width: 100%; max-width: 500px;
        }
      </style>
    </head>
    <body>
      <h1>⚡ ProtoForge Setup</h1>
      <p id="status">Setting up Python environment...</p>
      <div class="progress"><div class="bar" id="bar"></div></div>
      <div class="log" id="log"></div>
    </body>
    </html>
  `;
  
  setupWindow.loadURL('data:text/html,' + encodeURIComponent(html));
}

function updateSetup(status, progress, logLine) {
  if (setupWindow) {
    setupWindow.webContents.send('update', { status, progress, logLine });
  }
}

function createWindow() {
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

  mainWindow.loadURL(`http://localhost:${PORT}`);

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.focus();
    if (setupWindow) {
      setupWindow.close();
      setupWindow = null;
    }
  });

  mainWindow.on('closed', () => { mainWindow = null; });
  createMenu();
}

function createMenu() {
  const template = [
    {
      label: 'ProtoForge',
      submenu: [
        {
          label: 'About ProtoForge',
          click: () => dialog.showMessageBox(mainWindow, {
            type: 'info', title: 'About ProtoForge', message: 'ProtoForge v2.0.0',
            detail: 'AI-powered prototyping for software, hardware, and hybrid projects.\n\nMade by a 13-year-old.\n\nhttps://github.com/snarsnat/protoforge-v2',
          }),
        },
        { type: 'separator' },
        { label: 'Quit ProtoForge', accelerator: 'CmdOrCtrl+Q', click: () => app.quit() },
      ],
    },
    { label: 'Edit', submenu: [{ role: 'undo' }, { role: 'redo' }, { type: 'separator' }, { role: 'cut' }, { role: 'copy' }, { role: 'paste' }, { role: 'selectAll' }] },
    { label: 'View', submenu: [{ role: 'reload' }, { role: 'toggleDevTools' }, { type: 'separator' }, { role: 'resetZoom' }, { role: 'zoomIn' }, { role: 'zoomOut' }, { type: 'separator' }, { role: 'togglefullscreen' }] },
    { label: 'Help', submenu: [{ label: 'GitHub Repository', click: async () => require('electron').shell.openExternal('https://github.com/snarsnat/protoforge-v2') }] },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

function checkPython() {
  return new Promise((resolve) => {
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const check = spawn(pythonCmd, ['--version']);
    check.on('error', () => resolve(false));
    check.on('close', (code) => resolve(code === 0));
  });
}

function setupPythonEnvironment(paths) {
  return new Promise((resolve, reject) => {
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const venvPath = paths.venvPath;
    const requirementsPath = path.join(paths.resourcesPath, 'requirements.txt');
    
    console.log('Setting up Python environment...');
    console.log('  Venv path:', venvPath);
    console.log('  Requirements:', requirementsPath);
    
    // Check if venv already exists and is valid
    const pipPath = process.platform === 'win32' 
      ? path.join(venvPath, 'Scripts', 'pip')
      : path.join(venvPath, 'bin', 'pip');
    
    if (fs.existsSync(pipPath)) {
      console.log('Venv exists, checking if dependencies are installed...');
      const checkPip = spawn(pipPath, ['show', 'fastapi']);
      checkPip.on('close', (code) => {
        if (code === 0) {
          console.log('Dependencies already installed');
          resolve(venvPath);
        } else {
          console.log('Reinstalling dependencies...');
          installDeps();
        }
      });
      return;
    }
    
    installDeps();
    
    function installDeps() {
      // Create venv
      console.log('Creating virtual environment...');
      const venv = spawn(pythonCmd, ['-m', 'venv', venvPath]);
      
      venv.on('close', (code) => {
        if (code !== 0) {
          reject(new Error('Failed to create virtual environment'));
          return;
        }
        
        // Install dependencies
        console.log('Installing dependencies...');
        const pip = process.platform === 'win32'
          ? path.join(venvPath, 'Scripts', 'pip')
          : path.join(venvPath, 'bin', 'pip');
        
        const install = spawn(pip, ['install', '-r', requirementsPath]);
        
        install.stdout.on('data', (data) => {
          console.log('pip:', data.toString().trim());
        });
        
        install.stderr.on('data', (data) => {
          console.log('pip:', data.toString().trim());
        });
        
        install.on('close', (code) => {
          if (code === 0) {
            console.log('Dependencies installed');
            resolve(venvPath);
          } else {
            reject(new Error('Failed to install dependencies'));
          }
        });
      });
    }
  });
}

function startBackend(paths, useVenv = true) {
  return new Promise((resolve, reject) => {
    let pythonCmd;
    
    if (useVenv && process.platform !== 'win32') {
      pythonCmd = path.join(paths.venvPath, 'bin', 'python');
    } else if (useVenv && process.platform === 'win32') {
      pythonCmd = path.join(paths.venvPath, 'Scripts', 'python.exe');
    } else {
      pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    }
    
    const appPath = path.join(paths.backendPath, 'src', 'gateway', 'app.py');
    
    console.log('Starting backend...');
    console.log('  Python:', pythonCmd);
    console.log('  App:', appPath);
    
    if (!fs.existsSync(appPath)) {
      reject(new Error(`Backend not found: ${appPath}`));
      return;
    }
    
    const env = {
      ...process.env,
      PYTHONPATH: paths.backendPath,
      PROTOFORGE_APP_PATH: paths.resourcesPath,
      PYTHONUNBUFFERED: '1',
    };

    backendProcess = spawn(pythonCmd, [appPath], {
      cwd: paths.resourcesPath,
      env: env,
      stdio: ['pipe', 'pipe', 'pipe'],
    });

    let started = false;

    backendProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log('Backend:', output);
      
      if (output.includes('Uvicorn running') || output.includes('Application startup complete')) {
        started = true;
        resolve(true);
      }
    });

    backendProcess.stderr.on('data', (data) => {
      const error = data.toString();
      console.error('Backend:', error);
      
      if (error.includes('ModuleNotFoundError') && useVenv) {
        // Fallback to system Python
        console.log('Venv failed, trying system Python...');
        backendProcess.kill('SIGTERM');
        startBackend(paths, false).then(resolve).catch(reject);
      }
    });

    backendProcess.on('close', (code) => {
      if (!started) reject(new Error(`Backend exited with code ${code}`));
    });

    setTimeout(() => { if (!started) reject(new Error('Backend timeout')); }, 90000);
  });
}

function waitForServer(maxAttempts = 180) {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const check = () => {
      attempts++;
      http.get(`http://localhost:${PORT}`, (res) => {
        res.statusCode === 200 ? resolve(true) : retry();
      }).on('error', () => retry());
    };
    const retry = () => attempts >= maxAttempts ? reject(new Error('Server timeout')) : setTimeout(check, 500);
    check();
  });
}

async function setupApp() {
  const paths = getAppPaths();
  
  console.log('=== ProtoForge ===');
  console.log('Mode:', app.isPackaged ? 'Production' : 'Development');
  console.log('Resources:', paths.resourcesPath);
  console.log('Venv:', paths.venvPath);
  
  // Ensure user data directory exists
  const userDataPath = getUserDataPath();
  if (!fs.existsSync(userDataPath)) {
    fs.mkdirSync(userDataPath, { recursive: true });
  }
  
  const hasPython = await checkPython();
  if (!hasPython) {
    dialog.showErrorBox('Python Required', 'Please install Python 3.8+ from https://python.org');
    app.quit();
    return;
  }
  
  // Show setup window
  createSetupWindow();
  
  try {
    // Setup Python environment
    await setupPythonEnvironment(paths);
    
    // Start backend
    await startBackend(paths);
    await waitForServer();
    
    console.log('Ready!');
    new Notification({ title: 'ProtoForge Ready', body: 'Let\'s build something awesome!' }).show();
    
    createWindow();
  } catch (error) {
    console.error('Error:', error);
    
    let msg = `Setup failed:\n\n${error.message}`;
    if (error.message.includes('ModuleNotFoundError')) {
      msg += `\n\nManual fix:\n1. Open Terminal\n2. Run:\n\ncd "${paths.resourcesPath}"\npip3 install -r requirements.txt\n\n3. Open ProtoForge again`;
    }
    
    dialog.showErrorBox('ProtoForge Setup Error', msg);
    if (setupWindow) setupWindow.close();
  }
}

app.whenReady().then(() => setupApp());

app.on('window-all-closed', () => {
  if (backendProcess) { backendProcess.kill('SIGTERM'); backendProcess = null; }
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => { if (mainWindow === null) setupApp(); });

app.on('before-quit', () => {
  if (backendProcess) { backendProcess.kill('SIGTERM'); backendProcess = null; }
});

process.on('uncaughtException', (e) => console.error('Uncaught:', e));
