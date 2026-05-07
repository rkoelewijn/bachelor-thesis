import sys
import time
import json
from pathlib import Path

# 1. PATH CONFIGURATION
# Tell Python to look inside the 'main' subfolder for our modules
CURRENT_DIR = Path(__file__).resolve().parent
SRC_MAIN_DIR = CURRENT_DIR / "main"
sys.path.append(str(SRC_MAIN_DIR))

# 2. IMPORT ARCHITECTURE PILLARS
import data_loader
import dutch_parser
import decomposer
import validator 

def print_header():
    print("="*60)
    print(" 🚀 CLOUDSPEAKERS NLI PIPELINE v1.0")
    print("    Fact-Checking Hallucinations in Live Music Metadata")
    print("="*60)

def main():
    start_time = time.time()
    print_header()
    
    # --- STEP 1: INGESTION ---
    corpus = data_loader.get_evaluation_corpus()
    if not corpus:
        print("🚨 Pipeline aborted: No data found.")
        return
        
    print(f"📁 Loaded {len(corpus)} valid artist entries for evaluation.\n")
    
    final_output_data = [] # Stores all data for the final JSON export

    # --- STEP 2: PROCESSING LOOP ---
    for entry in corpus:
        artist = entry["artist"]
        summary = entry["summary"]
        dutch_text = entry["dutch_text"]

        print(f"🎤 EVALUATING: {artist.upper()}")
        print("-" * 60)

        # Phase 1: Prepare Dutch Evidence
        context_sentences = dutch_parser.prepare_dutch_sentences(dutch_text, artist)
        
        # Phase 2: Decompose English Summary
        claims = decomposer.extract_claims(summary, artist)
        print(f"  🔪 Extracted {len(claims)} atomic claims.")

        # Phase 3: Validate
        print(f"  ⚖️  Running cross-lingual verification...")
        evaluations = validator.validate_claims(claims, context_sentences)

        # Attach the results back to our entry data for exporting later
        entry["validation_results"] = evaluations
        final_output_data.append(entry)

        # --- STEP 3: REPORTING ---
        for i, eval_data in enumerate(evaluations, 1):
            print(f"\n  [{i}] CLAIM: '{eval_data['claim']}'")
            
            # Check if scores exist (handles edge cases with empty Dutch sentences)
            if eval_data['entailment_match']['scores']:
                ent_score = eval_data['entailment_match']['scores']['ent']
                con_score = eval_data['contradiction_match']['scores']['con']
                
                # Logic Thresholds: Which signal is stronger?
                if ent_score > 60 and ent_score > con_score: 
                    print("      ✅ RESULT: VERIFIED")
                    print(f"      🔎 EVIDENCE: '{eval_data['entailment_match']['evidence']}'")
                    print(f"      📊 SCORE: 🟢 {ent_score:.1f}% Entailment")
                elif con_score > 60 and con_score > ent_score: 
                    print("      🚨 RESULT: HALLUCINATION (Contradiction Caught)")
                    print(f"      🔎 EVIDENCE: '{eval_data['contradiction_match']['evidence']}'")
                    print(f"      📊 SCORE: 🔴 {con_score:.1f}% Contradiction")
                else: 
                    print("      ⚠️ RESULT: UNVERIFIED / NEUTRAL")
                    print(f"      🔎 TOP ENT EVIDENCE: '{eval_data['entailment_match']['evidence']}' ({ent_score:.1f}%)")
                    print(f"      🔎 TOP CON EVIDENCE: '{eval_data['contradiction_match']['evidence']}' ({con_score:.1f}%)")
            else:
                print("      ⚠️ RESULT: UNVERIFIED (No Dutch sentences available)")
        
        print("\n" + "="*60 + "\n")

    # --- STEP 4: EXPORT DATA ---
    export_path = CURRENT_DIR.parent / "data" / "validation_results_case1.json"
    print(f"💾 Saving complete evaluation dataset to: {export_path}")
    
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(final_output_data, f, indent=4, ensure_ascii=False)

    # --- WRAP UP ---
    elapsed = time.time() - start_time
    print(f"🏁 Pipeline finished in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()