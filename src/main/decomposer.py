import spacy

nlp = spacy.load("en_core_web_sm")

def extract_claims(summary, artist_name):
    """
    Decomposes a long-form text summary into verifiable, atomic factual claims.
    Uses spaCy's dependency parser to anchor claims around verbs and reconstruct 
    the surrounding grammatical structure (subjects, objects, modifiers).
    """ 
    doc = nlp(summary)
    claims = []
    
    # Iterate through every token in the parsed document to find action anchors
    for token in doc:
        # We look for Action Verbs (VERB) or Copular/Auxiliary Verbs (AUX, e.g., "is", "was")
        # This ensures we capture both active events and biographical states.
        if token.pos_ in ("VERB", "AUX"):
            
            # --- 1. IDENTIFY THE SUBJECT ---
            subj_token = None
            # Search the left syntactic children of the verb for the subject
            for child in token.lefts:
                # Look for nominal subjects (nsubj) or passive nominal subjects (nsubjpass)
                if child.dep_ in ("nsubj", "nsubjpass"):
                    subj_token = child
                    break
            
            # --- 2. EXTRACT FULL SUBJECT SPAN ---
            # Default to the artist's name to resolve loose pronouns contextually
            subj_text = artist_name
            # If a subject exists and is not a generic pronoun (he, she, they, it)
            if subj_token and subj_token.text.lower() not in ("he", "she", "they", "it"):
                # Use spaCy's document slicing to capture the entire compound noun phrase
                subj_text = subj_token.doc[subj_token.left_edge.i : subj_token.right_edge.i + 1].text

            # --- 3. EXTRACT BIOGRAPHICAL ATTRIBUTES ---
            # Extract additional identity facts tied to the subject noun
            if subj_token:
                for child in subj_token.children:
                    # Catch prepositional origins 
                    if child.dep_ == "prep":
                        prep_phrase = child.doc[child.left_edge.i : child.right_edge.i + 1].text
                        claims.append(f"{artist_name} is {prep_phrase}")
                        
                # Catch adjectives and determiners to form descriptive claims
                left_desc = [t.text for t in subj_token.lefts if t.dep_ in ("amod", "compound", "det")]
                if left_desc:
                    descriptor = child.doc[subj_token.left_edge.i : subj_token.i + 1].text
                    # Only append if the descriptor isn't just the artist's name repeated
                    if artist_name.lower() not in descriptor.lower():
                        claims.append(f"{artist_name} is {descriptor}")
            
            # --- 4. PRESERVE VERB TENSE & ASPECT ---
            # Collect helper verbs to maintain tenses like "is performing" or "has released"
            verb_phrase_tokens = []
            for left_child in token.lefts:
                if left_child.dep_ in ("aux", "auxpass"):
                    verb_phrase_tokens.append(left_child)
            verb_phrase_tokens.append(token) # Add the main verb last
            # Join the verb cluster into a single string
            verb_str = " ".join([t.text for t in verb_phrase_tokens])
            
            # --- 5. EXTRACT DIRECT OBJECT OR ATTRIBUTE ---
            dobj_str = ""
            # Search the right syntactic children for the receiver of the action
            for child in token.rights:
                # Look for direct objects (dobj), attributes (attr), or adjectival complements (acomp)
                if child.dep_ in ("dobj", "attr", "acomp"):
                    # Use span slicing to preserve natural text formatting and punctuation spacing
                    dobj_str = child.doc[child.left_edge.i : child.right_edge.i + 1].text
                    break 
            
            # --- 6. EXTRACT MODIFIERS (TIME, PLACE, MANNER) ---
            modifiers = []
            for child in token.rights:
                # Grab remaining phrases that are not core objects, punctuation, or conjunctions
                if child.dep_ not in ("dobj", "attr", "acomp", "punct", "cc", "conj"):
                    phrase = child.doc[child.left_edge.i : child.right_edge.i + 1].text
                    # Prevent nested subtree duplication by checking if the modifier is already in the object
                    if phrase and phrase not in dobj_str:
                        modifiers.append(phrase)
            
            # --- 7. CONSTRUCT THE BASE ACTION ---
            # Combine the core components into a singular baseline sentence
            base_action = f"{subj_text} {verb_str} {dobj_str}".strip()
            
            # Contextual Binding: Ensure the artist is explicitly named in the claim for NLI tracking.
            if subj_text.lower() not in artist_name.lower() and artist_name.lower() not in base_action.lower():
                base_action = f"{artist_name}, {base_action}"

            # --- 8. GENERATE ATOMIC CLAIMS ---
            if not modifiers:
                # If no modifiers exist, the base action is the only claim
                claims.append(base_action)
            else:
                # Multiply the base action by each modifier to create independent atomic facts
                for mod in modifiers:
                    claim = f"{base_action} {mod}"
                    # Normalize any double spaces created by the concatenation
                    clean_claim = " ".join(claim.split())
                    claims.append(clean_claim)
                    
    # --- 9. FINAL CLEANUP ---
    # Remove any exact duplicate claims using dictionary key conversion
    unique_claims = list(dict.fromkeys(claims))

    # Filter out claims that are too short to be verifiable facts (fragments under 5 words)
    MIN_WORDS = 5
    unique_claims = [c for c in unique_claims if len(c.split()) >= MIN_WORDS]
    
    # Fallback: if parsing yielded no valid structured claims, return the original summary
    return unique_claims if unique_claims else [summary]