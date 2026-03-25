import spacy

# Load the Dutch model
nlp_nl = spacy.load("nl_core_news_sm")

def clean_dutch_premise(raw_text, artist_name):
    doc = nlp_nl(raw_text)
    cleaned_sentences = []
    
    # "Marketing" keywords to flag for removal
    noise_words = ["ticket", "vvk", "euro", "uitverkocht", "vol=vol", "bestel", "koop"]
    
    for sent in doc.sents:
        text = sent.text.strip()
        
        # 1. REMOVE: Sentences that are just marketing "shouting" (Multiple exclamation points)
        if text.count('!') > 1:
            continue
            
        # 2. REMOVE: Sentences that are purely about logistics/money
        if any(word in text.lower() for word in noise_words):
            continue
            
        # 3. KEEP: Sentences that mention the artist (High Signal)
        if artist_name.lower() in text.lower():
            cleaned_sentences.append(text)
            continue
            
        # 4. KEEP: Sentences that describe the "vibe" or genre (Medium Signal)
        # (Usually sentences longer than 5 words that don't look like navigation)
        if len(text.split()) > 5:
            cleaned_sentences.append(text)

    return " ".join(cleaned_sentences)

# --- THE VROEGZAT TEST CASE ---
messy_vroegzat = """
VroegZat brengt het nachtleven terug naar de avond! 
Tickets zijn slechts 15 euro in de vvk! Bestel nu!
Evenveel feest, maar eerder op de avond (19.30 tot 00.00 uur). 
Muzikaal gaat het heen en weer: van disco naar pop en rock. 
Zorg dat je op tijd binnen bent, want hier kun je niet vroeg genoeg hard gaan!!!
Vol=Vol! Koop je kaarten bij de kassa.
"""

print("--- RAW TEXT ---")
print(messy_vroegzat)

cleaned = clean_dutch_premise(messy_vroegzat, "VroegZat")

print("\n--- CLEANED 'GOLDILOCKS' PREMISE ---")
print(cleaned)