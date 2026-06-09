import sys
from pathlib import Path
from unittest.mock import patch, mock_open
import json
sys.path.append(str(Path(__file__).resolve().parent.parent / "main"))

import data_loader

# Fake JSON data
mock_newsletters = {
    "ACT_1": {"act": "Fear Factory + Support", "summary": "A metal band."}
}
mock_web = {
    "ACT_1": {"text": "Dutch text about Fear Factory."}
}

# Patching 'builtins.open' intercepts the file read and feeds it our fake data
@patch('builtins.open')
@patch('json.load')
def test_get_evaluation_corpus(mock_json_load, mock_file_open):
    # Return newsletters first, then web data
    mock_json_load.side_effect = [mock_newsletters, mock_web]
    
    corpus = data_loader.get_evaluation_corpus()
    
    assert len(corpus) == 1
    entry = corpus[0]
    
    # Check if the "+ Support" was stripped correctly
    assert entry["artist"] == "Fear Factory"
    assert entry["summary"] == "A metal band."
    assert entry["dutch_text"] == "Dutch text about Fear Factory."