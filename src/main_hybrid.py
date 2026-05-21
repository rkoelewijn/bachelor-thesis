import sys
import time
import json
from pathlib import Path
import musicbrainzngs

# 1. PATH CONFIGURATION
CURRENT_DIR = Path(__file__).resolve().parent
SRC_MAIN_DIR = CURRENT_DIR / "main"
sys.path.append(str(SRC_MAIN_DIR))

# 2. IMPORT ARCHITECTURE PILLARS
import data_loader
import dutch_parser
import decomposer
import validator 

# --- MUSICBRAINZ SETUP ---
musicbrainzngs.set_useragent(
    app="CloudspeakersThesisValidator",
    version="1.0",
    contact="thesis@student.university.nl" # Update with your actual email
)

def get_artist_facts(artist_name):
    """Fetches factual baseline data from MusicBrainz."""
    try:
        result = musicbrainzngs.search_artists(query=artist_name, limit=1)
        if not result.get('artist-list'):
            return {"status": "Not Found"}

        match = result['artist-list'][0]
        time.sleep(1) # Respect MB rate limit
        
        return {
            "status": "Found",
            "name": match.get("name"),
            "type": match.get("type", "Unknown"), 
            "country": match.get("country", "Unknown"), 
            "area": match.get("area", {}).get("name", "Unknown")
        }
    except Exception as e:
        print(f" ⚠️ MusicBrainz API Error: {e}")
        return {"status": "Error"}

def check_extrinsic_conflict(claim, mb_facts):
    """Heuristic logic to flag conflicts between the claim and the real world."""
    if mb_facts.get("status") != "Found":
        return False 
    
    claim_lower = claim.lower()
    
    # Example logic: Flag if the band is British, but the claim says Dutch
    if mb_facts.get("country") == "GB":
        if "netherlands" in claim_lower or "dutch" in claim_lower or "nijmegen" in claim_lower:
            return True 
            
    return False

def print_header():
    print("="*60)
    print(" 🚀 CLOUDSPEAKERS HYBRID PIPELINE v2.0")
    print("    NLI + MusicBrainz Knowledge Graph Integration")
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
    final_output_data = []

    # --- STEP 2: PROCESSING LOOP ---
    for entry in corpus:
        artist = entry["artist"]
        summary = entry["summary"]
        dutch_text = entry["dutch_text"]

        print(f"🎤 EVALUATING: {artist.upper()}")
        print("-" * 60)

        # Pre-fetch Extrinsic Data
        print(f" 🌐 Fetching MusicBrainz data...")
        mb_facts = get_artist_facts(artist)

        # Prepare & Decompose
        context_sentences = dutch_parser.prepare_dutch_sentences(dutch_text, artist)
        claims = decomposer.extract_claims(summary, artist)
        print(f" 🔪 Extracted {len(claims)} atomic claims.")

        # Intrinsic Validation
        print(f" ⚖️  Running cross-lingual verification...")
        evaluations = validator.validate_claims(claims, context_sentences)

        hybrid_evaluations = []

        # --- STEP 3: CONFLICT RESOLUTION & REPORTING ---
        for i, eval_data in enumerate(evaluations, 1):
            claim = eval_data.get('claim', 'Unknown Claim')
            print(f"\n  [{i}] CLAIM: '{claim}'")
            
            # Use the new flat keys from the refactored validator
            # Default to 0 if the keys aren't found for any reason
            ent_score = eval_data.get('best_ent_score', 0)
            con_score = eval_data.get('best_con_score', 0)
            
            # (Optional) Grab the evidence string if you want to print it later
            evidence = eval_data.get('evidence_used', 'No evidence found')
            # 1. Determine Intrinsic Verdict
            if ent_score > 60 and ent_score > con_score:
                intrinsic_verdict = "ENTAILMENT"
            elif con_score > 60 and con_score > ent_score:
                intrinsic_verdict = "CONTRADICTION"
            else:
                intrinsic_verdict = "UNSUPPORTED"

            # 2. Determine Extrinsic Conflict
            has_extrinsic_conflict = check_extrinsic_conflict(claim, mb_facts)

            # 3. Final Matrix Resolution
            if intrinsic_verdict == "ENTAILMENT" and not has_extrinsic_conflict:
                final_status = "VALID"
                print(f"      ✅ STATUS: {final_status}")
                print(f"      📊 NLI: {ent_score:.1f}% Entailment")
            
            elif intrinsic_verdict == "ENTAILMENT" and has_extrinsic_conflict:
                final_status = "SOURCE_CONFLICT (Text likely wrong)"
                print(f"      ⚠️ STATUS: {final_status}")
                print(f"      📊 NLI supported it, but MusicBrainz flags an error.")
            
            elif intrinsic_verdict == "CONTRADICTION":
                final_status = "INTRINSIC_HALLUCINATION"
                print(f"      🚨 STATUS: {final_status}")
                print(f"      📊 NLI: {con_score:.1f}% Contradiction")
            
            elif intrinsic_verdict == "UNSUPPORTED" and not has_extrinsic_conflict:
                final_status = "EXTRINSIC_INJECTION_TRUE"
                print(f"      ⚠️ STATUS: {final_status} (Factual addition)")
            
            elif intrinsic_verdict == "UNSUPPORTED" and has_extrinsic_conflict:
                final_status = "EXTRINSIC_HALLUCINATION_FALSE"
                print(f"      🚨 STATUS: {final_status} (False addition)")

            # Store hybrid results
            eval_data["hybrid_status"] = final_status
            eval_data["mb_data_used"] = mb_facts
            hybrid_evaluations.append(eval_data)

        entry["validation_results"] = hybrid_evaluations
        final_output_data.append(entry)
        print("\n" + "="*60 + "\n")

    # --- STEP 4: EXPORT DATA ---
    # Save this as case2 so it doesn't overwrite your baseline test
    export_path = CURRENT_DIR.parent / "data" / "validation_results_case2.json"
    print(f"💾 Saving hybrid evaluation dataset to: {export_path}")
    
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(final_output_data, f, indent=4, ensure_ascii=False)

    elapsed = time.time() - start_time
    print(f"🏁 Hybrid Pipeline finished in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()