import sys
import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
SRC_MAIN_DIR = CURRENT_DIR.parent / "main"
sys.path.append(str(SRC_MAIN_DIR))

from decomposer import extract_claims 

DATA_PATH = CURRENT_DIR.parent.parent / "data" / "newsletters.json"
NO_OF_TESTS = 11 

def run_benchmark():

    # Loading the testing database JSON. 
    try:
        with open(DATA_PATH, 'r') as f:
            corpus = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found at {DATA_PATH}")
        return

    print(f"\n{'ARTIST':<20} | {'STATUS'}")
    print("-" * 40)

    count = 0 

    # 2. Iterate through all 11 entries
    for key, entry in corpus.items():
        if key == "TEMPLATE": continue
        
        # Pull data
        artist_raw = entry.get('act', 'Unknown')
        # Clean the artist name for the claim (e.g., Fear Factory + Support -> Fear Factory)
        artist_clean = artist_raw.split('+')[0].strip()
        summary = entry.get('summary', '')

        # 3. Execute Decomposition
        claims = extract_claims(summary, artist_clean)

        # 4. Report Results
        print(f"{artist_clean:<20} | Found {len(claims)} claims")
        print(f"Summary: {summary}")
        for i, c in enumerate(claims, 1):
            print(f"  └─ [{i}] {c}")
        print()

        count += 1
        if count >= NO_OF_TESTS:
            print(f"\n🛑 Stopped after {NO_OF_TESTS} entries for testing.")
            break

if __name__ == "__main__":
    run_benchmark()