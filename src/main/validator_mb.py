import time
import musicbrainzngs
from validate_intrinsic import run_intrinsic_pipeline

# --- CONFIGURATION ---
musicbrainzngs.set_useragent(
    app="CloudspeakersThesisValidator",
    version="1.0",
    contact="your.email@example.com" # Update this
)

def get_artist_facts(artist_name):
    """Queries MB for factual baseline data."""
    try:
        result = musicbrainzngs.search_artists(query=artist_name, limit=1)
        if not result.get('artist-list'):
            return {"status": "Not Found"}

        match = result['artist-list'][0]
        time.sleep(1) # Respect MB rate limit!
        
        return {
            "status": "Found",
            "name": match.get("name"),
            "type": match.get("type", "Unknown"), 
            "country": match.get("country", "Unknown"), 
            "area": match.get("area", {}).get("name", "Unknown")
        }
    except Exception as e:
        print(f"MusicBrainz API Error: {e}")
        return {"status": "Error"}

def check_extrinsic_conflict(claim, mb_facts):
    """
    A heuristic checker. If the claim mentions a country (like NL) 
    but the band is from GB, it flags a conflict.
    """
    if mb_facts.get("status") != "Found":
        return False # Can't conflict if we have no data
    
    claim_lower = claim.lower()
    
    # Example logic: Check for origin conflicts
    if mb_facts.get("country") == "GB":
        if "netherlands" in claim_lower or "dutch" in claim_lower:
            return True 
            
    return False

def run_hybrid_pipeline(artist_name, summary_claims, dutch_sentences):
    """Runs Phase 1 (NLI) and Phase 2 (MB) sequentially."""
    
    print(f"🔍 Pre-fetching MusicBrainz data for: {artist_name}")
    mb_facts = get_artist_facts(artist_name)
    
    # 1. Run the existing intrinsic pipeline
    intrinsic_results = run_intrinsic_pipeline(summary_claims, dutch_sentences)
    
    # 2. Layer on the extrinsic conflict resolution
    final_results = []
    for item in intrinsic_results:
        verdict = item["nli_verdict"]
        has_conflict = check_extrinsic_conflict(item["claim"], mb_facts)
        
        if verdict == "ENTAILMENT" and not has_conflict:
            final_status = "VALID"
        elif verdict == "ENTAILMENT" and has_conflict:
            final_status = "SOURCE_CONFLICT"
        elif verdict == "CONTRADICTION":
            final_status = "INTRINSIC_HALLUCINATION"
        elif verdict == "UNSUPPORTED" and not has_conflict:
            final_status = "EXTRINSIC_INJECTION_TRUE"
        elif verdict == "UNSUPPORTED" and has_conflict:
            final_status = "EXTRINSIC_HALLUCINATION_FALSE"
            
        item["final_status"] = final_status
        item["mb_conflict_flag"] = has_conflict
        item["mb_data_used"] = mb_facts
        final_results.append(item)
        
    return final_results