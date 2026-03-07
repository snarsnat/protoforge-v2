---
name: diagram-generation
description: Generate Mermaid.js diagrams for circuits and components
allowed-tools: bash, write_file, read_file
---

# Diagram Generation Skill

This skill generates Mermaid.js diagrams for hardware circuits and software components.

## Usage

When the user asks for:
- Circuit diagrams
- Wiring diagrams
- Component diagrams
- Architecture diagrams
- Flowcharts

Use the `write_file` tool to create `.md` files with Mermaid.js code blocks.

## Circuit Diagram Template

```mermaid
flowchart TB
    subgraph Power["⚡ Power"]
        USB["🔌 USB 5V"]
        VCC["📍 VCC"]
        GND["📍 GND"]
    end
    
    subgraph MCU["🧠 Controller"]
        PIN["🎛️ GPIO Pins"]
    end
    
    subgraph Components["📟 Components"]
        SENSOR["📡 Sensor"]
        OUTPUT["📤 Output"]
    end
    
    USB --> VCC
    USB --> GND
    VCC --> PIN
    PIN --> SENSOR
    PIN --> OUTPUT
```

## Component Diagram Template

```mermaid
flowchart TB
    subgraph Client["🏠 Client"]
        UI["🖥️ UI"]
    end
    
    subgraph Server["⚙️ Server"]
        API["🔌 API"]
        DB["💾 Database"]
    end
    
    UI --> API
    API --> DB
```

## Output Files

Save diagrams to:
- `/mnt/user-data/outputs/circuit.md` - Circuit diagrams
- `/mnt/user-data/outputs/components.md` - Component diagrams
- `/mnt/user-data/outputs/architecture.md` - Architecture diagrams
