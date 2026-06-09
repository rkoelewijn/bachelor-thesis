import sys
from pathlib import Path
from unittest.mock import patch
sys.path.append(str(Path(__file__).resolve().parent.parent / "main"))

import validator

# We 'mock' (fake) the NLI check so we don't need to load the 2GB model for a unit test
@patch('validator.run_nli_check')
def test_validate_claims(mock_run_nli_check):
    # Fake the model's output based on what sentence it receives
    def side_effect(premise, hypothesis):
        if "Nijmegen" in premise and "Nijmegen" in hypothesis:
            return {"ent": 95.0, "neu": 4.0, "con": 1.0}
        else:
            return {"ent": 5.0, "neu": 80.0, "con": 15.0}
            
    mock_run_nli_check.side_effect = side_effect

    artist = "Frank Boeijen"
    claims = ["Frank Boeijen returns to Nijmegen"]
    dutch_sentences = [
        "Over Frank Boeijen: Hij speelt liedjes.",
        "Over Frank Boeijen: Hij keert terug naar Nijmegen."
    ]
    
    results = validator.validate_claims(claims, dutch_sentences)
    
    # Assertions
    assert len(results) == 1
    
    report = results[0]
    assert report["claim"] == claims[0]
    assert report["scores"]["ent"] == 95.0
    # It should have successfully locked onto the sentence that gave the highest score
    assert report["evidence"] == "Over Frank Boeijen: Hij keert terug naar Nijmegen."


def test_validate_claims_edge_no_evidence():
    artist = "Ghost"
    claims = ["Ghost plays metal music."]
    
    # The Dutch parser returned an empty list because the text was junk
    dutch_sentences = [] 
    
    results = validator.validate_claims(claims, dutch_sentences)
    
    # It should still return a report for the claim...
    assert len(results) == 1
    # ...but the evidence should be empty and scores should be None
    assert results[0]["claim"] == claims[0]
    assert results[0]["evidence"] == ""
    assert results[0]["scores"] is None