import spacy

# Load the English parser
nlp_en = spacy.load("en_core_web_sm")

def extract_entity_claims(summary, artist_name):
    doc = nlp_en(summary)
    claims = []
    
    # 1. Define aliases the LLM might use for the artist
    aliases = ["he", "she", "they", "the band", "the artist", "the group", "the singer", "the duo"]
    artist_lower = artist_name.lower()
    
    for token in doc:
        # 2. Find the actions (Verbs)
        if token.pos_ == "VERB":
            # 3. Find who is doing the action (the subject)
            subj_token = next((child for child in token.lefts if child.dep_ in ["nsubj", "nsubjpass"]), None)
            
            is_target_entity = False
            
            if subj_token:
                # Check if the subject is the artist or an alias
                subj_text = " ".join([t.text.lower() for t in subj_token.subtree])
                if artist_lower in subj_text or any(alias == subj_text.strip() for alias in aliases):
                    is_target_entity = True
            else:
                # If there's no explicit subject (e.g., "Returns to Nijmegen AND plays songs")
                # we assume it belongs to our target entity.
                is_target_entity = True 

            # 4. If the action belongs to our artist, grab the FULL predicate
            if is_target_entity:
                # Get everything from the verb to the end of its logical chunk
                rights = list(token.rights)
                if rights:
                    # Find the furthest right word connected to this verb
                    end_idx = rights[-1].right_edge.i + 1
                    predicate = doc[token.i : end_idx].text
                    
                    # Construct the perfectly normalized claim
                    claim = f"{artist_name} {predicate}"
                    claims.append(claim)
                    
    return claims if claims else [summary]

# ==========================================
# TEST THE NEW LOGIC
# ==========================================

print("--- TEST 1: The Pronoun Resolution ---")
aatt_smry = "The English post-punk band And Also the Trees from Worcestershire performs songs from their new album 'The Devil's Door'."
for i, claim in enumerate(extract_entity_claims(aatt_smry, "And Also the Trees"), 1):
    print(f"Claim {i}: {claim}")

print("\n--- TEST 2: The Complex Fragment ---")
bertolf_smry = "Dutch musician Bertolf presents his bluegrass album 'Bluefinger vol. 2' with his excellent Dutch band."

for i, claim in enumerate(extract_entity_claims(bertolf_smry, "Bertolf"), 1):
    print(f"Claim {i}: {claim}")

print("\n--- TEST 3: Multiple Actions ---")
wyatt_smry = "Belgian band Wyatt E. performs long, hypnotic, and atmospheric compositions built on heavy, repetitive riffs and deep drones, often based on ancient mythology."

for i, claim in enumerate(extract_entity_claims(wyatt_smry, "Wyatt E."), 1):
    print(f"Claim {i}: {claim}")