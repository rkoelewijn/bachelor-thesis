import time
import musicbrainzngs

# MusicBrainz REQUIRES a descriptive User-Agent, or they will block your IP.
musicbrainzngs.set_useragent(
    app="CloudspeakersThesisValidator",
    version="1.0",
    contact="ruben.koelewijn@ru.nl" # Replace with your email
)

def get_artist_facts(artist_name):
    """
    Queries MusicBrainz for factual metadata about an artist to catch Extrinsic Hallucinations.
    """
    try:
        # Search for the artist (limit=1 to get the most likely match)
        result = musicbrainzngs.search_artists(query=artist_name, limit=1)
        
        if not result.get('artist-list'):
            return {"status": "Not Found"}

        # Extract the top result
        match = result['artist-list'][0]
        
        # Build a structured dictionary of real-world facts
        facts = {
            "status": "Found",
            "name": match.get("name"),
            "type": match.get("type", "Unknown"), # e.g., Group, Person
            "country": match.get("country", "Unknown"), # e.g., GB, NL, US
            "area": match.get("area", {}).get("name", "Unknown"), # e.g., Leeds, Amsterdam
            "formed": match.get("life-span", {}).get("begin", "Unknown")
        }
        
        # Sleep for 1 second to respect the MusicBrainz rate limit!
        time.sleep(1) 
        return facts

    except musicbrainzngs.WebServiceError as exc:
        print(f"MusicBrainz API Error: {exc}")
        return {"status": "Error"}

import json
from pathlib import Path

# --- CONFIGURATION ---
# Points directly to the current directory since they are side-by-side
CURRENT_DIR = Path(__file__).resolve().parent
NEWSLETTERS_PATH = CURRENT_DIR / "newsletters.json"

def list_all_artists():
    print(f"📥 Loading database from: {NEWSLETTERS_PATH}")
    
    try:
        with open(NEWSLETTERS_PATH, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("🚨 Error: Could not find newsletters.json. Please check the path.")
        return

    # Using a set to automatically filter out duplicates
    unique_artists = set()
    total_entries = 0

    for key, entry in data.items():
        if key == "TEMPLATE": 
            continue
        
        total_entries += 1
        
        # Replicate the extraction logic from your data_loader
        artist_raw = entry.get('act', 'Unknown')
        artist_clean = artist_raw.split('+')[0].strip()
        
        if artist_clean and artist_clean != "Unknown":
            unique_artists.add(artist_clean)

    # Sort alphabetically for easier reading
    sorted_artists = sorted(list(unique_artists))

    # --- TERMINAL OUTPUT ---
    print("\n" + "="*50)
    print("📊 DATABASE ARTIST SUMMARY")
    print("="*50)
    print(f"Total entries processed: {total_entries}")
    print(f"Unique headliners found: {len(sorted_artists)}")
    print("-" * 50)
    
    for i, artist in enumerate(sorted_artists, 1):
        print(f"{i:03d}. {artist}")
        
    print("="*50 + "\n")

if __name__ == "__main__":
    list_all_artists()