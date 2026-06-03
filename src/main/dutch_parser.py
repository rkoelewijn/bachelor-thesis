import spacy
import re


try:
    nlp_nl = spacy.load("nl_core_news_sm")
except OSError:
    print("Error: Dutch spaCy model not found.")


def clean_cookie_text(text):
    """Verwijdert veelvoorkomende cookie-waarschuwingsteksten uit de gescrapte data."""
    
    # Een lijst met herkenbare zinnen uit je cookie-melding
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
    
    # Verwijder overtollige witregels die achterblijven
    return re.sub(r'\n\s*\n', '\n', cleaned_text).strip()

def prepare_dutch_sentences(raw_text, artist_name):
    doc = nlp_nl(raw_text)
    noise_words = ["ticket", "vvk", "euro", "uitverkocht", "bestel", "koop", "kassa"]
    prepared_sentences = []
    
    for sent in doc.sents:
        text = sent.text.strip()
        
        clean_text = clean_cookie_text(text)
        # Filter out promotional noise words and exclamation marks
        if text.count('!') > 1: continue
        if any(word in text.lower() for word in noise_words) and artist_name.lower() not in text.lower():
            continue
            
        # Ensure the sentence has enough substance or mentions the artist
        if len(text.split()) > 5 or artist_name.lower() in text.lower():
            # Inject Context
            # RoBERTa has problems finding whether the statement is true if the artist is not in the sentence. 
            contextualized = f"Over {artist_name}: {text}"
            prepared_sentences.append(contextualized)

            # Translate Dutch to English
            # Data shows that our pipeline performs better if the source text is in the same language as the hypothesis
            # translated = translate_nl_to_en(contextualized)
            # prepared_sentences.append(translated)
            
    return prepared_sentences


# Translation model for the source text 
from transformers import MarianMTModel, MarianTokenizer
mt_model_name = "Helsinki-NLP/opus-mt-nl-en"
mt_tokenizer = MarianTokenizer.from_pretrained(mt_model_name)
mt_model = MarianMTModel.from_pretrained(mt_model_name)

def translate_nl_to_en(text):
    tokens = mt_tokenizer([text], return_tensors="pt", padding=True, truncation=True)
    translated = mt_model.generate(**tokens)
    return mt_tokenizer.decode(translated[0], skip_special_tokens=True)