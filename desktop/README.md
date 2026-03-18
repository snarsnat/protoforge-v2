# ProtoForge Desktop App

Package ProtoForge v2 as a native macOS application (.dmg installer).

## Prerequisites

- Node.js 18+ installed
- Python 3.8+ installed
- npm or yarn

## Building the .dmg

### Quick Build

```bash
cd desktop
npm install
npm run build:dmg
```

The .dmg file will be created in `desktop/dist/ProtoForge-2.0.0.dmg`

### Build Options

```bash
# Build for current Mac architecture only
npm run build:dmg

# Build universal (Intel + Apple Silicon)
npm run build

# Build without codesigning (for testing)
npm run pack
```

## Distribution

### Unsigned (Development/Testing)
The .dmg can be distributed for testing, but users will see a warning on first launch.

**To open on macOS:**
1. Double-click the .dmg
2. Drag ProtoForge to Applications folder
3. When opening, if you see "cannot be opened":
   - Go to System Preferences → Security & Privacy
   - Click "Open Anyway"
   - Or run: `xattr -rd com.apple.quarantine /Applications/ProtoForge.app`

### Signed (Distribution)
For distribution without warnings, you need an Apple Developer certificate:

1. Get an Apple Developer account ($99/year)
2. Create a Developer ID Application certificate
3. Add to `package.json`:
```json
"build": {
  "mac": {
    "identity": "Developer ID Application: Your Name (TEAM_ID)"
  }
}
```

## File Structure

```
desktop/
├── main.js              # Electron main process
├── preload.js           # Secure context bridge
├── package.json         # Dependencies + electron-builder config
├── build/
│   ├── entitlements.mac.plist  # macOS permissions
│   └── icon.icns        # App icon (generated)
└── dist/                # Built .dmg appears here
```

## What's Included

The .dmg installer includes:
- ProtoForge Electron app
- Python backend (bundled)
- All templates and static files
- Auto-starts backend on launch

## System Requirements

- macOS 10.13+ (High Sierra or later)
- Python 3.8+ (app will check on launch)
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space

## Troubleshooting

### Backend won't start
- Ensure Python 3.8+ is installed: `python3 --version`
- Check if port 8001 is available: `lsof -i :8001`

### App shows security warning
- This is normal for unsigned apps
- Right-click → Open, then click "Open Anyway"
- Or use: `xattr -rd com.apple.quarantine /Applications/ProtoForge.app`

### Build fails
- Clear node_modules: `rm -rf node_modules && npm install`
- Update electron-builder: `npm install electron-builder@latest --save-dev`

## License

MIT - See main repository LICENSE
