import sys
from pathlib import Path
import json

# --- Path Alignment ---
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

import data_loader
import decomposer

def main():
    print("=" * 60)
    print("🚀 INITIALIZING FULL CORPUS CLAIM EXPORT")
    print("=" * 60)

    # 1. Load the entire corpus from the Data Access Layer
    corpus = data_loader.get_evaluation_corpus()
    if not corpus:
        print("🚨 Export aborted: Evaluation corpus is empty or missing.")
        return

    extracted_payload = []
    total_artists = len(corpus)
    total_claims_count = 0

    print(f"Processing {total_artists} artist entries...\n")

    # 2. Iterate through every entry and extract atomic claims
    for index, entry in enumerate(corpus, 1):
        artist = entry.get("artist", "Unknown Artist")
        summary = entry.get("summary", "")
        
        print(f"[{index}/{total_artists}] Extracting claims for: {artist.upper()}")
        
        # Run the updated Spacy dependency parsing logic (handling AUX, proper nouns, etc.)
        claims = decomposer.extract_claims(summary, artist)
        total_claims_count += len(claims)

        # Build a clean object for this artist
        extracted_payload.append({
            "artist": artist,
            "original_summary": summary,
            "total_claims": len(claims),
            "claims": claims
        })

    # 3. Define the destination inside your centralized /data folder
    # data_loader.CORPUS_PATH points to repo/data/full_evaluation_corpus.json, 
    # so we anchor our new export right alongside it.
    output_path = data_loader.CORPUS_PATH.parent / "all_extracted_claims.json"

    print("\n" + "=" * 60)
    print(f"Writing structured output to: {output_path}")
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_payload, f, indent=4, ensure_ascii=False)
        
        print(f"✅ EXPORT SUCCESSFUL!")
        print(f"   Total Artists Processed: {total_artists}")
        print(f"   Total Atomic Claims Exported: {total_claims_count}")
    except Exception as e:
        print(f"🚨 Failed to write JSON file: {e}")
    print("=" * 60)

if __name__ == "__main__":
    main()