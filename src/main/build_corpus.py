import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import musicbrainzngs

# --- 1. CONFIGURATION ---
CURRENT_DIR = Path(__file__).resolve().parent
NEWSLETTERS_PATH = CURRENT_DIR / "newsletters.json"
OUTPUT_CORPUS_PATH = CURRENT_DIR / "full_evaluation_corpus.json"

musicbrainzngs.set_useragent(
    app="CloudspeakersThesisValidator",
    version="1.0",
    contact="ruben.koelewijn@ru.nl" 
)

# --- 2. SCRAPING & API ENGINES ---
def fetch_dynamic_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=15000) 
            full_html = page.content()
        except Exception as e:
            print(f"Playwright timeout: {e}")
            full_html = ""
        finally:
            browser.close()
        return full_html

def clean_html_with_bs4(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    for unwanted in soup(['nav', 'header', 'footer', 'script', 'style', 'aside', 'form', 'button']):
        unwanted.decompose()
    main_content = soup.find('main') or soup.find('article') or soup.body
    if not main_content: return ""
    
    clean_text_lines = [
        p.get_text(separator=" ", strip=True) 
        for p in main_content.find_all('p') 
        if len(p.get_text(separator=" ", strip=True)) > 40
    ]
    return "\n".join(clean_text_lines)

def get_artist_facts(artist_name):
    """Fetches factual baseline data from MusicBrainz."""
    try:
        result = musicbrainzngs.search_artists(query=artist_name, limit=1)
        if not result.get('artist-list'):
            return {"status": "Not Found"}

        match = result['artist-list'][0]
        time.sleep(1) # Crucial: Respect MB rate limit during batch ingestion
        
        return {
            "status": "Found",
            "name": match.get("name"),
            "type": match.get("type", "Unknown"), 
            "country": match.get("country", "Unknown"), 
            "area": match.get("area", {}).get("name", "Unknown")
        }
    except Exception as e:
        print(f"MusicBrainz Error: {e}")
        return {"status": "Error"}

# --- 3. MASTER LOOP ---
def main():
    print("="*60)
    print("CLOUDSPEAKERS DATA INGESTION: BUILDING CORPUS")
    print("="*60)

    try:
        with open(NEWSLETTERS_PATH, 'r', encoding='utf-8') as f:
            newsletters = json.load(f)
    except FileNotFoundError:
        return

    full_corpus = []
    total_entries = len([k for k in newsletters.keys() if k != "TEMPLATE"])
    print(f"Found {total_entries} entries. Beginning scrape...\n")

    for i, (key, entry) in enumerate(newsletters.items()):
        if key == "TEMPLATE": continue

        artist_raw = entry.get('act', 'Unknown')
        artist_clean = artist_raw.split('+')[0].strip()
        url = entry.get('url', '')
        summary = entry.get('summary', '')

        print(f"[{i}/{total_entries}] Processing: {artist_clean}")
        if not url or not summary: continue

        # 1. Get Doornroosje Text
        raw_html = fetch_dynamic_html(url)
        dutch_text = clean_html_with_bs4(raw_html)

        # 2. Get MusicBrainz Facts
        print("Fetching MusicBrainz baseline...")
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

    print("\n" + "="*60)
    print(f"Saving compiled corpus with {len(full_corpus)} valid entries...")
    with open(OUTPUT_CORPUS_PATH, 'w', encoding='utf-8') as f:
        json.dump(full_corpus, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()