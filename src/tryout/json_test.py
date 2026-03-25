import json
from pathlib import Path

# 1. Define where the data lives relative to this script
# This says: "Go up one level (..), then into the 'data' folder"
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "newsletters.json"

def load_data():
    try:
        with open(DATA_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Could not find the file at {DATA_PATH}")
        return None

data = load_data()

print(len(data))