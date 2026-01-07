# MCP Configuration Management

## Overview

The MCP configuration management capability provides centralized configuration handling for Model Context Protocol services, including environment variables, mcp.json schema, runtime settings, and multi-environment support.

**Keywords**: mcp, configuration, settings, environment, mcp.json, config, management, runtime, validation, safeguards

## Purpose

Manages MCP service configuration through:
- **Configuration Files**: mcp.json, config.yaml, settings.py
- **Environment Variables**: .env file support with validation
- **Runtime Configuration**: Dynamic config reload and updates
- **Multi-Environment**: Dev, staging, production configurations
- **Schema Validation**: Type-safe configuration with validation

## Architecture

### Configuration Hierarchy

```
┌─────────────────────────────────────┐
│   Environment Variables (.env)      │
│   (highest priority)                │
└─────────────┬───────────────────────┘
              │ overrides
              ▼
┌─────────────────────────────────────┐
│   mcp.json Configuration            │
│   (MCP-specific settings)           │
└─────────────┬───────────────────────┘
              │ overrides
              ▼
┌─────────────────────────────────────┐
│   config.yaml / settings.py         │
│   (application defaults)            │
└─────────────────────────────────────┘
```

### Configuration Loading Flow

```python
# Pseudocode for configuration loading
def load_config():
    # 1. Load default configuration
    config = load_defaults()
    
    # 2. Load config files
    config.update(load_yaml("config.yaml"))
    config.update(load_json("mcp.json"))
    
    # 3. Apply environment overrides
    config.update(load_env_vars())
    
    # 4. Validate configuration
    validate_config_schema(config)
    
    return config
```

## Configuration Files

### mcp.json Schema

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "title": "MCP Service Configuration",
  "type": "object",
  "properties": {
    "server": {
      "type": "object",
      "properties": {
        "host": {"type": "string", "default": "0.0.0.0"},
        "port": {"type": "integer", "minimum": 1024, "maximum": 65535},
        "workers": {"type": "integer", "minimum": 1},
        "timeout_seconds": {"type": "integer", "minimum": 1}
      },
      "required": ["port"]
    },
    "capabilities": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "enabled": {"type": "boolean", "default": true},
          "version": {"type": "string"}
        },
        "required": ["name", "version"]
      }
    },
    "logging": {
      "type": "object",
      "properties": {
        "level": {
          "type": "string",
          "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        },
        "format": {"type": "string"}
      }
    }
  },
  "required": ["server", "capabilities"]
}
```

### Example mcp.json

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "workers": 4,
    "timeout_seconds": 30
  },
  "capabilities": [
    {
      "name": "code_analysis",
      "version": "1.0.0",
      "enabled": true
    },
    {
      "name": "documentation",
      "version": "2.1.0",
      "enabled": false
    }
  ],
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  },
  "auth": {
    "enabled": true,
    "api_key_header": "X-API-Key"
  }
}
```

### Environment Variables (.env)

```bash
# .env file
MCP_SERVER_PORT=8080
MCP_SERVER_HOST=0.0.0.0
MCP_WORKERS=4
MCP_LOG_LEVEL=INFO

# Database
MCP_DB_HOST=localhost
MCP_DB_PORT=5432
MCP_DB_NAME=mcp_db

# Authentication
MCP_API_KEY=your-secret-api-key
MCP_JWT_SECRET=your-jwt-secret

# Feature flags
MCP_ENABLE_CACHING=true
MCP_ENABLE_METRICS=true
```

### Python Settings Module

```python
# settings.py
from pydantic import BaseSettings, Field

class MCPSettings(BaseSettings):
    """MCP Service Configuration."""
    
    # Server settings
    server_host: str = Field("0.0.0.0", env="MCP_SERVER_HOST")
    server_port: int = Field(8080, env="MCP_SERVER_PORT", gt=1024, le=65535)
    workers: int = Field(4, env="MCP_WORKERS", gt=0)
    
    # Database settings
    db_host: str = Field("localhost", env="MCP_DB_HOST")
    db_port: int = Field(5432, env="MCP_DB_PORT")
    db_name: str = Field("mcp_db", env="MCP_DB_NAME")
    
    # Authentication
    api_key: str = Field(..., env="MCP_API_KEY")
    jwt_secret: str = Field(..., env="MCP_JWT_SECRET")
    
    # Feature flags
    enable_caching: bool = Field(True, env="MCP_ENABLE_CACHING")
    enable_metrics: bool = Field(True, env="MCP_ENABLE_METRICS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Usage
settings = MCPSettings()
```

## Usage Examples

### Example 1: Load Configuration

```python
import json
from pathlib import Path

def load_mcp_config(config_path: str = "mcp.json"):
    """Load MCP configuration with validation."""
    with open(config_path) as f:
        config = json.load(f)
    
    # Validate required fields
    assert "server" in config, "Missing 'server' section"
    assert "port" in config["server"], "Missing 'server.port'"
    
    return config

# Usage
config = load_mcp_config()
print(f"Server port: {config['server']['port']}")
```

### Example 2: Environment Override

```python
import os
from typing import Any, Dict

def apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to config."""
    
    # Server overrides
    if "MCP_SERVER_PORT" in os.environ:
        config["server"]["port"] = int(os.environ["MCP_SERVER_PORT"])
    
    if "MCP_SERVER_HOST" in os.environ:
        config["server"]["host"] = os.environ["MCP_SERVER_HOST"]
    
    # Logging overrides
    if "MCP_LOG_LEVEL" in os.environ:
        config.setdefault("logging", {})["level"] = os.environ["MCP_LOG_LEVEL"]
    
    return config

# Usage
config = load_mcp_config()
config = apply_env_overrides(config)
```

