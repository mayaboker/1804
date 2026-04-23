# Logging Setup Summary

This project uses Python `logging` with:

- One shared rotating log file
- Colored console output
- Per-module log level overrides from config

## Files Involved

- `logger.py`
  - Defines `setup_logging(app_name, level, module_levels)`
  - Configures root logger, console handler, and rotating file handler
  - Applies per-module levels from `module_levels`
- `orchestrator.py`
  - Entry point that loads `logging_config.json`
  - Parses string levels (for example `"INFO"`, `"CRITICAL"`) into `logging` constants
  - Calls `setup_logging(...)` with root + per-module levels
- `zmq_pub_sub.py`
  - Uses `log = logging.getLogger(__name__)`
  - Emits logs with `log.debug/info/warning/error/exception`
  - Module name resolves to `zmq_pub_sub`, matching the override key
- `logging_config.json`
  - Runtime logging configuration (no code change needed)
  - Defines `app_name`, `root_level`, and `module_levels`
  - Supports module alias values `"root_level"`, `"root"`, or `"inherit"` to follow root

## How It Works

1. `orchestrator.py` loads `logging_config.json`.
2. `logger.py` creates:
   - Console handler (colored)
   - File handler (`<app_name>.log`)
3. `root_level` sets the default for all modules.
4. `module_levels` overrides selected modules.
5. Each module logs through its own named logger (`logging.getLogger(__name__)`).

## Log Levels (Quick Reference)

Order from most verbose to most severe:

`DEBUG` < `INFO` < `WARNING` < `ERROR` < `CRITICAL`

- `DEBUG`: developer/troubleshooting details
- `INFO`: normal lifecycle events (start/stop/connect)
- `WARNING`: unexpected but recoverable conditions
- `ERROR`: operation failed
- `CRITICAL`: severe failure

## Example Configuration (`logging_config.json`)

```json
{
  "app_name": "my_project",
  "root_level": "INFO",
  "module_levels": {
    "orchestrator": "root_level",
    "zmq_pub_sub": "CRITICAL"
  }
}
```

Result:

- All logs go to one file: `my_project.log`
- Console shows module logs according to each module's configured level
- You can change logging behavior by editing only `logging_config.json`
