import json
from pathlib import Path

print("🗄️ Booting up Data Access Layer...")

# 1. PATH CONFIGURATION
CURRENT_DIR = Path(__file__).resolve().parent
CORPUS_PATH = CURRENT_DIR / "full_evaluation_corpus.json"

def get_evaluation_corpus():
    """
    Loads the pre-compiled evaluation corpus.
    Must run build_corpus.py first to generate this file.
    """
    try:
        with open(CORPUS_PATH, 'r', encoding='utf-8') as f:
            corpus = json.load(f)
            return corpus
    except FileNotFoundError:
        print(f"🚨 Error: Could not find {CORPUS_PATH.name}.")
        print("   Please run the build_corpus.py ingestion script first.")
        return []
