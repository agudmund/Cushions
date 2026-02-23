# utils/settings.py
import os
import json
from typing import Any, Optional

SETTINGS_FILE = "sketchbook_settings.json"


class Settings:
    """Central place to read/write persistent settings."""

    @staticmethod
    def _load() -> dict:
        if not os.path.exists(SETTINGS_FILE):
            return {}
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}  # silent fail → defaults

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        data = Settings._load()
        return data.get(key, default)

    @staticmethod
    def set(key: str, value: Any) -> bool:
        data = Settings._load()
        data[key] = value
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except OSError:
            return False

    @staticmethod
    def get_directory(key: str, default: str = "") -> str:
        """Get last used directory, return only if it still exists."""
        path = Settings.get(key, default)
        return path if path and os.path.isdir(path) else ""

    @staticmethod
    def set_directory(key: str, filepath: str) -> bool:
        """Remember the parent directory of a just-selected file."""
        if not filepath:
            return False
        dirname = os.path.dirname(filepath)
        if dirname:
            return Settings.set(key, dirname)
        return False