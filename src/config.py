"""
Configuration loader for Satpam Laptop
"""
import os
import json

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
DATA_DIR = os.path.join(BASE_DIR, 'data')
CAPTURES_DIR = os.path.join(DATA_DIR, 'captures')

CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
CONFIG_EXAMPLE_FILE = os.path.join(CONFIG_DIR, 'config.example.json')
OWNER_DATA_FILE = os.path.join(DATA_DIR, 'owner_data.pkl')
OWNER_FACE_FILE = os.path.join(DATA_DIR, 'owner_face.jpg')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CAPTURES_DIR, exist_ok=True)

def load_config():
    """Load konfigurasi dari file JSON"""
    default_config = {
        "telegram_token": "YOUR_BOT_TOKEN_HERE",
        "chat_id": "YOUR_CHAT_ID_HERE",
        "cooldown_seconds": 10,
        "similarity_threshold": 0.7,
        "camera_index": 0,
        "auto_lock_on_intruder": False,
        "window_width": 850,
        "window_height": 700
    }

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
                print(f"✅ Config loaded from {CONFIG_FILE}")
        except Exception as e:
            print(f"⚠️ Gagal load config: {e}, menggunakan default")
    else:
        # Copy from example if exists
        if os.path.exists(CONFIG_EXAMPLE_FILE):
            import shutil
            shutil.copy(CONFIG_EXAMPLE_FILE, CONFIG_FILE)
            print(f"📝 Config copied from example: {CONFIG_FILE}")
        else:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
            print(f"📝 Config file created: {CONFIG_FILE}")

    return default_config

# Load config on import
CONFIG = load_config()
