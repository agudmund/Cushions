# utils/settings.py
import os
import json
import base64
from pathlib import Path
from typing import Any, Optional

# Absolute path for the settings file
SETTINGS_FILE = str(Path(__file__).parent.parent / "sketchbook_settings.json")

class Settings:
    """Central place to read/write persistent settings, layouts, and masked credentials."""
    
    @staticmethod
    def _load() -> dict:
        if not os.path.exists(SETTINGS_FILE):
            return {}
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

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

    # --- Private Masking Helpers ---

    @staticmethod
    def _mask(text: str) -> str:
        if not text: return ""
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')

    @staticmethod
    def _unmask(masked_text: str) -> str:
        if not masked_text: return ""
        try:
            # Decode only if it's valid base64, otherwise return raw
            return base64.b64decode(masked_text.encode('utf-8')).decode('utf-8')
        except Exception:
            return masked_text

    # --- Trello Credential Helpers ---

    @staticmethod
    def get_trello_creds() -> tuple[Optional[str], Optional[str]]:
        """Returns (api_key, token) unmasked, falling back to environment variables."""
        data = Settings._load()
        
        # 1. Try to get from JSON (masked)
        key = Settings._unmask(data.get("trello_key"))
        token = Settings._unmask(data.get("trello_token"))
        
        # 2. If JSON is empty, check Environment Variables
        if not key:
            key = os.environ.get("TRELLO_KEY")
        if not token:
            token = os.environ.get("TRELLO_TOKEN")
            
        return key, token

    @staticmethod
    def set_trello_creds(api_key: str, token: str) -> bool:
        """Stores Trello credentials as masked strings."""
        data = Settings._load()
        data["trello_key"] = Settings._mask(api_key)
        data["trello_token"] = Settings._mask(token)
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except OSError:
            return False

    # --- Directory Helpers ---

    @staticmethod
    def get_directory(key: str, default: str = "") -> str:
        path = Settings.get(key, default)
        return path if path and os.path.isdir(path) else ""

    @staticmethod
    def set_directory(key: str, filepath: str) -> bool:
        if not filepath: return False
        dirname = os.path.dirname(filepath)
        return Settings.set(key, dirname) if dirname else False

    # --- Layout Persistence Helpers ---

    @staticmethod
    def get_layout(source_file_path: str) -> dict:
        """Loads the hidden .layout.json associated with a markdown file."""
        p = Path(source_file_path)
        layout_path = p.parent / f".{p.name}.layout.json"
        if layout_path.exists():
            try:
                return json.loads(layout_path.read_text(encoding='utf-8'))
            except Exception:
                return {}
        return {}

    @staticmethod
    def save_layout(source_file_path: str, layout_map: dict) -> bool:
        """Saves the layout map to a hidden .layout.json file."""
        try:
            p = Path(source_file_path)
            layout_path = p.parent / f".{p.name}.layout.json"
            layout_path.write_text(json.dumps(layout_map, indent=2), encoding='utf-8')
            return True
        except Exception:
            return False