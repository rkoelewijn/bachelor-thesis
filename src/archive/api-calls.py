from playwright.sync_api import sync_playwright
import html2text

def fetch_dynamic_html(url):
    # Start the Playwright browser
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Go to the URL and wait for the network to be idle (JS finished loading)
        page.goto(url, wait_until="networkidle")
        
        # Optional: Wait for a specific element to appear to ensure text is loaded
        # page.wait_for_selector('.event-description') 
        
        # Extract the fully rendered HTML
        full_html = page.content()
        browser.close()
        
        return full_html

def convert_to_markdown(html_content):
    # Pass the rendered HTML into your existing html2text setup
    h = html2text.HTML2Text()
    h.ignore_links = True
    return h.handle(html_content)

import re

def clean_doornroosje_markdown(raw_markdown):
    # 1. Bypass the top menu
    if "Toon resultaten" in raw_markdown:
        content = raw_markdown.split("Toon resultaten")[1]
    else:
        content = raw_markdown

    # 2. Cut off the bottom using the newsletter prompt or standard headers
    bottom_markers = ["route & bezoek", "Programma", "Schrijf je in", "## media"]
    for marker in bottom_markers:
        if marker in content:
            content = content.split(marker)[0]

    # 3. Use Regex to completely remove markdown image/URL links, even if split across newlines
    content = re.sub(r'!?\[.*?\]\(.*?\)', '', content, flags=re.DOTALL)

    # 4. Filter line-by-line for metadata
    lines = content.split('\n')
    pure_text_lines = []
    skip_next_line = False

    metadata_headers = ['locatie:', 'datum:', 'zaal open:', 'start:', 'deuren sluiten:', 'einde:']

    for line in lines:
        clean_line = line.strip()

        if not clean_line:
            continue
            
        if clean_line.startswith('#'):
            continue

        if 'Tickets' in clean_line and '€' in clean_line:
            continue

        if clean_line in metadata_headers:
            skip_next_line = True
            continue
        
        if skip_next_line:
            skip_next_line = False
            continue

        pure_text_lines.append(clean_line)

    # 5. Catch stray genre lists at the very end (e.g., "indierock, pop noir, doornroosjepas")
    if pure_text_lines and ("doornroosjepas" in pure_text_lines[-1].lower() or pure_text_lines[-1].count(',') > 2):
        pure_text_lines.pop()

    return "\n".join(pure_text_lines)


# Example usage in your script:
urls = [
    "https://doornroosje.nl/event/adult-dvd", 
    "https://www.doornroosje.nl/event/vroegzat-10/", 
    "https://doornroosje.nl/event/frank-boeijen-19/", 
    "https://doornroosje.nl/event/and-also-the-trees/"
] 

for url in urls: 
    print(f"📥 Fetching: {url}...")
    raw_md = convert_to_markdown(fetch_dynamic_html(url))
    final_clean_text = clean_doornroosje_markdown(raw_md)
    
    print("\n" + "="*50)
    print(final_clean_text)
    print("="*50 + "\n")

