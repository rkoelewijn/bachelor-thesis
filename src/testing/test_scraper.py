import sys
import time
import re
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
import html2text

# --- PATH CONFIGURATION ---
CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent
SRC_MAIN_DIR = SRC_DIR / "main"
sys.path.append(str(SRC_MAIN_DIR))

# Import your data_loader just to get the correct file paths
try:
    import data_loader
except ImportError:
    print(f"🚨 Error: Could not import data_loader. Looked in {SRC_MAIN_DIR}")
    sys.exit(1)

# --- SCRAPING & CLEANING FUNCTIONS ---
def fetch_dynamic_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        full_html = page.content()
        browser.close()
        return full_html

def convert_to_markdown(html_content):
    h = html2text.HTML2Text()
    h.ignore_links = True
    return h.handle(html_content)

def clean_doornroosje_markdown(raw_markdown):
    if "Toon resultaten" in raw_markdown:
        content = raw_markdown.split("Toon resultaten")[1]
    else:
        content = raw_markdown

    bottom_markers = ["route & bezoek", "Programma", "Schrijf je in", "## media"]
    for marker in bottom_markers:
        if marker in content:
            content = content.split(marker)[0]

    content = re.sub(r'!?\[.*?\]\(.*?\)', '', content, flags=re.DOTALL)

    lines = content.split('\n')
    pure_text_lines = []
    skip_next_line = False
    metadata_headers = ['locatie:', 'datum:', 'zaal open:', 'start:', 'deuren sluiten:', 'einde:']

    for line in lines:
        clean_line = line.strip()
        if not clean_line or clean_line.startswith('#') or ('Tickets' in clean_line and '€' in clean_line):
            continue
        if clean_line in metadata_headers:
            skip_next_line = True
            continue
        if skip_next_line:
            skip_next_line = False
            continue
        pure_text_lines.append(clean_line)

    if pure_text_lines and ("doornroosjepas" in pure_text_lines[-1].lower() or pure_text_lines[-1].count(',') > 2):
        pure_text_lines.pop()

    return "\n".join(pure_text_lines)

# --- MAIN TESTING LOOP ---
def main():
    print("="*60)
    print("⚙️ RUNNING BATCH SCRAPER TEST ON NEWSLETTERS.JSON")
    print("="*60)

    # 1. Open the newsletters.json file directly
    try:
        with open(data_loader.NEWSLETTERS_PATH, 'r') as f:
            newsletters_data = json.load(f)
    except Exception as e:
        print(f"🚨 Error loading newsletters.json: {e}")
        return

    # 2. Extract every URL from the raw JSON
    urls = []
    for key, entry in newsletters_data.items():
        if key == "TEMPLATE": 
            continue
        url = entry.get("url")
        if url:
            urls.append(url)
    
    # 3. Filter for Doornroosje URLs specifically
    doornroosje_urls = [url for url in urls if "doornroosje.nl" in url]
    
    if not doornroosje_urls:
        print("No valid Doornroosje URLs found in newsletters.json.")
        return

    print(f"Found {len(doornroosje_urls)} Doornroosje URLs to test.\n")

    successful = 0
    failed = 0
    start_time = time.time()

    # 4. Run the test loop
    for i, url in enumerate(doornroosje_urls, 1):
        print(f"[{i}/{len(doornroosje_urls)}] Testing: {url}")
        try:
            raw_md = convert_to_markdown(fetch_dynamic_html(url))
            clean_text = clean_doornroosje_markdown(raw_md)
            
            if len(clean_text) < 20:
                print("   ⚠️ WARNING: Extracted text is unusually short or empty.")
                failed += 1
            else:
                preview = clean_text[:100].replace('\n', ' ') + "..."
                print(f"   ✅ Success. Preview: '{preview}'")
                successful += 1
                
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)}")
            failed += 1

    elapsed = time.time() - start_time
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print(f"Total processed: {len(doornroosje_urls)}")
    print(f"Successful:      {successful}")
    print(f"Failed/Empty:    {failed}")
    print(f"Time elapsed:    {elapsed:.2f} seconds")
    print("="*60)

if __name__ == "__main__":
    main()