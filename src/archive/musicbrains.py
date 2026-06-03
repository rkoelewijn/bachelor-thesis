import time
import musicbrainzngs
import json
from pathlib import Path

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
        
        # --- FIX: Extract Genres from Tags ---
        # MusicBrainz stores genres as user-generated tags. We pull the top 2.
        tags = match.get("tag-list", [])
        if tags:
            genre = ", ".join([tag.get("name") for tag in tags[:2]])
        else:
            genre = "Unknown"

        # --- FIX: Extract Place from Begin-Area ---
        # 'area' is usually the country, 'begin-area' is the founding city/town.
        place = match.get("begin-area", {}).get("name", "Unknown")

        # Build a structured dictionary of real-world facts
        facts = {
            "status": "Found",
            "name": match.get("name", "Unknown"),
            "type": match.get("type", "Unknown"), 
            "country": match.get("country", "Unknown"), 
            "area": match.get("area", {}).get("name", "Unknown"), 
            "place": place,
            "genre": genre
        }
        
        # Sleep for 1 second to respect the MusicBrainz rate limit
        time.sleep(1) 
        return facts

    except musicbrainzngs.WebServiceError as exc:
        print(f"MusicBrainz API Error: {exc}")
        return {"status": "Error"}


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
    print("\n" + "="*90)
    print("📊 DATABASE ARTIST SUMMARY & MUSICBRAINZ FACTS")
    print("="*90)
    print(f"Total entries processed: {total_entries}")
    print(f"Unique headliners found: {len(sorted_artists)}")
    print("Fetching facts from MusicBrainz... (Note: 1 second delay per artist due to rate limits)")
    print("-" * 90)
    
    for i, artist in enumerate(sorted_artists, 1):
        # Fetch the facts for the current artist
        facts = get_artist_facts(artist)
        
        if facts.get("status") == "Found":
            # Extract the required fields, defaulting to "Unknown" if missing
            genre = facts.get("genre", "Unknown")
            area = facts.get("area", "Unknown")
            place = facts.get("place", "Unknown")
            
            # Print with formatted spacing for readability
            print(f"{i:03d}. ARTIST: {artist:<20} | GENRE: {genre:<15} | AREA: {area:<15} | PLACE: {place}")
        else:
            print(f"{i:03d}. ARTIST: {artist:<20} | Status: {facts.get('status', 'Error')}")
            
    print("="*90 + "\n")

if __name__ == "__main__":
    list_all_artists()