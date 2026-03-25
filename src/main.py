import sys
import time
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

        # --- STEP 3: REPORTING ---
        for i, eval_data in enumerate(evaluations, 1):
            print(f"\n  [{i}] CLAIM: '{eval_data['claim']}'")
            
            if eval_data['scores']:
                scores = eval_data['scores']
                print(f"      🔎 EVIDENCE: '{eval_data['evidence']}'")
                print(f"      📊 SCORES: 🟢 {scores['ent']:.1f}% Entail | 🟡 {scores['neu']:.1f}% Neut | 🔴 {scores['con']:.1f}% Cont")
                
                # Logic Thresholds
                if scores['ent'] > 60: 
                    print("      ✅ RESULT: VERIFIED")
                elif scores['con'] > 60: 
                    print("      🚨 RESULT: HALLUCINATION")
                else: 
                    print("      ⚠️ RESULT: UNVERIFIED")
            else:
                print("      ⚠️ RESULT: UNVERIFIED (No Dutch sentences available)")
        
        print("\n" + "="*60 + "\n")

    # --- WRAP UP ---
    elapsed = time.time() - start_time
    print(f"🏁 Pipeline finished in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()