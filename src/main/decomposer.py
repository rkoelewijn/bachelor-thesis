import spacy

nlp = spacy.load("en_core_web_sm")

def extract_claims(summary, artist_name):
    doc = nlp(summary)
    claims = []
    
    for token in doc:
        if token.pos_ == "VERB":
            verb_str = token.text
            
            # 1. Get the Direct Object (and its attached adjectives)
            # E.g., not just "nightlife", but "the vibrant nightlife"
            dobj_str = ""
            for child in token.rights:
                if child.dep_ == "dobj":
                    dobj_str = " ".join([t.text for t in child.subtree])
                    break # Usually only one direct object
            
            # 2. Get the Modifiers (The "OTHER" prepositions/clauses)
            modifiers = []
            for child in token.rights:
                # We ignore the direct object, punctuation, and 'and/but'
                if child.dep_ not in ("dobj", "punct", "cc", "conj"):
                    phrase = " ".join([t.text for t in child.subtree])
                    modifiers.append(phrase)
            
            # 3. Construct the Base Action
            # E.g., "VroegZat bringing nightlife" or "Frank Boeijen returns"
            base_action = f"{artist_name} {verb_str} {dobj_str}".strip()
            
            # 4. Generate the Atomic Claims!
            if not modifiers:
                # If there are no extra details, just use the base action
                claims.append(base_action)
            else:
                # If there are details, create a separate claim for EACH detail
                for mod in modifiers:
                    claim = f"{base_action} {mod}"
                    # Clean up double spaces
                    clean_claim = " ".join(claim.split())
                    claims.append(clean_claim)
                    
    # Fallback just in case
    return claims if claims else [summary]