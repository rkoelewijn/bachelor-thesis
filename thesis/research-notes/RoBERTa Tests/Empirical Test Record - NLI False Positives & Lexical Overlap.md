
**Date:** March 2026
**Component Tested:** Phase 3 - XLM-RoBERTa (Cross-Lingual NLI)
**Tags:** #test-results #nli #xlm-roberta #false-positive #knowledge-graphs #micro-hallucinations

---

## 📝 Part 1: Baseline Accuracy (Standard Entailment & Contradiction)
Initial tests proved that the NLI model performs exceptionally well on standard data extraction tasks, effortlessly crossing the language barrier.
* **True Positive (Noor):** Correctly mapped "De Amsterdamse zangeres" to "Amsterdam-based singer" (**99.9% Entailment**).
* **True Negative (Bertolf):** Successfully caught a massive hallucination when the LLM changed a "Nederlandse band" playing "bluegrass" into an "American blues legend" (**94%+ Contradiction**).
* **Domain Vocabulary:** Handled highly specific musical phrasing seamlessly (e.g., mapping "Paarse zaal" to "Purple room" and matching genres like "pop noir").

## 📝 Part 2: The "Close Call" Sensitivity Tests
We stress-tested the model against micro-hallucinations (subtle errors) using a baseline text about the artist *Pip Blom*.
* **Test A (Wrong Date):** 14 mei vs. May 15.
* **Test B (Wrong Room):** kleine zaal vs. main hall.
* **Test C (Wrong Role):** hoofdact vs. support act.
* **Observation:** When errors are highly subtle, the model sometimes struggles to issue a pure Contradiction and instead spikes a high **Neutral** score. In the context of our deterministic pipeline, a high Neutral score is correctly flagged as a failure, as it indicates the LLM introduced unverified information not explicitly backed by the source text.

## 📝 Part 3: The False Positive & Lexical Overlap (The Daoud Test)
We evaluated the model's ability to detect an "Open-World Hallucination" (where the LLM uses external knowledge to inject factually correct real-world data that is *not* present in the source text).

**The Data:**
* **Dutch Source:** 'De Franse componist daoud speelt originele, dansbare and vrolijke jazz in een combinatie van hip-hop en house.'
* **LLM Summary:** 'The French-Moroccan trumpeter and composer daoud plays unconventional, danceable, and cheerful jazz that blends hip-hop grooves, neo-soul, and rock.'
* **The Result:** False Positive (**97.18% Entailment**).

**Scientific Diagnosis: Lexical Overlap Bias**
The model failed to flag the hallucinated facts ("Moroccan", "trumpeter", "neo-soul", "rock"). Because approximately 80% of the English sentence was a mathematically perfect semantic match to the Dutch source, the neural network's overall confidence score was artificially inflated. It evaluated the general "vibe" of the sentence rather than strictly checking the newly injected entities.

## 🏗️ Architectural Validation
This entire test suite empirically proves a core thesis argument: **Evaluating full, complex sentences via NLI is fundamentally flawed for strict factual validation.** This directly justifies the necessity of **Phase 2 (Graph Extraction)** in the validation pipeline. To prevent Lexical Overlap Bias, the pipeline *must* use OpenIE/SpaCy to chop the LLM's output into atomic Knowledge Graph Triples `(Subject, Predicate, Object)` before running the NLI math. 

**Example Fix for the Daoud Test:**
Instead of checking the whole sentence, the pipeline will test individual claims:
1. `(daoud, is, French-Moroccan)` -> NLI Verdict: Neutral/Contradiction
2. `(daoud, blends, rock)` -> NLI Verdict: Contradiction

By isolating the entities, the NLI model is forced to evaluate the exact facts without being blinded by surrounding semantic matches.


## Length Tests
As seen below, RoBERTa struggles when the texts arent the same length: 

```


Source (Dutch): 'VroegZat brengt het nachtleven terug naar de avond! Evenveel feest, maar eerder op de avond (19.30 tot 00.00 uur). Dus op een normale tijd naar bed, waardoor je de volgende dag gewoon fit bent. Win-win! Muzikaal gaat het heen en weer: van disco naar pop, van reggae naar rock en van happy naar hiphop, en die lekkere dansbare tunes die daartussen en daarbuiten vallen. DJ Rob de Nice en MC Rick Rossig gooien alles in de mix. Zorg dat je op tijd binnen bent, want hier kun je niet vroeg genoeg hard gaan!'    
LLM Summary (English): 'A Dutch event bringing nightlife to the early evening with a mix of danceable tunes across genres.'
----------------------------------------
🟢 Entailment (True):     18.57%
🟡 Neutral (Unverified):  81.04%
🔴 Contradiction (False): 0.39%
⚠️ VERDICT: INCONCLUSIVE / NEUTRAL (The LLM added unverified fluff)
----------------------------------------

Source (Dutch): 'VroegZat is een feestconcept waarbij je al vroeg op de avond (19:30–00:00) uitgaat, zodat je de volgende dag nog fit bent. Je krijgt een mix van dansbare muziekstijlen zoals disco, pop, reggae, rock en hiphop, verzorgd door DJ Rob de Nice en MC Rick Rossig. Kom op tijd om niets te missen en volop te feesten.'
LLM Summary (English): 'A Dutch event bringing nightlife to the early evening with a mix of danceable tunes across genres.'
----------------------------------------
🟢 Entailment (True):     99.39%
🟡 Neutral (Unverified):  0.47%
🔴 Contradiction (False): 0.14%
✅ VERDICT: FACTUALLY ACCURATE! (High Entailment)
----------------------------------------

Source (Dutch): 'VroegZat is een feest waar je al vroeg op de avond (19:30–00:00) kunt genieten van een mix van dansbare muziek, zodat je toch op tijd naar bed gaat en de volgende dag fit bent.'
LLM Summary (English): 'A Dutch event bringing nightlife to the early evening with a mix of danceable tunes across genres.'
----------------------------------------
🟢 Entailment (True):     20.14%
🟡 Neutral (Unverified):  79.79%
🔴 Contradiction (False): 0.07%
⚠️ VERDICT: INCONCLUSIVE / NEUTRAL (The LLM added unverified fluff)

```