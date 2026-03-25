import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

print("Loading XLM-RoBERTa NLI Model... (This might take a minute to download the first time)")
# We use a model specifically trained on XNLI (Cross-lingual NLI)
model_name = "joeddav/xlm-roberta-large-xnli"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def check_hallucination(dutch_premise, english_hypothesis):
    print(f"\nSource (Dutch): '{dutch_premise}'")
    print(f"LLM Summary (English): '{english_hypothesis}'")
    
    # Tokenize the input pair
    tokens = tokenizer(dutch_premise, english_hypothesis, return_tensors="pt", truncation=True)
    
    # Run the model
    with torch.no_grad():
        output = model(**tokens)
    
    # Calculate probabilities using Softmax
    probabilities = torch.nn.functional.softmax(output.logits, dim=-1)[0]
    
    # The labels for this specific model are ordered: [Contradiction, Neutral, Entailment]
    contradiction_score = probabilities[0].item() * 100
    neutral_score = probabilities[1].item() * 100
    entailment_score = probabilities[2].item() * 100
    
    print("-" * 40)
    print(f"🟢 Entailment (True):     {entailment_score:.2f}%")
    print(f"🟡 Neutral (Unverified):  {neutral_score:.2f}%")
    print(f"🔴 Contradiction (False): {contradiction_score:.2f}%")
    
    # Thesis Logic: Flagging the hallucination
    if contradiction_score > 50:
        print("🚨 VERDICT: HALLUCINATION DETECTED! (High Contradiction)")
    elif entailment_score > 50:
        print("✅ VERDICT: FACTUALLY ACCURATE! (High Entailment)")
    else:
        print("⚠️ VERDICT: INCONCLUSIVE / NEUTRAL (The LLM added unverified fluff)")
    print("-" * 40)

# ==========================================
# THE THESIS TEST CASES
# ==========================================

# TEST 1 

dutch_txt = "VroegZat brengt het nachtleven terug naar de avond! Evenveel feest, maar eerder op de avond (19.30 tot 00.00 uur). Dus op een normale tijd naar bed, waardoor je de volgende dag gewoon fit bent. Win-win! Muzikaal gaat het heen en weer: van disco naar pop, van reggae naar rock en van happy naar hiphop, en die lekkere dansbare tunes die daartussen en daarbuiten vallen. DJ Rob de Nice en MC Rick Rossig gooien alles in de mix. Zorg dat je op tijd binnen bent, want hier kun je niet vroeg genoeg hard gaan!"
dutch_summary = "VroegZat is een feestconcept waarbij je al vroeg op de avond (19:30-00:00) uitgaat, zodat je de volgende dag nog fit bent. Je krijgt een mix van dansbare muziekstijlen zoals disco, pop, reggae, rock en hiphop, verzorgd door DJ Rob de Nice en MC Rick Rossig. Kom op tijd om niets te missen en volop te feesten."
dutch_sentence = "VroegZat is een feest waar je al vroeg op de avond (19:30-00:00) kunt genieten van een mix van dansbare muziek, zodat je toch op tijd naar bed gaat en de volgende dag fit bent."
english_smry = "A Dutch event bringing nightlife to the early evening with a mix of danceable tunes across genres."

# check_hallucination(dutch_txt, english_smry) 
# check_hallucination(dutch_summary, english_smry)
# check_hallucination(dutch_sentence, english_smry)


# TEST 2

full = "Frank Boeijen keert samen met zijn band terug naar Openluchttheater de Goffert, in zijn geliefde thuisstad Nijmegen. Iconische nummers als'Zwart Wit', 'Kronenburger Park' en 'De Verzoening' zullen de revue passeren, maar hij weet het publiek ook steevast te verrassen met nieuw werk. Een avond met Frank Boeijen staat garant voor een gevarieerde show op hoog niveau, waarbij Franks warme stem en zijn voortreffelijke muzikale begeleiders de luisteraar meenemen in een tocht langs ontroering en herkenning, langs avontuur en vakmanschap. Duik in een wereld vol poëtische nummers en verhalen over schoonheid, liefde en het leven. En dat alles in de intieme, groene omgeving van Openluchttheater de Goffert. “Frank Boeijen weet als vanouds vernieuwend voor de dag te komen. Hij verkeert in artistieke topvorm. Zijn stem heeft aan betekenisvolle gloed gewonnen. Er valt veel te genieten tijdens zijn voorstelling” - Popmagazine Heaven"
paragraph = "Frank Boeijen keert terug naar Openluchttheater de Goffert in Nijmegen voor een concert met zowel bekende nummers als nieuw werk. Samen met zijn band brengt hij een afwisselende en kwalitatief hoogstaande show, waarin zijn warme stem en poëtische liedjes het publiek meenemen langs emoties, herkenning en verhalen over het leven."
line = "Frank Boeijen geeft in Openluchttheater de Goffert een gevarieerd concert met bekende en nieuwe nummers, vol emotie, poëzie en muzikaal vakmanschap."
summary = "Dutch singer-songwriter Frank Boeijen returns to his beloved hometown of Nijmegen for an evening of poetic songs and stories."

check_hallucination(full, summary)
check_hallucination(paragraph, summary)
check_hallucination(line, summary)
