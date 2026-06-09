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
    
    clean_p = clean_dutch_premise(str(dutch_source), artist)
    claims = decomposer.extract_claims(summary, artist)
    
    # We parse the cleaned Dutch text into individual sentences
    dutch_sentences = [sent.text.strip() for sent in nlp_nl(clean_p).sents if len(sent.text.strip()) > 5]
    
    for i, claim in enumerate(claims, 1):
        print(f"[{i}] CLAIM: '{claim}'")
        
        best_entail = 0
        best_res = None
        best_evidence = ""
        
       # 🔍 THE FACT HUNTER: Test the claim against each Dutch sentence individually
        for sentence in dutch_sentences:
            
            # --- THE FIX: CONTEXT INJECTION ---
            # We anchor the artist's name to the sentence so RoBERTa knows the subject
            contextual_sentence = f"Over {artist}: {sentence}"
            
            # We test the injected sentence, but...
            res = run_nli_check(contextual_sentence, claim)
            
            if res['ent'] > best_entail:
                best_entail = res['ent']
                best_res = res
                # ...we still save the original sentence so your printout looks clean!
                best_evidence = sentence

        # Print the best result found
        if best_res:
            print(f"    🔎 EVIDENCE: '{best_evidence}'")
            print(f"    📊 SCORES: 🟢 {best_res['ent']:.1f}% Entail | 🟡 {best_res['neu']:.1f}% Neut | 🔴 {best_res['con']:.1f}% Cont")
            
            # Adjusted thresholds to account for cross-lingual fuzziness and grammar fragments
            if best_res['ent'] > 60: 
                print("    ✅ RESULT: VERIFIED")
            elif best_res['con'] > 60: 
                print("    🚨 RESULT: HALLUCINATION")
            else: 
                print("    ⚠️ RESULT: UNVERIFIED (Fluff/Missing Evidence)")
        else:
            print("    ⚠️ RESULT: UNVERIFIED (No valid Dutch sentences to check against)")
    
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