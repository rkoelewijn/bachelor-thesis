import time
import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent 
EXPORT_PATH =  ROOT_DIR / "data" / "validation_results_hybrid.json"

import data_loader
import dutch_parser
import decomposer
import validator 


# TODO:: MAKE THIS FUNCTION MAKE SENSE AND ACTUALLY DO SOMETHING
def extract_verifiable_facts(claim, artist):
    """Extract structured facts that can be verified against MusicBrainz."""
    facts = []
    claim_lower = claim.lower()
    
    # Country/origin patterns
    country_map = {
        'dutch': 'NL', 'netherlands': 'NL', 'belgian': 'BE', 'belgium': 'BE',
        'english': 'GB', 'british': 'GB', 'american': 'US', 'canadian': 'CA',
        'swedish': 'SE', 'german': 'DE', 'italian': 'IT', 'australian': 'AU'
    }
    for keyword, code in country_map.items():
        if keyword in claim_lower:
            facts.append(('country', code))
    
    # Artist type (band vs person)
    if any(x in claim_lower for x in ['band', 'group', 'trio', 'quartet', 'duo']):
        facts.append(('type', 'Group'))
    elif any(x in claim_lower for x in ['singer', 'songwriter', 'artist', 'musician']):
        facts.append(('type', 'Person'))
    
    return facts

def verify_facts(extracted_facts, mb_facts):
    """Check each extracted fact against MusicBrainz."""
    if mb_facts.get('status') != 'Found':
        return None  # Can't verify
    
    conflicts = []
    for fact_type, fact_value in extracted_facts:
        mb_value = mb_facts.get(fact_type)
        if mb_value and mb_value != 'Unknown' and mb_value != fact_value:
            conflicts.append((fact_type, fact_value, mb_value))
    
    return conflicts  # Returns list of (fact_type, claimed, actual) tuples


def check_extrinsic_conflict(claim, mb_facts, artist):
    """Bridge function: Evaluates the claim and returns True if a database conflict exists."""
    if mb_facts.get("status") != "Found":
        return False
        
    extracted_facts = extract_verifiable_facts(claim, artist)
    
    # If no facts could be extracted from the text, there is no conflict
    if not extracted_facts:
        return False
        
    conflicts = verify_facts(extracted_facts, mb_facts)
    
    # If the conflicts list is populated, an extrinsic hallucination occurred
    if conflicts:
        # Optional: Print the specific conflict to the terminal for transparency
        for c in conflicts:
            print(f"      [!] API CONFLICT: Claim says {c[0]} is '{c[1]}', but MusicBrainz says '{c[2]}'")
        return True
        
    return False


def print_header():
    print("="*60)
    print("CLOUDSPEAKERS HYBRID EVALUATOR")
    print("="*60)

def main():
    """ The evaluator loads the created corpus, parses the Dutch source text, extracts claims from the given summary and validates these claims against the source and the loaded Music Brainz data. 
    Returns different entailment scores, and the source. """
     
    start_time = time.time()
    print_header()
    
    # Load data using the setup data_loader.py
    corpus = data_loader.get_evaluation_corpus()
    if not corpus:
        print("Pipeline aborted: No data found.")
        return
        
    print(f"Loaded {len(corpus)} valid artist entries for evaluation.\n")

    final_output_data = []

    for entry in corpus:
        artist = entry.get("artist", "Unknown")
        summary = entry.get("summary", "")
        dutch_text = entry.get("dutch_text", "")
        mb_facts = entry.get("musicbrainz_facts", {"status": "Not Found"})

        print(f"EVALUATING: {artist.upper()}")
        print("-" * 60)

        # Parse Dutch text using dutch_parser.py
        context_sentences = dutch_parser.prepare_dutch_sentences(dutch_text, artist)

        # Extract claims from summary using decomposer.py
        claims = decomposer.extract_claims(summary, artist)
        print(f"Extracted {len(claims)} claims. Running NLI verification...")

        # Validate claims using validator.py
        evaluations = validator.validate_claims(claims, context_sentences)

        hybrid_evaluations = []

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
            has_extrinsic_conflict = check_extrinsic_conflict(claim, mb_facts, artist)

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

    # Export data
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving complete hybrid evaluation dataset to: {EXPORT_PATH}")
    with open(EXPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_output_data, f, indent=4, ensure_ascii=False)

    elapsed = time.time() - start_time
    print(f"Pipeline finished in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()