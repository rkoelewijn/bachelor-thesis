import spacy

nlp = spacy.load("en_core_web_sm")

def extract_claims(summary, artist_name):
    doc = nlp(summary)
    claims = []
    
    for token in doc:
        if token.pos_ == "VERB":
            verb_str = token.text
            
            # 1. Find the Subject Token
            subj_token = None
            for child in token.lefts:
                if child.dep_ in ("nsubj", "nsubjpass"):
                    subj_token = child
                    break
                    
            # 1.5 NEW: Extract Subject Attributes (The "Worcestershire" Rule)
            if subj_token:
                # A. Find Origin/Location Prepositions (e.g., "from Worcestershire")
                for child in subj_token.children:
                    if child.dep_ == "prep":
                        prep_phrase = " ".join([t.text for t in child.subtree])
                        claims.append(f"{artist_name} is {prep_phrase}")
                        
                # B. Find Descriptive Identities (e.g., "The English post-punk band")
                # We grab the adjectives and determiners to the left of the subject
                left_desc = [t.text for t in subj_token.lefts if t.dep_ in ("amod", "compound", "det")]
                if left_desc:
                    descriptor = " ".join(left_desc + [subj_token.text])
                    # Ensure we don't just output the artist's name by itself
                    if artist_name.lower() not in descriptor.lower():
                        claims.append(f"{artist_name} is {descriptor}")
            
            # 2. Get the Direct Object
            dobj_str = ""
            for child in token.rights:
                if child.dep_ == "dobj":
                    dobj_str = " ".join([t.text for t in child.subtree])
                    break 
            
            # 3. Get the Verb Modifiers (The "OTHER" parts)
            modifiers = []
            for child in token.rights:
                # Ignore direct objects, punctuation, and coordinating conjunctions
                if child.dep_ not in ("dobj", "punct", "cc", "conj"):
                    phrase = " ".join([t.text for t in child.subtree])
                    modifiers.append(phrase)
            
            # 4. Construct the Base Action
            base_action = f"{artist_name} {verb_str} {dobj_str}".strip()
            
            # 5. Generate the Atomic Claims
            if not modifiers:
                claims.append(base_action)
            else:
                for mod in modifiers:
                    claim = f"{base_action} {mod}"
                    clean_claim = " ".join(claim.split())
                    claims.append(clean_claim)
                    
    # Remove any duplicate claims just to be clean
    unique_claims = list(dict.fromkeys(claims))
    return unique_claims if unique_claims else [summary]