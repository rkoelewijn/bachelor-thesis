import spacy
import re


try:
    nlp_nl = spacy.load("nl_core_news_sm")
except OSError:
    print("Error: Dutch spaCy model not found.")


def clean_cookie_text(text):
    """Deletes cookie text that occurs when scraping the webpage. """   
    patterns = [
        r"We gebruiken cookies om je ervaring op onze website te verbeteren\..*?privacybeleid\.",
        r"Noodzakelijke cookies zijn cruciaal voor de basisfuncties van de website.*",
        r"Functionele cookies helpen bepaalde functionaliteiten uit te voeren.*",
        r"Analytische cookies worden gebruikt om te begrijpen hoe bezoekers omgaan met de website.*",
        r"Prestatiecookies worden gebruikt om de belangrijkste prestatie-indexen.*",
        r"Advertentiecookies worden gebruikt om bezoekers gepersonaliseerde advertenties.*",
        r"Andere niet-gecategoriseerde cookies zijn cookies.*"
    ]
    
    cleaned_text = text
    for pattern in patterns:
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.DOTALL | re.IGNORECASE)
    
    return re.sub(r'\n\s*\n', '\n', cleaned_text).strip()

def synthesize_musicbrainz_sentences(artist_name, mb_facts):
    """
    Convert MusicBrainz structured data into natural language sentences.
    These get added to the NLI premise to help verify facts not in Dutch text.
    """
    if mb_facts.get("status") != "Found":
        return []
    
    sentences = []
    
    # Country/origin mapping
    country_adjectives = {
        'NL': 'Dutch',
        'GB': 'English', 
        'US': 'American',
        'BE': 'Belgian',
        'DE': 'German',
        'SE': 'Swedish',
        'AU': 'Australian',
        'IT': 'Italian',
        'CA': 'Canadian',
        'CO': 'Colombian',
        'FR': 'French',
        'ES': 'Spanish'
    }
    
    artist_type = mb_facts.get('type', 'Unknown')
    country = mb_facts.get('country', 'Unknown')
    area = mb_facts.get('area', 'Unknown')
    country_adj = country_adjectives.get(country, area)
    
    # Generate type + country sentences
    if artist_type == 'Group' and country != 'Unknown':
        sentences.append(f"{artist_name} is a {country_adj} band.")
        sentences.append(f"The band {artist_name} is from {area}.")
        sentences.append(f"{artist_name} is a musical group.")
    
    elif artist_type == 'Person' and country != 'Unknown':
        sentences.append(f"{artist_name} is a {country_adj} artist.")
        sentences.append(f"{artist_name} is from {area}.")
        sentences.append(f"{artist_name} is a solo artist.")
    
    # Fallback: at least assert existence
    if not sentences:
        sentences.append(f"{artist_name} is a known musical artist.")
    
    return sentences

def prepare_dutch_sentences(raw_text, artist_name, mb_facts=None):
    """
    Parse Dutch source text into sentences and optionally augment with 
    MusicBrainz-synthesized facts.
    
    Args:
        raw_text: Raw Dutch text from scraping
        artist_name: Name of the artist
        mb_facts: MusicBrainz facts dict (optional, from data_loader)
    
    Returns:
        List of contextualized sentences for NLI verification
    """
    doc = nlp_nl(raw_text)
    noise_words = ["ticket", "vvk", "euro", "uitverkocht", "bestel", "koop", "kassa", "mailbox", 
        "is gevestigd op",                      # Locatie Doornroosje/Merleyn
        "is gevestigd aan",                     # Locatie De Vereeniging
        "klik voor alle info over jouw bezoek", # Bezoekersinfo
        "klik voor route",                      # Route info
        "schrijf je in en ontvang wekelijks",   # Nieuwsbrief
        "neem een kijkje op onze",              # Promotie andere pagina's
        "meld je aan voor updates"              # Ticket updates
        ]
    prepared_sentences = []
    
    # 1. Parse Dutch text
    for sent in doc.sents:
        text = sent.text.strip()
        
        clean_text = clean_cookie_text(text)
        if not clean_text:
            continue
            
        # Filter out promotional noise and excessive exclamation marks
        if clean_text.count('!') > 1: 
            continue
            
        if any(word in clean_text.lower() for word in noise_words) and artist_name.lower() not in clean_text.lower():
            continue
            
        # Ensure the sentence has enough substance or explicitly mentions the artist
        if len(clean_text.split()) > 5 or artist_name.lower() in clean_text.lower():
            
            # Inject Context: Helps RoBERTa resolve coreferences if the artist isn't named in the sentence
            contextualized = f"Over {artist_name}: {clean_text}"
            prepared_sentences.append(contextualized)
            
    return prepared_sentences


