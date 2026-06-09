import json
from pathlib import Path

# Setup paths relative to the script location
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent 
EXPORT_PATH = ROOT_DIR / "data" / "eval" / "extracted_claims_for_labeling.json"

# Internal modules
import data_loader
import decomposer

def main():
    print("="*60)
    print("GROUND TRUTH TEMPLATE GENERATOR")
    print("="*60)
    
    # Load the manually pasted newsletter corpus
    corpus = data_loader.get_evaluation_corpus()
    if not corpus:
        print("Error: Could not load the evaluation corpus.")
        return

    print(f"Loaded {len(corpus)} entries from the corpus.")
    print("Extracting claims exactly as the decomposer outputs them...\n")

    template_data = []

    for entry in corpus:
        artist = entry.get("artist", "Unknown")
        summary = entry.get("summary", "")
        
        # Extract claims using the exact pipeline logic to guarantee string matching
        claims = decomposer.extract_claims(summary, artist)
        
        for index, claim_text in enumerate(claims):
            # Build the dictionary exactly matching the required schema
            claim_entry = {
                "artist": artist,
                "claim": claim_text,
                "claim_index": index,
                "evidence_used": None,
                "ground_truth": None,  # Ready for manual labeling
                "notes": ""
            }
            template_data.append(claim_entry)

    # Export the template
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(EXPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(template_data, f, indent=2, ensure_ascii=False)

    print(f"Successfully exported {len(template_data)} empty claim templates.")
    print(f"File saved to: {EXPORT_PATH}")
    print("="*60)
    print("Next steps:")
    print("1. Open 'extracted_claims_for_labeling.json'.")
    print("2. Fill in the 'ground_truth' fields with SUPPORTED, INTRINSIC, or EXTRINSIC.")
    print("3. Rename the file to 'ternary_ground_truth_labels.json' to use it in the baseline evaluator.")

if __name__ == "__main__":
    main()