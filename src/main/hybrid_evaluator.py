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

def check_extrinsic_conflict(claim, mb_facts):
    """Heuristic logic to flag conflicts between the LLM claim and the real world."""
    if mb_facts.get("status") != "Found":
        return False 
    
    claim_lower = claim.lower()
    
    if mb_facts.get("country") == "GB":
        if "netherlands" in claim_lower or "dutch" in claim_lower or "nijmegen" in claim_lower:
            return True 
            
    return False

def print_header():
    print("="*60)
    print("CLOUDSPEAKERS HYBRID EVALUATOR (OFFLINE MODE)")
    print("="*60)

def main():
    start_time = time.time()
    print_header()
    
    # --- STEP 1: INGESTION ---
    corpus = data_loader.get_evaluation_corpus()
    if not corpus:
        print("🚨 Pipeline aborted: No data found. Run build_corpus.py first.")
        return
        
    print(f"Loaded {len(corpus)} valid artist entries for evaluation.\n")
    final_output_data = []

    # --- STEP 2: PROCESSING LOOP ---
    for entry in corpus:
        artist = entry.get("artist", "Unknown")
        summary = entry.get("summary", "")
        dutch_text = entry.get("dutch_text", "")
        mb_facts = entry.get("musicbrainz_facts", {"status": "Not Found"})

        print(f"EVALUATING: {artist.upper()}")
        print("-" * 60)

        context_sentences = dutch_parser.prepare_dutch_sentences(dutch_text, artist)
        claims = decomposer.extract_claims(summary, artist)
        print(f"Extracted {len(claims)} claims. Running NLI verification...")

        evaluations = validator.validate_claims(claims, context_sentences)
        hybrid_evaluations = []

        # --- STEP 3: CONFLICT RESOLUTION & REPORTING ---
        for i, eval_data in enumerate(evaluations, 1):
            claim = eval_data.get('claim', 'Unknown Claim')
            print(f"  [{i}] CLAIM: '{claim}'")
            
            ent_score = eval_data.get('best_ent_score', 0)
            con_score = eval_data.get('best_con_score', 0)

            # Determine Intrinsic Verdict
            if ent_score > 60 and con_score > 60:
                intrinsic_verdict = "AMBIGUOUS"
            elif ent_score > 60 and ent_score > con_score:
                intrinsic_verdict = "ENTAILMENT"
            elif con_score > 60 and con_score > ent_score:
                intrinsic_verdict = "CONTRADICTION"
            else:
                intrinsic_verdict = "UNSUPPORTED"

            # Determine Extrinsic Conflict
            has_extrinsic_conflict = check_extrinsic_conflict(claim, mb_facts)

            # Final Matrix Resolution
            if intrinsic_verdict == "ENTAILMENT" and not has_extrinsic_conflict:
                final_status = "VALID"
                print(f"      ✅ STATUS: {final_status} (NLI: {ent_score:.1f}% Entailment)")
            
            elif intrinsic_verdict == "ENTAILMENT" and has_extrinsic_conflict:
                final_status = "SOURCE_CONFLICT (Text likely wrong)"
                print(f"      ⚠️ STATUS: {final_status}")
            
            elif intrinsic_verdict == "CONTRADICTION":
                final_status = "INTRINSIC_HALLUCINATION"
                print(f"      🚨 STATUS: {final_status} (NLI: {con_score:.1f}% Contradiction)")
            
            elif intrinsic_verdict == "UNSUPPORTED" and not has_extrinsic_conflict:
                final_status = "EXTRINSIC_INJECTION_TRUE"
                print(f"      ⚠️ STATUS: {final_status} (Factual addition)")
            
            elif intrinsic_verdict == "AMBIGUOUS":
                final_status = "AMBIGUOUS"
                print(f"      ❓ STATUS: {final_status} (Ent: {ent_score:.1f}%, Con: {con_score:.1f}% — conflicting signals)")
                
            elif intrinsic_verdict == "UNSUPPORTED" and has_extrinsic_conflict:
                final_status = "EXTRINSIC_HALLUCINATION_FALSE"
                print(f"      🚨 STATUS: {final_status} (False addition)")

            eval_data["hybrid_status"] = final_status
            eval_data["mb_conflict_flag"] = has_extrinsic_conflict
            hybrid_evaluations.append(eval_data)

        entry["validation_results"] = hybrid_evaluations
        final_output_data.append(entry)
        print("="*60)

    # --- STEP 4: EXPORT DATA ---
    export_path = CURRENT_DIR / "data" / "final_hybrid_results.json"
    export_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving complete hybrid evaluation dataset to: {export_path}")
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(final_output_data, f, indent=4, ensure_ascii=False)

    elapsed = time.time() - start_time
    print(f"Pipeline finished in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()