import spacy

nlp = spacy.load("en_core_web_sm")

def extract_claims(summary, artist_name):
    doc = nlp(summary)
    claims = []
    
    for token in doc:
        if token.pos_ == "VERB":
            # Use the base form of the verb (lemma) for a cleaner relation
            verb_str = token.lemma_ 
            
            # 1. Identify Subject Structure
            subj_token = None
            for child in token.lefts:
                if child.dep_ in ("nsubj", "nsubjpass"):
                    subj_token = child
                    break
                             
            # 2. Extract Static Attributes (The Origin/Identity check)
            if subj_token:
                # A. Origin (e.g., "from the Netherlands")
                for child in subj_token.children:
                    if child.dep_ == "prep":
                        prep_phrase = " ".join([t.text for t in child.subtree])
                        claims.append(f"{artist_name} is {prep_phrase}")
                        
                # B. Identity (e.g., "The Dutch synthpunk band")
                left_desc = [t.text for t in subj_token.lefts if t.dep_ in ("amod", "compound", "det")]
                if left_desc:
                    descriptor = " ".join(left_desc + [subj_token.text])
                    if artist_name.lower() not in descriptor.lower():
                        claims.append(f"{artist_name} is {descriptor}")
                        
            # 3. Extract the Primary Action (Direct Object or Prepositional Object)
            dobj_str = ""
            for child in token.rights:
                # We specifically target the direct object or the prepositional target
                if child.dep_ in ("dobj", "prep", "attr", "pobj"):
                    dobj_str = " ".join([t.text for t in child.subtree])
                    break
                    
            # Build the atomic triple
            if dobj_str:
                claims.append(f"{artist_name} {verb_str} {dobj_str}")
                
    # Clean up duplicates
    unique_claims = list(dict.fromkeys(claims))
    
    # Fallback if spaCy fails to parse complex verbs
    return unique_claims if unique_claims else [summary]