### Example 3: Dynamic Configuration Reload

```python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigReloadHandler(FileSystemEventHandler):
    def __init__(self, config_path: str, on_reload_callback):
        self.config_path = config_path
        self.callback = on_reload_callback
    
    def on_modified(self, event):
        if event.src_path.endswith(self.config_path):
            print(f"Configuration changed, reloading...")
            new_config = load_mcp_config(self.config_path)
            self.callback(new_config)

def setup_config_watch(config_path: str, callback):
    """Watch configuration file for changes."""
    event_handler = ConfigReloadHandler(config_path, callback)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()
    return observer

# Usage
def on_config_reload(new_config):
    print(f"Updated configuration: {new_config}")

observer = setup_config_watch("mcp.json", on_config_reload)
```

### Example 4: Multi-Environment Configuration

```python
import os

class ConfigManager:
    """Manages multi-environment configurations."""
    
    def __init__(self):
        self.env = os.getenv("MCP_ENV", "development")
        self.config = self._load_config()
    
    def _load_config(self):
        """Load environment-specific configuration."""
        base_config = self._load_json("config.base.json")
        env_config = self._load_json(f"config.{self.env}.json")
        
        # Merge configurations (env overrides base)
        return {**base_config, **env_config}
    
    def _load_json(self, path: str):
        """Load JSON config file."""
        try:
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)

# Usage
config_mgr = ConfigManager()
db_host = config_mgr.get("database.host", "localhost")
```

## Integration with Audit Pipeline

### Detection Command

```bash
# Check configuration capability
python scripts/space_traversal/audit_runner.py explain mcp-configuration

# Run full audit
python scripts/space_traversal/audit_runner.py run
```

### Programmatic Detection

```python
from scripts.space_traversal.detectors import mcp_configuration

# Run detector
file_index = {
    "files": [
        {"path": "mcp.json"},
        {"path": ".env"},
        {"path": "config.yaml"},
        {"path": "src/services/settings.py"}
    ]
}

result = mcp_configuration.detect(file_index)
print(f"Found patterns: {result['found_patterns']}")
print(f"Config types: {result['meta']['config_types']}")
```

## Best Practices

### Configuration Security

1. **Never Commit Secrets**
   ```bash
   # .gitignore
   .env
   .env.local
   .env.*.local
   *secret*
   *key*
   ```

2. **Use Environment Variables for Secrets**
   ```python
   # Good
   api_key = os.getenv("MCP_API_KEY")
   
   # Avoid
   api_key = "hardcoded-secret-key"
   ```

3. **Encrypt Sensitive Configuration**
   ```python
   from cryptography.fernet import Fernet
   
   def encrypt_config(config: dict, key: bytes) -> bytes:
       f = Fernet(key)
       return f.encrypt(json.dumps(config).encode())
   ```

### Configuration Validation

1. **Validate on Load**
   ```python
   from jsonschema import validate
   
   schema = {...}  # JSON schema
   validate(instance=config, schema=schema)
   ```

2. **Type Checking**
   ```python
   from pydantic import BaseModel, ValidationError
   
   class Config(BaseModel):
       port: int
       host: str
   
   try:
       Config(**config)
   except ValidationError as e:
       print(f"Invalid config: {e}")
   ```

3. **Range Validation**
   ```python
   assert 1024 <= config["port"] <= 65535, "Invalid port range"
   ```

### Configuration Documentation

1. **Document All Settings**: Provide descriptions and examples
2. **Include Defaults**: Specify default values clearly
3. **Show Environment Variables**: Document env var names and mappings
4. **Provide Examples**: Include example configurations for common scenarios

## Troubleshooting

### Issue: Configuration Not Found

**Solution**:
```python
from pathlib import Path

config_path = Path("mcp.json")
if not config_path.exists():
    print(f"Config not found at {config_path.absolute()}")
    config_path = Path("/etc/mcp/mcp.json")  # Fallback
```

### Issue: Invalid JSON

**Solution**:
```python
import json

try:
    config = json.load(f)
except json.JSONDecodeError as e:
    print(f"Invalid JSON at line {e.lineno}: {e.msg}")
```

### Issue: Missing Environment Variables

**Solution**:
```python
required_vars = ["MCP_API_KEY", "MCP_DB_HOST"]
missing = [var for var in required_vars if var not in os.environ]
if missing:
    raise ValueError(f"Missing required environment variables: {missing}")
```

## Performance Considerations

- **Config Caching**: Cache loaded configuration to avoid repeated file I/O
- **Lazy Loading**: Load configuration sections on-demand for large configs
- **Hot Reload**: Use file watchers instead of polling for configuration changes

## Monitoring

### Configuration Audit Trail

```python
import logging

logger = logging.getLogger(__name__)

def log_config_change(key: str, old_value, new_value):
    logger.info(f"Config changed: {key} = {old_value} → {new_value}")
```

### Configuration Drift Detection

```bash
# Compare production config against baseline
diff config.production.json config.baseline.json
```

## Related Capabilities

- **mcp-schema-validation**: Configuration schema validation
- **mcp-security-safeguards**: Secure configuration handling
- **documentation-system**: Configuration documentation

## Safeguards

1. **Validation**: All configuration validated on load
2. **Type Safety**: Strong typing with Pydantic
3. **Bounds Checking**: Port ranges, worker counts validated
4. **Secret Management**: Environment variables for sensitive data
5. **Error Handling**: Graceful degradation with defaults

---

**Last Updated**: 2024-12-09  
**Capability ID**: mcp-configuration
