import json
from pathlib import Path
import os

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent 
CORPUS_PATH = ROOT_DIR / "data" / "full_evaluation_corpus.json"

def get_evaluation_corpus():
    """
    Loads the pre-compiled evaluation corpus.
    Must run build_corpus.py first to generate this file.
    """
    try:
        with open(CORPUS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # --- NEW: Intercept Test Mode Signal ---
            test_limit = os.environ.get("PIPELINE_TEST_LIMIT")
            if test_limit and test_limit.isdigit():
                print(f"⚠️ TEST MODE ACTIVE: Yielding only the first {test_limit} artists for rapid testing.")
                return data[:int(test_limit)]
                
            return data
            
    except FileNotFoundError:
        print(f"🚨 Error: Could not find {CORPUS_PATH.name} at {CORPUS_PATH.parent}.")
        print("   Please run the build_corpus.py ingestion script first.")
        return []

def save_evaluation_corpus(corpus_data):
    """Saves the compiled corpus data to the centralized location."""
    try:
        # Ensure directory exists if you change paths later
        CORPUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        with open(CORPUS_PATH, 'w', encoding='utf-8') as f:
            json.dump(corpus_data, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved compiled corpus to: {CORPUS_PATH}")
    except Exception as e:
        print(f"Failed to save corpus data: {e}")