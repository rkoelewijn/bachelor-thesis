import spacy

try:
    nlp_nl = spacy.load("nl_core_news_sm")
except OSError:
    print("🚨 Error: Dutch spaCy model not found. Run: python3 -m spacy download nl_core_news_sm")

def prepare_dutch_sentences(raw_text, artist_name):
    doc = nlp_nl(raw_text)
    noise_words = ["ticket", "vvk", "euro", "uitverkocht", "bestel", "koop", "kassa", "vroegzat"]
    prepared_sentences = []
    
    for sent in doc.sents:
        text = sent.text.strip()
        
        # 1. Filter out promotional noise
        if text.count('!') > 1: continue
        if any(word in text.lower() for word in noise_words) and artist_name.lower() not in text.lower():
            continue
            
        # 2. Ensure the sentence has enough substance or mentions the artist
        if len(text.split()) > 5 or artist_name.lower() in text.lower():
            # 3. Inject Context
            contextualized = f"Over {artist_name}: {text}"
            prepared_sentences.append(contextualized)
            
    return prepared_sentences