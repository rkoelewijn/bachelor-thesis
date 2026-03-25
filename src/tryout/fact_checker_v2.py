import torch
import spacy
from transformers import AutoModelForSequenceClassification, AutoTokenizer

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

# --- PHASE 2: SUBTREE ATOMIC DECOMPOSITION (Improved) ---
def extract_atomic_claims(text):
    doc = nlp_en(text)
    claims = []
    for token in doc:
        if token.pos_ == "VERB":
            # Find the subject
            subj = next((child.text for child in token.lefts if child.dep_ == "nsubj"), "The artist")
            
            # IMPROVED: Grab full subtrees to prevent "mangled claims"
            parts = []
            for child in token.rights:
                if child.dep_ in ["dobj", "prep", "attr", "advmod", "pobj", "acomp", "xcomp"]:
                    parts.append(" ".join([t.text for t in child.subtree]))
            
            obj_phrase = " ".join(parts)
            if obj_phrase:
                claims.append(f"{subj} {token.text} {obj_phrase}")
                
    return claims if claims else [text]

# --- PHASE 3: CROSS-LINGUAL VERIFICATION ---
def run_nli_check(premise, hypothesis):
    tokens = tokenizer(premise, hypothesis, return_tensors="pt", truncation=True)
    with torch.no_grad():
        output = model(**tokens)
    probs = torch.nn.functional.softmax(output.logits, dim=-1)[0]
    return {"ent": probs[2].item() * 100, "neu": probs[1].item() * 100, "con": probs[0].item() * 100}

# --- THE ORCHESTRATOR ---
def validate(test_name, artist, dutch_source, summary):
    print(f"\n" + "-"*50 + f"\nRUN: {test_name}\n" + "-"*50)
    clean_p = clean_dutch_premise(dutch_source, artist)
    claims = extract_atomic_claims(summary)
    
    for i, claim in enumerate(claims, 1):
        res = run_nli_check(clean_p, claim)
        print(f"[{i}] CLAIM: '{claim}'")
        print(f"    🟢 {res['ent']:.1f}% Entail | 🟡 {res['neu']:.1f}% Neut | 🔴 {res['con']:.1f}% Cont")
        
        if res['ent'] > 75: print("    ✅ RESULT: VERIFIED")
        elif res['con'] > 50: print("    🚨 RESULT: HALLUCINATION")
        else: print("    ⚠️ RESULT: UNVERIFIED (Fluff/Missing Evidence)")

# ==========================================
# DATA: Newsletter data
# ==========================================

aatt_txt = "De Engelse postpunkband And Also the Trees, bekend om hun meeslepende liveoptredens, unieke stijl, suggestieve teksten en donkere jazzritmes, is na ruim 15 albums nog steeds springlevend. De band komt dan ook met hun nieuwe album ‘The Devil’s Door’ in het najaar naar Doornroosje! And Also the Trees werd opgericht in 1979, tijdens het geboorte van het postpunk-tijdperk in Worcestershire. Vanaf de start kon de band het goed vinden met The Cure.  Ze speelden en werkten nauw samen.  And Also the Trees is opgericht door zanger Simon Huw Jones en gitarist Justin Jones. Beiden zorgden ze voor een continue behouden aanwezigheid binnen de internationale postpunk- en alternatieve scene. De band staat bekend om hun meeslepende liveoptredens. Het muzikale recept is bekend en nauwelijks aangepast, maar And Also the Trees werkt het op plaat en op het podium tot in de puntjes uit. De half gezongen teksten op nauwkeurig afgestemde gitaarlijnen klinken verfijnd en natuurlijk.And Also the Trees bracht op 26 februari 2026 hun nieuwe album ‘The Devil’s Door’ uit. Deze ruwe maar prachtige parel is een aanrader voor liefhebbers van sombere, tijdloze liedjes, zoals The Cure, Killing Joke, Cocteau Twins, Tindersticks of Nick Cave die kan maken."
aatt_smry = "The English post-punk band And Also the Trees from Worcestershire performs songs from their new album 'The Devil's Door'."
 
bertwolf_txt = "Bertolf is terug met zijn bluegrass album ‘Bluefinger vol. 2’! In tegenstelling tot de eerdere versie ‘Bluefinger’ bestaat ‘Bluefinger vol. 2’ uit volledig nieuw en eigen repertoire. De plaat wordt gebracht met ongelofelijke instrumentale virtuositeit, aanstekelijk spelplezier en prachtige meerstemmige zang. Natuurlijk komt ook het beste van ‘Bluefinger’ voorbij, met af en toe een verrassende cover in een bluegrass bewerking. Bertolf kreeg bluegrass muziek met de paplepel ingegoten en vloog in 2022 naar Nashville om een lang gekoesterde droom te laten uitkomen. Hij nam er het album ‘Bluefinger’ op – een bluegrass album, met zijn grootste helden uit de scene Jerry Douglas en Stuart Duncan. Rond dit album volgde een uitgebreide tour langs Nederlandse theaters, podia en festivals met een band bestaande uit de beste muzikanten uit de nationale bluegrass-scene. De band raakte zo hecht en goed op elkaar ingespeeld, dat Bertolf besloot om ‘Bluefinger vol. 2’ op te nemen, maar dit keer met zijn uitmuntende Nederlandse band. De befaamde engineer en mixer Dave Sinko kwam overgevlogen om het album op te nemen te mixen."
bertwolf_smry = "Dutch musician Bertolf presents his bluegrass album 'Bluefinger vol. 2' with his excellent Dutch band."

wyatt_txt = "De muziek van het Belgische Wyatt E. ontvouwt zich als een ritueel: langzaam, meeslepend en hypnotiserend, gedragen door diepe drones, gelaagde doom melodieën en een indrukwekkende sfeer die zowel spiritueel als filmisch aanvoelt. Met een karakteristieke combinatie van zware, repetitieve riffs, trage spanningsopbouw en een sterk atmosferisch geluid creëert de band langgerekte composities die zowel intens als ingetogen zijn. De releases van Wyatt E. zijn vaak conceptueel opgebouwd rond huidige gebeurtenissen en nieuws artikelen die recentelijk verschenen zijn, waarbij albums functioneren als samenhangende, verhalende gehelen. Ook live staat de band bekend om intense, zorgvuldig opgebouwde shows die het publiek onderdompelen in een langzaam ontwikkelende, hypnotiserende sfeer. Daarmee positioneert Wyatt E. zich als een act die zowel binnen de heavy muziekwereld als bij een avontuurlijk, genre-overschrijdend publiek in de smaak valt. hun optreden tijdens Soulcrusher 2025 was weergaloos en smaakt absoluut naar meer!"
wyatt_smry = "Belgian band Wyatt E. performs long, hypnotic, and atmospheric compositions built on heavy, repetitive riffs and deep drones, often based on ancient mythology."

# ==========================================
# EXECUTE TESTS
# ==========================================
validate("aatt", "aatt", aatt_txt, aatt_smry)
validate("bertwolf", "bertwolf", bertwolf_txt, bertwolf_smry)
validate("wyatt", "wyatt", wyatt_txt, wyatt_smry)
