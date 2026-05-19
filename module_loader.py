# module_loader.py
# Dynamically loads ONLY high-value engines from the root directory

import importlib
import sys
import os

HIGH_VALUE_ENGINES = {
    "idor_engine",
    "ssrf_engine",
    "auth_bypass_engine",
    "rate_limit_engine",
    "sensitive_data_engine",
    "jwt_engine"
}

def load_modules():
    modules = {}

    # Ensure root directory is on sys.path so top-level engines are importable
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    for name in HIGH_VALUE_ENGINES:
        filename = os.path.join(root_dir, f"{name}.py")
        if not os.path.exists(filename):
            print(f"[module_loader] Warning: {name}.py not found, skipping")
            continue
        try:
            modules[name] = importlib.import_module(name)
        except Exception as e:
            print(f"[module_loader] Failed to load {name}: {e}")

    return modules
