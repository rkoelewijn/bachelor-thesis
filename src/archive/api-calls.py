from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def fetch_dynamic_html(url):
    """Fetches fully rendered HTML, waiting for JavaScript to execute."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        full_html = page.content()
        browser.close()
        return full_html

def clean_html_with_bs4(html_content):
    """
    Uniformly extracts descriptive text by targeting semantic HTML tags.
    This approach is highly transferable to other venue websites.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Nuke the noisy structural elements
    for unwanted in soup(['nav', 'header', 'footer', 'script', 'style', 'aside', 'form', 'button']):
        unwanted.decompose()

    # 2. Target the main content area if it exists (improves accuracy)
    main_content = soup.find('main') or soup.find('article') or soup.body

    # 3. Extract paragraph text
    # Venue descriptions are almost universally stored in <p> tags. 
    # Metadata (prices, dates) usually live in <span>, <div>, or <li> tags.
    paragraphs = main_content.find_all('p')
    
    clean_text_lines = []
    for p in paragraphs:
        text = p.get_text(separator=" ", strip=True)
        
        # 4. Length Heuristic: Ignore short UI remnants (e.g., "Tickets €19", "Read more")
        # A standard descriptive sentence is usually at least 40 characters long.
        if len(text) > 40: 
            clean_text_lines.append(text)

    return "\n".join(clean_text_lines)

# --- Example Usage ---
if __name__ == "__main__":
    urls = [
        "https://doornroosje.nl/event/adult-dvd", 
        "https://www.doornroosje.nl/event/vroegzat-10/", 
        "https://doornroosje.nl/event/frank-boeijen-19/", 
        "https://doornroosje.nl/event/and-also-the-trees/"
    ] 

    for url in urls: 
        print(f"📥 Fetching: {url}...")
        raw_html = fetch_dynamic_html(url)
        final_clean_text = clean_html_with_bs4(raw_html)
        
        print("\n" + "="*50)
        print(final_clean_text)
        print("="*50 + "\n")