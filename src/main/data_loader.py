import json
from pathlib import Path

print("🗄️ Booting up Data Access Layer...")

CURRENT_DIR = Path(__file__).resolve().parent
DATA_DIR = CURRENT_DIR.parent.parent / "data"

NEWSLETTERS_PATH = DATA_DIR / "newsletters.json"
WEB_PATH = DATA_DIR / "doornroosje.json"

def get_evaluation_corpus():
    try:
        with open(NEWSLETTERS_PATH, 'r') as f:
            corpus = json.load(f)
        with open(WEB_PATH, 'r') as f:
            dutch_web_data = json.load(f)
    except FileNotFoundError as e:
        print(f"🚨 Error loading data: {e}")
        return []

    evaluation_data = []

    for key, entry in corpus.items():
        if key == "TEMPLATE": continue
        
        artist_raw = entry.get('act', 'Unknown')
        artist_clean = artist_raw.split('+')[0].strip()
        summary = entry.get('summary', '')
        
        # Grab the URL from the newsletter entry
        url = entry.get('url', '')

        web_entry = dutch_web_data.get(key, {})
        dutch_text = web_entry.get('text', '')

        if dutch_text and summary:
            evaluation_data.append({
                "artist": artist_clean,
                "summary": summary,
                "dutch_text": dutch_text,
                "url": url 
            })

    return evaluation_data