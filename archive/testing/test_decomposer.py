import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "main"))

import decomposer

def test_extract_claims():
    summary = "Dutch singer-songwriter Frank Boeijen returns to his beloved hometown of Nijmegen for an evening of poetic songs and stories. "
    artist = "Frank Boeijen"
    
    claims = decomposer.extract_claims(summary, artist)
    
    assert len(claims) == 2, f"Expected 2 claims, got {len(claims)}"
    assert "Frank Boeijen returns to his beloved hometown of Nijmegen" in claims
    assert "Frank Boeijen returns for an evening of poetic songs and stories" in claims

    
def test_extract_claims_edge_no_verbs():
    # Testing when a sentence does not have an action. 
    summary = "A highly energetic Dutch pop-rock band."
    artist = "The Band"
    
    claims = decomposer.extract_claims(summary, artist)
    
    # It should trigger our fallback and just return the original summary
    assert len(claims) == 1
    assert claims[0] == summary

def test_extract_claims_edge_weird_punctuation():
    # Testing if the punctuation is weird. 
    summary = "Wyatt E. plays heavy riffs..."
    artist = "Wyatt E."
    
    claims = decomposer.extract_claims(summary, artist)
    
    # We expect it to return the claim with "plays". 
    assert len(claims) >= 1
    assert any("plays" in claim for claim in claims)

