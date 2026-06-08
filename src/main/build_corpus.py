import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import musicbrainzngs
import data_loader

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent
NEWSLETTERS_PATH = ROOT_DIR / "data" / "corpus" / "newsletters.json"

musicbrainzngs.set_useragent(
    app="CloudspeakersThesisValidator",
    version="1.0",
    contact="ruben.koelewijn@ru.nl" 
)

def fetch_dynamic_html(page, url):
    """Navigates to the URL using the pre-allocated browser page."""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return page.content()
    except Exception as e:
        print(f"🚨 Error scraping {url}: {e}")
        return ""

def clean_html_with_bs4(html_content):
    """Uses BeautifulSoup to clean HTML and return body text, ignoring cookie banners."""
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Strip out standard non-content tags
    for unwanted in soup(['nav', 'header', 'footer', 'script', 'style', 'aside', 'form', 'button']):
        unwanted.decompose()
        
    main_content = soup.find('main') or soup.find('article') or soup.body
    if not main_content: 
        return ""
    
    # Blocklist of phrases from the Dutch cookie notice
    cookie_blocklist = [
        "We gebruiken cookies om",
        "Noodzakelijke cookies zijn",
        "Deze cookies slaan geen persoonlijk",
        "Functionele cookies helpen",
        "Analytische cookies worden",
        "Prestatiecookies worden",
        "Advertentiecookies worden",
        "Andere niet-gecategoriseerde cookies"
    ]
    
    clean_text_lines = []
    
    for p in main_content.find_all('p'):
        text = p.get_text(separator=" ", strip=True)
        
        # Check if text meets length requirement
        if len(text) > 40:
            # Check if it matches anything in our blocklist (case-insensitive)
            is_cookie_text = any(phrase.lower() in text.lower() for phrase in cookie_blocklist)
            
            if not is_cookie_text:
                clean_text_lines.append(text)
                
    return "\n".join(clean_text_lines)

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
    except Exception as e:
        print(f"MusicBrainz Error: {e}")
        return {"status": "Error"}

def main():
    print("="*60)
    print("CLOUDSPEAKERS DATA INGESTION: BUILDING CORPUS")
    print("="*60)

    try:
        with open(NEWSLETTERS_PATH, 'r', encoding='utf-8') as f:
            newsletters = json.load(f)
    except FileNotFoundError:
        print(f"Ingestion aborted: Could not find raw input file at '{NEWSLETTERS_PATH}'")
        return

    full_corpus = []
    total_entries = len([k for k in newsletters.keys() if k != "TEMPLATE"])
    print(f"Found {total_entries} entries. Beginning scrape...\n")

    # --- ARCHITECTURE FIX: Initialize Playwright and Browser ONCE outside the loop ---
    print("Launching stable browser instance...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-gpu",           # Stops WSL2 graphics conflicts
                "--single-process"         # Aggregates threads to prevent segmentation faults
            ]
        )
        context = browser.new_context()
        page = context.new_page()

        for i, (key, entry) in enumerate(newsletters.items()):
            # Avoiding template that is put into newsletter file to make copying easier. 
            if key == "TEMPLATE": continue

            artist_raw = entry.get('act', 'Unknown')
            artist_clean = artist_raw.split('+')[0].strip()
            url = entry.get('url', '')
            summary = entry.get('summary', '')

            print(f"[{i}/{total_entries}] Processing: {artist_clean}")
            if not url or not summary: continue

            # --- Pass the initialized 'page' object into the scraping function ---
            raw_html = fetch_dynamic_html(page, url)
            dutch_text = clean_html_with_bs4(raw_html)

            print(" Fetching MusicBrainz baseline...")
            mb_facts = get_artist_facts(artist_clean)

            if dutch_text:
                print(" Scrape & API successful.")
                full_corpus.append({
                    "artist": artist_clean,
                    "url": url,
                    "summary": summary,
                    "dutch_text": dutch_text,
                    "musicbrainz_facts": mb_facts
                })
        
        print("Scraping complete. Closing browser.")

    print("\n" + "="*60)
    print(f"Saving compiled corpus with {len(full_corpus)} valid entries...")
    
    data_loader.save_evaluation_corpus(full_corpus)

if __name__ == "__main__":
    main()