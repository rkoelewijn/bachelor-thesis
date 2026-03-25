import torch
import spacy
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# 1. Load the "Separator" (spaCy) and the "Judge" (XLM-RoBERTa)
print("Loading Models... (This takes a moment)")
nlp = spacy.load("en_core_web_sm")
model_name = "joeddav/xlm-roberta-large-xnli"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def extract_atomic_claims(text):
    """Phase 2: Decomposition - Breaking the summary into bite-sized facts."""
    doc = nlp(text)
    claims = []
    for token in doc:
        if token.pos_ == "VERB":
            subj = next((child.text for child in token.lefts if child.dep_ == "nsubj"), "The artist")
            # Capture the meaningful phrase (Object/Prepositional phrase)
            obj_phrase = " ".join([t.text for t in token.rights if t.dep_ in ["dobj", "prep", "attr", "advmod", "pobj"]])
            if obj_phrase:
                claims.append(f"{subj} {token.text} {obj_phrase}")
    return claims

def run_nli_check(premise, hypothesis):
    """Phase 3: The Cross-Lingual NLI Verdict."""
    tokens = tokenizer(premise, hypothesis, return_tensors="pt", truncation=True)
    with torch.no_grad():
        output = model(**tokens)
    probs = torch.nn.functional.softmax(output.logits, dim=-1)[0]
    return {
        "entailment": probs[2].item() * 100,
        "neutral": probs[1].item() * 100,
        "contradiction": probs[0].item() * 100
    }

def validate_event(test_name, dutch_source, english_summary):
    print("\n" + "="*80)
    print(f"RUNNING: {test_name}")
    print(f"SOURCE (NL): {dutch_source[:100]}...")
    print(f"SUMMARY (EN): {english_summary}")
    print("="*80)

    claims = extract_atomic_claims(english_summary)
    
    if not claims:
        # Fallback if the parser misses the verb
        claims = [english_summary]

    for i, claim in enumerate(claims, 1):
        scores = run_nli_check(dutch_source, claim)
        
        print(f"\n🔍 CLAIM {i}: '{claim}'")
        print(f"   🟢 Entailment: {scores['entailment']:.1f}%")
        print(f"   🟡 Neutral:    {scores['neutral']:.1f}%")
        print(f"   🔴 Contradict: {scores['contradiction']:.1f}%")
        
        if scores['entailment'] > 75:
            print("   ✅ VERDICT: VERIFIED (Solid Evidence)")
        elif scores['contradiction'] > 50:
            print("   🚨 VERDICT: HALLUCINATION (Direct Conflict)")
        else:
            print("   ⚠️ VERDICT: UNVERIFIED / NEUTRAL (Evidence missing in source)")

# ==========================================
# TEST 1: VROEGZAT (Safety Check)
# ==========================================
# dutch_txt = "VroegZat brengt het nachtleven terug naar de avond! Evenveel feest, maar eerder op de avond (19.30 tot 00.00 uur). Dus op een normale tijd naar bed, waardoor je de volgende dag gewoon fit bent. Win-win! Muzikaal gaat het heen en weer: van disco naar pop, van reggae naar rock en van happy naar hiphop, en die lekkere dansbare tunes die daartussen en daarbuiten vallen. DJ Rob de Nice en MC Rick Rossig gooien alles in de mix. Zorg dat je op tijd binnen bent, want hier kun je niet vroeg genoeg hard gaan!"
# dutch_summary = "VroegZat is een feestconcept waarbij je al vroeg op de avond (19:30-00:00) uitgaat, zodat je de volgende dag nog fit bent. Je krijgt een mix van dansbare muziekstijlen zoals disco, pop, reggae, rock en hiphop, verzorgd door DJ Rob de Nice en MC Rick Rossig. Kom op tijd om niets te missen en volop te feesten."
# dutch_sentence = "VroegZat is een feest waar je al vroeg op de avond (19:30-00:00) kunt genieten van een mix van dansbare muziek, zodat je toch op tijd naar bed gaat en de volgende dag fit bent."
# english_smry = "A Dutch event bringing nightlife to the early evening with a mix of danceable tunes across genres."

# print("\n--- STARTING TEST 1: VROEGZAT ---")
# validate_event("VroegZat: Full Text", dutch_txt, english_smry)
# validate_event("VroegZat: Dutch Summary", dutch_summary, english_smry)
# validate_event("VroegZat: Single Sentence", dutch_sentence, english_smry)


# # ==========================================
# # TEST 2: FRANK BOEIJEN (Evidence Gradient)
# # ==========================================
# full = "Frank Boeijen keert samen met zijn band terug naar Openluchttheater de Goffert, in zijn geliefde thuisstad Nijmegen. Iconische nummers als'Zwart Wit', 'Kronenburger Park' en 'De Verzoening' zullen de revue passeren, maar hij weet het publiek ook steevast te verrassen met nieuw werk. Een avond met Frank Boeijen staat garant voor een gevarieerde show op hoog niveau, waarbij Franks warme stem en zijn voortreffelijke muzikale begeleiders de luisteraar meenemen in een tocht langs ontroering en herkenning, langs avontuur en vakmanschap. Duik in een wereld vol poëtische nummers en verhalen over schoonheid, liefde en het leven. En dat alles in de intieme, groene omgeving van Openluchttheater de Goffert. “Frank Boeijen weet als vanouds vernieuwend voor de dag te komen. Hij verkeert in artistieke topvorm. Zijn stem heeft aan betekenisvolle gloed gewonnen. Er valt veel te genieten tijdens zijn voorstelling” - Popmagazine Heaven"
# paragraph = "Frank Boeijen keert terug naar Openluchttheater de Goffert in Nijmegen voor een concert met zowel bekende nummers als nieuw werk. Samen met zijn band brengt hij een afwisselende en kwalitatief hoogstaande show, waarin zijn warme stem en poëtische liedjes het publiek meenemen langs emoties, herkenning en verhalen over het leven."
# line = "Frank Boeijen geeft in Openluchttheater de Goffert een gevarieerd concert met bekende en nieuwe nummers, vol emotie, poëzie en muzikaal vakmanschap."
# summary = "Dutch singer-songwriter Frank Boeijen returns to his beloved hometown of Nijmegen for an evening of poetic songs and stories."

