# utils/features.py
import os
import json

FEATURES_FILE = "features.json"


def load_features() -> list[str]:
    if not os.path.exists(FEATURES_FILE):
        default_features = [
            "Dark cozy theme with soft pastel accents",
            "Drag-and-drop file area with hover feedback",
            # ... all the others ...
        ]
        with open(FEATURES_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_features, f, indent=2)
        return default_features

    try:
        with open(FEATURES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []