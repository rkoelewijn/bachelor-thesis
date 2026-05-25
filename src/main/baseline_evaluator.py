import sys
import time
import json
from pathlib import Path

# --- 1. PATH CONFIGURATION ---
CURRENT_DIR = Path(__file__).resolve().parent
SRC_MAIN_DIR = CURRENT_DIR / "main"
sys.path.append(str(SRC_MAIN_DIR))

# --- 2. IMPORT ARCHITECTURE PILLARS ---
import data_loader
import dutch_parser
import decomposer
import validator 

def print_header():
    print("="*60)
    print("CLOUDSPEAKERS BASELINE EVALUATOR (NLI ONLY)")
    print("="*60)

def main():
    start_time = time.time()
    print_header()
    
    # --- STEP 1: INGESTION ---
    corpus = data_loader.get_evaluation_corpus()
    if not corpus:
        print("🚨 Pipeline aborted: No data found.")
        return
        
    print(f"Loaded {len(corpus)} valid artist entries for evaluation.\n")
    
    final_output_data = [] 

    # --- STEP 2: PROCESSING LOOP ---
    for entry in corpus:
        artist = entry.get("artist", "Unknown")
        summary = entry.get("summary", "")
        dutch_text = entry.get("dutch_text", "")

        print(f"EVALUATING: {artist.upper()}")
        print("-" * 60)

        # Phase 1: Prepare Dutch Evidence
        context_sentences = dutch_parser.prepare_dutch_sentences(dutch_text, artist)
        
        # Phase 2: Decompose English Summary
        claims = decomposer.extract_claims(summary, artist)
        print(f"Extracted {len(claims)} atomic claims. Running NLI verification...")

        # Phase 3: Validate
        evaluations = validator.validate_claims(claims, context_sentences)

        # Attach the results back to our entry data for exporting later
        entry["validation_results"] = evaluations
        final_output_data.append(entry)

        # --- STEP 3: REPORTING ---
        for i, eval_data in enumerate(evaluations, 1):
            claim = eval_data.get('claim', 'Unknown Claim')
            print(f"  [{i}] CLAIM: '{claim}'")
            
            # Fetch flattened scores from the updated validator
            ent_score = eval_data.get('best_ent_score', 0)
            con_score = eval_data.get('best_con_score', 0)
            
            # Logic Thresholds: Which signal is stronger?
            if ent_score > 60 and ent_score > con_score: 
                print(f"      ✅ RESULT: VERIFIED (NLI: {ent_score:.1f}% Entailment)")
            elif con_score > 60 and con_score > ent_score: 
                print(f"      🚨 RESULT: HALLUCINATION (NLI: {con_score:.1f}% Contradiction)")
            else: 
                print(f"      ⚠️ RESULT: UNVERIFIED / NEUTRAL (Ent: {ent_score:.1f}%, Con: {con_score:.1f}%)")
        
        print("="*60)

    # --- STEP 4: EXPORT DATA ---
    export_path = CURRENT_DIR.parent / "data" / "validation_results_case1.json"
    
    # Ensure the directory exists
    export_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving complete baseline evaluation dataset to: {export_path}")
    
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(final_output_data, f, indent=4, ensure_ascii=False)

    # --- WRAP UP ---
    elapsed = time.time() - start_time
    print(f"Baseline Pipeline finished in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()