# print("\n--- STARTING TEST 2: FRANK BOEIJEN ---")
# validate_event("Boeijen: Full Bio", full, summary)
# validate_event("Boeijen: Paragraph", paragraph, summary)
# validate_event("Boeijen: Single Line", line, summary)


# New test: 
aatt_txt = "De Engelse postpunkband And Also the Trees, bekend om hun meeslepende liveoptredens, unieke stijl, suggestieve teksten en donkere jazzritmes, is na ruim 15 albums nog steeds springlevend. De band komt dan ook met hun nieuwe album ‘The Devil’s Door’ in het najaar naar Doornroosje! And Also the Trees werd opgericht in 1979, tijdens het geboorte van het postpunk-tijdperk in Worcestershire. Vanaf de start kon de band het goed vinden met The Cure.  Ze speelden en werkten nauw samen.  And Also the Trees is opgericht door zanger Simon Huw Jones en gitarist Justin Jones. Beiden zorgden ze voor een continue behouden aanwezigheid binnen de internationale postpunk- en alternatieve scene. De band staat bekend om hun meeslepende liveoptredens. Het muzikale recept is bekend en nauwelijks aangepast, maar And Also the Trees werkt het op plaat en op het podium tot in de puntjes uit. De half gezongen teksten op nauwkeurig afgestemde gitaarlijnen klinken verfijnd en natuurlijk.And Also the Trees bracht op 26 februari 2026 hun nieuwe album ‘The Devil’s Door’ uit. Deze ruwe maar prachtige parel is een aanrader voor liefhebbers van sombere, tijdloze liedjes, zoals The Cure, Killing Joke, Cocteau Twins, Tindersticks of Nick Cave die kan maken."
aatt_smry = "The English post-punk band And Also the Trees from Worcestershire performs songs from their new album 'The Devil's Door'."
 
bertwolf_txt = "Bertolf is terug met zijn bluegrass album ‘Bluefinger vol. 2’! In tegenstelling tot de eerdere versie ‘Bluefinger’ bestaat ‘Bluefinger vol. 2’ uit volledig nieuw en eigen repertoire. De plaat wordt gebracht met ongelofelijke instrumentale virtuositeit, aanstekelijk spelplezier en prachtige meerstemmige zang. Natuurlijk komt ook het beste van ‘Bluefinger’ voorbij, met af en toe een verrassende cover in een bluegrass bewerking. Bertolf kreeg bluegrass muziek met de paplepel ingegoten en vloog in 2022 naar Nashville om een lang gekoesterde droom te laten uitkomen. Hij nam er het album ‘Bluefinger’ op – een bluegrass album, met zijn grootste helden uit de scene Jerry Douglas en Stuart Duncan. Rond dit album volgde een uitgebreide tour langs Nederlandse theaters, podia en festivals met een band bestaande uit de beste muzikanten uit de nationale bluegrass-scene. De band raakte zo hecht en goed op elkaar ingespeeld, dat Bertolf besloot om ‘Bluefinger vol. 2’ op te nemen, maar dit keer met zijn uitmuntende Nederlandse band. De befaamde engineer en mixer Dave Sinko kwam overgevlogen om het album op te nemen te mixen."
bertwolf_smry = "Dutch musician Bertolf presents his bluegrass album 'Bluefinger vol. 2' with his excellent Dutch band."

wyatt_txt = "De muziek van het Belgische Wyatt E. ontvouwt zich als een ritueel: langzaam, meeslepend en hypnotiserend, gedragen door diepe drones, gelaagde doom melodieën en een indrukwekkende sfeer die zowel spiritueel als filmisch aanvoelt. Met een karakteristieke combinatie van zware, repetitieve riffs, trage spanningsopbouw en een sterk atmosferisch geluid creëert de band langgerekte composities die zowel intens als ingetogen zijn. De releases van Wyatt E. zijn vaak conceptueel opgebouwd rond huidige gebeurtenissen en nieuws artikelen die recentelijk verschenen zijn, waarbij albums functioneren als samenhangende, verhalende gehelen. Ook live staat de band bekend om intense, zorgvuldig opgebouwde shows die het publiek onderdompelen in een langzaam ontwikkelende, hypnotiserende sfeer. Daarmee positioneert Wyatt E. zich als een act die zowel binnen de heavy muziekwereld als bij een avontuurlijk, genre-overschrijdend publiek in de smaak valt. hun optreden tijdens Soulcrusher 2025 was weergaloos en smaakt absoluut naar meer!"
wyatt_smry = "Belgian band Wyatt E. performs long, hypnotic, and atmospheric compositions built on heavy, repetitive riffs and deep drones, often based on ancient mythology."

validate_event("aatt", aatt_txt, aatt_smry)
validate_event("bertwolf", bertwolf_txt, bertwolf_smry)
validate_event("wyatt", wyatt_txt, wyatt_smry)
