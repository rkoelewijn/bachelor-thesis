import time
import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent 
EXPORT_PATH =  ROOT_DIR / "data" / "validation_results_baseline.json"

import data_loader
import dutch_parser
import decomposer
import validator 

def print_header():
    print("="*60)
    print("CLOUDSPEAKERS BASELINE EVALUATOR")
    print("="*60)

def main():
    """ The evaluator loads the created corpus, parses the Dutch source text, extracts claims from the given summary and validates these claims. 
    Returns different entailment scores, and the source. """

    start_time = time.time()
    print_header()
    
    # Load data using the setup data_loader.py
    corpus = data_loader.get_evaluation_corpus()
    if not corpus:
        print("Data loading error.")
        return
        
    print(f"Loaded {len(corpus)} valid artist entries for evaluation.\n")
    
    final_output_data = [] 

    for entry in corpus:
        artist = entry.get("artist", "Unknown")
        summary = entry.get("summary", "")
        dutch_text = entry.get("dutch_text", "")

        print(f"EVALUATING: {artist.upper()}")
        print("-" * 60)

        # Parse Dutch text using dutch_parser.py
        context_sentences = dutch_parser.prepare_dutch_sentences(dutch_text, artist)
        
        # Extract claims from summary using decomposer.py
        claims = decomposer.extract_claims(summary, artist)
        print(f"Extracted {len(claims)} atomic claims. Running NLI verification...")

        # Validate claims using validator.py
        evaluations = validator.validate_claims(claims, context_sentences)

        # Attach the results back to our entry data for exporting later
        entry["validation_results"] = evaluations
        final_output_data.append(entry)

        # Reporting results to terminal
        for i, eval_data in enumerate(evaluations, 1):
            claim = eval_data.get('claim', 'Unknown Claim')
            print(f"  [{i}] CLAIM: '{claim}'")
            
            # Fetch flattened scores from the updated validator
            ent_score = eval_data.get('best_ent_score', 0)
            con_score = eval_data.get('best_con_score', 0)
            
            # Logic Thresholds: Which signal is stronger?
            # TODO: Change hardcoded ent. score values 
            if ent_score > 60 and ent_score > con_score: 
                print(f"      ✅ RESULT: VERIFIED (NLI: {ent_score:.1f}% Entailment)")
            elif con_score > 60 and con_score > ent_score: 
                print(f"      🚨 RESULT: HALLUCINATION (NLI: {con_score:.1f}% Contradiction)")
            else: 
                print(f"      ⚠️ RESULT: UNVERIFIED / NEUTRAL (Ent: {ent_score:.1f}%, Con: {con_score:.1f}%)")
        
        print("="*60)

    # Export data
    # Ensure the directory exists
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving complete baseline evaluation dataset to: {EXPORT_PATH}")
    
    with open(EXPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_output_data, f, indent=4, ensure_ascii=False)

    # Print time
    elapsed = time.time() - start_time
    print(f"Baseline Pipeline finished in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()