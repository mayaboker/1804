import signal
import sys
import time
import logging
import json
from pathlib import Path
from zmq_pub_sub import ZMQSubscriberModule
from logger import setup_logging
# from your_other_modules import FaceDetector, Tracker


def load_logging_config(config_path="logging_config.json"):
    defaults = {
        "app_name": "my_project",
        "root_level": "INFO",
        "module_levels": {
            "orchestrator": "INFO",
            "zmq_pub_sub": "INFO",
        },
    }

    path = Path(config_path)
    if not path.exists():
        return defaults

    with path.open("r") as f:
        config = json.load(f)

    return {
        "app_name": config.get("app_name", defaults["app_name"]),
        "root_level": config.get("root_level", defaults["root_level"]),
        "module_levels": config.get("module_levels", defaults["module_levels"]),
    }


def parse_log_level(level_name, fallback=logging.INFO):
    if not isinstance(level_name, str):
        return fallback
    return getattr(logging, level_name.upper(), fallback)


def resolve_module_level(level_name, root_level):
    """Resolve per-module level with support for 'root_level' alias."""
    if isinstance(level_name, str) and level_name.strip().lower() in (
        "root_level",
        "root",
        "inherit",
    ):
        return root_level
    return parse_log_level(level_name, root_level)

def main():
    log_cfg = load_logging_config("logging_config.json")
    root_level = parse_log_level(log_cfg["root_level"], logging.INFO)
    module_levels = {
        name: resolve_module_level(level_name, root_level)
        for name, level_name in log_cfg["module_levels"].items()
    }

    setup_logging(
        app_name=log_cfg["app_name"],
        level=root_level,  # default for all modules
        module_levels=module_levels,
    )
    log = logging.getLogger("orchestrator")

    # 1. The Registry
    # This list will hold anything that needs a .stop() call
    resources = []

    # 2. The Closer (Defined INSIDE main)
    # This function captures 'resources' from the local scope.
    def handle_exit(signum, frame):
        log.info("Signal %s received. Shutting down...", signum)
        
        # Shut down in reverse order (Last In, First Out)
        # This is safer if later objects depend on earlier ones.
        for component in reversed(resources):
            try:
                log.info("Stopping %s...", type(component).__name__)
                component.stop()
            except Exception as e:
                log.exception("Error stopping component: %s", e)
                
        log.info("Shutdown complete.")
        sys.exit(0)

    # 3. Register Signals
    signal.signal(signal.SIGINT, handle_exit)  # Ctrl+C
    signal.signal(signal.SIGTERM, handle_exit) # Docker Stop

    # ==========================================
    # 4. The Orchestration (Wire your system)
    # ==========================================
    
    log.info("Initializing modules...")

    # --- Create Module A (Subscriber 1) ---
    sub_cam = ZMQSubscriberModule()
    # Add to registry IMMEDIATELY after creation
    resources.append(sub_cam) 
    
    # --- Create Module B (Subscriber 2) ---
    sub_lidar = ZMQSubscriberModule()
    resources.append(sub_lidar)

    # --- Create Processing Modules ---
    # (Assuming these don't need cleanup, but if they did, append them too!)
    # detector = FaceDetector()
    # tracker = Tracker()

    # --- Wire Dependencies ---
    log.debug("Wiring callbacks...")
    # sub_cam.register_callback("front_cam", detector.process)
    # sub_lidar.register_callback("top_lidar", tracker.process)

    # --- Start Everything ---
    log.info("Starting loops...")
    # sub_cam.start(["tcp://127.0.0.1:5555"])
    # sub_lidar.start(["tcp://127.0.0.1:5556"])
    sub_cam.start("tcp://127.0.0.1:5555")
    sub_lidar.start("tcp://127.0.0.1:5556")
    # ==========================================
    # 5. Keep Alive
    # ==========================================
    log.info("System running. Press Ctrl+C to stop.")
    
    # This loop just keeps the main thread alive while background threads work
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()