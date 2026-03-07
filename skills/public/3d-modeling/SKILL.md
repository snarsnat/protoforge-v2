---
name: 3d-modeling
description: Generate 3D model specifications for hardware prototypes
allowed-tools: bash, write_file, read_file
---

# 3D Modeling Skill

This skill generates 3D model specifications for hardware prototypes.

## Usage

When the user asks for:
- 3D models
- Hardware enclosures
- PCB layouts
- Mechanical designs

Generate OBJ files and JSON specifications.

## Output Format

### JSON Specification

```json
{
  "type": "enclosure",
  "dimensions": {
    "width": 100,
    "height": 50,
    "depth": 80
  },
  "material": "ABS plastic",
  "color": "#2d3436",
  "components": [
    {
      "name": "display",
      "type": "cutout",
      "position": {"x": 10, "y": 5, "z": 0}
    }
  ]
}
```

### OBJ File

Generate simple OBJ format 3D models:

```
# ProtoForge 3D Model
v -50.0 0.0 -40.0
v 50.0 0.0 -40.0
v 50.0 0.0 40.0
v -50.0 0.0 40.0
v -50.0 25.0 -40.0
v 50.0 25.0 -40.0
v 50.0 25.0 40.0
v -50.0 25.0 40.0

f 1 2 3 4
f 5 6 7 8
...
```

## Output Files

Save to:
- `/mnt/user-data/outputs/model.obj` - 3D model
- `/mnt/user-data/outputs/model.json` - Specification
- Present files when complete
