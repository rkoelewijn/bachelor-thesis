import json
from pathlib import Path
from owi_client import OWIClient

class OWIDataLoader:
    def __init__(self):
        self.owi = OWIClient()
        self.data_dir = Path(__file__).resolve().parent.parent.parent / "data"
        self.newsletters_path = self.data_dir / "newsletters.json"

    def get_evaluation_corpus(self, venue_domain="doornroosje.nl"):
        """
        Loads English summaries from local storage and fetches 
        Dutch counterparts from the Open Web Index.
        """
        try:
            with open(self.newsletters_path, 'r') as f:
                newsletters = json.load(f)
        except FileNotFoundError:
            print(f"🚨 Error: Could not find {self.newsletters_path}")
            return []

        evaluation_data = []

        for key, entry in newsletters.items():
            if key == "TEMPLATE": continue
            
            artist_raw = entry.get('act', 'Unknown')
            artist_clean = artist_raw.split('+')[0].strip()
            summary = entry.get('summary', '')

            print(f"🌐 Fetching Ground Truth from OWI for: {artist_clean}...")
            
            # Use OWI to find the original Dutch page content
            dutch_text = self.owi.search_artist_at_venue(artist_clean, venue_domain)

            if dutch_text:
                evaluation_data.append({
                    "artist": artist_clean,
                    "summary": summary,
                    "dutch_text": dutch_text
                })
            else:
                print(f"  ❌ No OWI data found for {artist_clean}. Skipping.")

        return evaluation_data