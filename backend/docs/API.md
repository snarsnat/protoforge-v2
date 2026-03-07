# API Reference

## Gateway API

The Gateway API provides REST endpoints for managing ProtoForge.

### Models

#### GET /api/models

List available models.

**Response:**
```json
{
  "models": [
    {
      "name": "gpt-4o",
      "display_name": "GPT-4o",
      "supports_thinking": false,
      "supports_vision": true
    }
  ]
}
```

#### GET /api/models/{name}

Get model details.

### Skills

#### GET /api/skills

List available skills.

**Response:**
```json
{
  "skills": [
    {
      "name": "research",
      "description": "Research any topic deeply",
      "enabled": true,
      "path": "./skills/public/research"
    }
  ]
}
```

#### PUT /api/skills/{name}

Update skill enabled state.

**Request:**
```json
{
  "enabled": true
}
```

### Memory

#### GET /api/memory

Get memory data.

#### GET /api/memory/status

Get memory status.

#### POST /api/memory/reload

Reload memory from disk.

### MCP

#### GET /api/mcp/config

Get MCP configuration.

#### PUT /api/mcp/config

Update MCP configuration.

### Threads

#### POST /api/threads/{thread_id}/uploads

Upload files to thread.

#### GET /api/threads/{thread_id}/uploads/list

List uploaded files.

#### GET /api/threads/{thread_id}/artifacts/{path}

Get artifact file.
