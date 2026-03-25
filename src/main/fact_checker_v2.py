import sys # <-- FIX 1: Added missing import
import torch
import spacy
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import decomposer
import json
from pathlib import Path

# 1. THE BRIDGE
CURRENT_DIR = Path(__file__).resolve().parent
SRC_MAIN_DIR = CURRENT_DIR.parent / "main"
sys.path.append(str(SRC_MAIN_DIR))

# 2. DATA PATH
DATA_PATH = CURRENT_DIR.parent.parent / "data" / "newsletters.json"
WEB_PATH = CURRENT_DIR.parent.parent / "data" / "doornroosje.json"

# 1. INITIALIZATION
print("🚀 Launching Cloudspeakers Validator v1.1...")
nlp_nl = spacy.load("nl_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")

model_name = "joeddav/xlm-roberta-large-xnli"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# --- PHASE 1: SEMANTIC CLEANING ---
def clean_dutch_premise(raw_text, artist_name):
    doc = nlp_nl(raw_text)
    cleaned_sentences = []
    noise_words = ["ticket", "vvk", "euro", "uitverkocht", "bestel", "koop", "kassa", "vroegzat"]
    
    for sent in doc.sents:
        text = sent.text.strip()
        if text.count('!') > 1: continue
        if any(word in text.lower() for word in noise_words) and artist_name.lower() not in text.lower():
            continue
        if artist_name.lower() in text.lower() or len(text.split()) > 5:
            cleaned_sentences.append(text)
            
    return " ".join(cleaned_sentences)

# --- PHASE 3: CROSS-LINGUAL VERIFICATION ---
def run_nli_check(premise, hypothesis):
    tokens = tokenizer(premise, hypothesis, return_tensors="pt", truncation=True)
    with torch.no_grad():
        output = model(**tokens)
    probs = torch.nn.functional.softmax(output.logits, dim=-1)[0]
    return {"ent": probs[2].item() * 100, "neu": probs[1].item() * 100, "con": probs[0].item() * 100}

# --- THE ORCHESTRATOR ---
def validate(test_name, artist, dutch_source, summary):
    print(f"\n" + "="*50)
    print(f"🚀 RUNNING VALIDATION FOR: {artist}")
    print("="*50)
    
    # 🔴 TRACER 1: Check what we actually loaded from the JSON
    if not dutch_source:
        print("🚨 [DEBUG] RAW TEXT IS EMPTY! Check how doornroosje.json is being read.")
    else:
        # Print the first 300 characters of the raw text so it doesn't flood your screen
        print(f"📄 [DEBUG] RAW DUTCH TEXT RECEIVED:\n{str(dutch_source)[:300]}...\n")

    # Run Phase 1
    clean_p = clean_dutch_premise(str(dutch_source), artist)
    
    # 🟢 TRACER 2: Check what survived the cleaner
    if not clean_p.strip():
        print("🚨 [DEBUG] CLEANED PREMISE IS EMPTY! The cleaner deleted everything.")
    else:
        print(f"✨ [DEBUG] CLEANED PREMISE (Sent to RoBERTa):\n{clean_p}\n")
    
    print("-" * 50)

    # Run Phase 2
    claims = decomposer.extract_claims(summary, artist)
    
    for i, claim in enumerate(claims, 1):
        # We pass clean_p to the NLI model
        res = run_nli_check(clean_p, claim)
        print(f"[{i}] CLAIM: '{claim}'")
        print(f"    🟢 {res['ent']:.1f}% Entail | 🟡 {res['neu']:.1f}% Neut | 🔴 {res['con']:.1f}% Cont")
        
        if res['ent'] > 75: print("    ✅ RESULT: VERIFIED")
        elif res['con'] > 50: print("    🚨 RESULT: HALLUCINATION")
        else: print("    ⚠️ RESULT: UNVERIFIED (Fluff/Missing Evidence)")
    
    return claims
def run_benchmark():
    # 1. Load the database
    try:
        with open(DATA_PATH, 'r') as f:
            corpus = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found at {DATA_PATH}")
        return
    
    try:
        with open(WEB_PATH, 'r') as f:
            dutch = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found at {WEB_PATH}")
        return

    print(f"\n{'ARTIST':<20} | {'STATUS'}")
    print("-" * 40)

    # 2. Iterate through all entries
    for key, entry in corpus.items():
        if key == "TEMPLATE": continue
        
        # Pull data
        artist_raw = entry.get('act', 'Unknown')
        artist_clean = artist_raw.split('+')[0].strip()
        summary = entry.get('summary', '')

        # Check if it is Frank Boeijen
        if artist_clean == "Frank Boeijen" or "VroegZat": 
            
            # --- 🛠️ THE NESTED JSON FIX ---
            # 1. Get the specific data for THIS artist key (e.g., "FRANK_BOEIJEN")
            web_data = dutch.get(key, {}) 
            
            # 2. Extract the "text" field from inside that data
            dutch_text = web_data.get('text', '')
            
            # 3. Safety check just in case
            if not dutch_text:
                print(f"🚨 Error: Could not find 'text' for {key} in doornroosje.json")
                continue
            # -------------------------------

            claims = validate(artist_raw, artist_clean, dutch_text, summary)

            # 4. Report Results
            print(f"\n{artist_clean:<20} | Found {len(claims)} claims")
            print(f"Summary: {summary}")
            for i, c in enumerate(claims, 1):
                print(f"  └─ [{i}] {c}")
            print()
            
        else: 
            continue
        
if __name__ == "__main__":
    run_benchmark()