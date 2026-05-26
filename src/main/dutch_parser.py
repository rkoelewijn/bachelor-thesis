import spacy

try:
    nlp_nl = spacy.load("nl_core_news_sm")
except OSError:
    print("🚨 Error: Dutch spaCy model not found. Run: python3 -m spacy download nl_core_news_sm")
    print("🚨 Error: Dutch spaCy model not found. Run: python3 -m spacy download nl_core_news_sm")

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
    noise_words = ["ticket", "vvk", "euro", "uitverkocht", "bestel", "koop", "kassa"]
    dutch_sentences = []
    
    # 1. Parse Dutch text
    for sent in doc.sents:
        text = sent.text.strip()
        
        # Filter promotional noise
        if text.count('!') > 1: 
            continue
        # 1. Filter out promotional noise
        if text.count('!') > 1: continue
        if any(word in text.lower() for word in noise_words) and artist_name.lower() not in text.lower():
            continue
            
        # Keep substantive sentences
        # 2. Ensure the sentence has enough substance or mentions the artist
        if len(text.split()) > 5 or artist_name.lower() in text.lower():
            # 3. Inject Context
            contextualized = f"Over {artist_name}: {text}"
            dutch_sentences.append(contextualized)
    
    # 2. Generate MusicBrainz sentences (if data available)
    if mb_facts:
        mb_sentences = synthesize_musicbrainz_sentences(artist_name, mb_facts)
        mb_sentences_contextualized = [
            f"Over {artist_name}: {s}" for s in mb_sentences
        ]
        
        # 3. Prepend MB facts (high-confidence external knowledge comes first)
        return mb_sentences_contextualized + dutch_sentences
    
    return dutch_sentences

            translated = translate_nl_to_en(contextualized)
            prepared_sentences.append(translated)
            
    return prepared_sentences


from transformers import MarianMTModel, MarianTokenizer
mt_model_name = "Helsinki-NLP/opus-mt-nl-en"
mt_tokenizer = MarianTokenizer.from_pretrained(mt_model_name)
mt_model = MarianMTModel.from_pretrained(mt_model_name)

def translate_nl_to_en(text):
    tokens = mt_tokenizer([text], return_tensors="pt", padding=True, truncation=True)
    translated = mt_model.generate(**tokens)
    return mt_tokenizer.decode(translated[0], skip_special_tokens=True)