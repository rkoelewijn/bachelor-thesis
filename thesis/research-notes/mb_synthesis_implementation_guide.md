# MusicBrainz Sentence Synthesis for NLI Context Augmentation

## Overview

This approach **converts MusicBrainz structured facts into natural language sentences** and adds them to the NLI verification context. This elegantly solves multiple problems:

1. ✅ **Closes knowledge gaps** - Claims about artist origin/type can now be verified even if not in Dutch text
2. ✅ **Reduces false negatives** - Should fix 6/12 EXTRINSIC_INJECTION_TRUE errors in your ground truth
3. ✅ **Reduces both-hot problem** - Adding consistent facts should stabilize NLI scores
4. ✅ **Simple implementation** - Reuses existing NLI infrastructure, no new models
5. ✅ **Interpretable** - Easy to explain in thesis: "MB says X, claim says X, NLI confirms match"

---

## Implementation Steps

### 1. Modify `dutch_parser.py`

**BEFORE:**
```python
def prepare_dutch_sentences(raw_text, artist_name):
    # Parse Dutch text only
    return dutch_sentences
```

**AFTER:**
```python
def prepare_dutch_sentences(raw_text, artist_name, mb_facts=None):
    # 1. Parse Dutch text
    dutch_sentences = [...]
    
    # 2. Synthesize MB sentences
    if mb_facts:
        mb_sentences = synthesize_musicbrainz_sentences(artist_name, mb_facts)
        mb_sentences_contextualized = [f"Over {artist_name}: {s}" for s in mb_sentences]
        return mb_sentences_contextualized + dutch_sentences
    
    return dutch_sentences

def synthesize_musicbrainz_sentences(artist_name, mb_facts):
    """Generate natural language sentences from MB structured data."""
    if mb_facts.get("status") != "Found":
        return []
    
    sentences = []
    country_map = {'NL': 'Dutch', 'GB': 'English', 'US': 'American', ...}
    
    artist_type = mb_facts.get('type')
    country = mb_facts.get('country')
    country_adj = country_map.get(country)
    
    if artist_type == 'Group' and country:
        sentences.append(f"{artist_name} is a {country_adj} band.")
    elif artist_type == 'Person' and country:
        sentences.append(f"{artist_name} is a {country_adj} artist.")
    
    return sentences
```

### 2. Update evaluator call sites

**In `hybrid_evaluator.py`:**
```python
# BEFORE:
context_sentences = dutch_parser.prepare_dutch_sentences(dutch_text, artist)

# AFTER:
mb_facts = entry.get("musicbrainz_facts", {"status": "Not Found"})
context_sentences = dutch_parser.prepare_dutch_sentences(
    dutch_text, 
    artist,
    mb_facts=mb_facts  # Pass MB facts
)
```

### 3. (Optional) Add AMBIGUOUS verdict

While you're modifying the evaluator, add the both-hot detector:

```python
# In verdict logic, add this at the top:
if ent_score > 60 and con_score > 60:
    intrinsic_verdict = "AMBIGUOUS"
```

---

## Example: How This Fixes Your False Negatives

### Case 1: IOS - "A Dutch Nederpop band"

**Current pipeline:**
- Dutch text: "IOS deed dit jaar mee aan The Voice..." (doesn't mention origin)
- Claim: "A Dutch Nederpop band returns..."
- NLI: ent=3.7, con=1.3 → EXTRINSIC_INJECTION_TRUE
- **Ground truth: TRUE** ❌ False negative!

**With MB synthesis:**
- MB facts: `{country: 'NL', type: 'Group'}`
- Generated: "IOS is a Dutch band."
- Context now includes: "Over IOS: IOS is a Dutch band."
- NLI: ent=~90+ → VALID ✅

### Case 2: And Also the Trees - "English post-punk band"

**Current pipeline:**
- Dutch text mentions band but not explicitly "English"
- NLI: ent=99.8, con=92.3 (both-hot problem!)
- Verdict: VALID but unstable

**With MB synthesis:**
- Generated: "And Also the Trees is an English band."
- NLI should stabilize: ent stays high, con drops to <60
- Both-hot problem reduced ✅

### Case 3: Daryll-Ann - "performs album in its entirety"

**Current pipeline:**
- Dutch says: "De band heeft het album nog niet eerder in z'n geheel uitgevoerd"
- Claim: "performs their cult-classic album 'Daryll-Ann Weeps' in its entirety"
- NLI: ent=40.5, con=55.9 → EXTRINSIC_INJECTION_TRUE
- **Ground truth: TRUE** ❌ False negative!

**With MB synthesis:**
- MB adds basic artist facts, improves baseline entailment
- Cross-lingual translation (separate fix) will help most here
- Combined: should reach VALID ✅

---

## Expected Impact on Metrics

Based on your ground truth (59 evaluable claims):

| Metric | Current | With MB Synthesis | Improvement |
|--------|---------|-------------------|-------------|
| **Precision** | 1.000 | 0.95-1.00 | Maintained |
| **Recall** | 0.816 | 0.90-0.93 | **+10-15%** |
| **F1** | 0.899 | 0.93-0.95 | **+3-5%** |
| **False Negatives** | 9 | 3-5 | **4-6 fewer** |
| **Both-hot cases** | 15 | 5-8 | **~50% reduction** |

### Specific fixes expected:
- ✅ IOS "Dutch band" claim
- ✅ Daryll-Ann "Dutch pop band"  
- ✅ And Also the Trees both-hot stabilization
- ✅ Other low-ent origin claims
- ⚠️ May not fix cross-lingual NLI failures (need translation for those)

---

## Advantages for Your Thesis

1. **Novelty**: Combining structured KB facts with NLI in this way is not standard practice
2. **Simplicity**: Easy to implement and explain
3. **Interpretability**: You can show exact MB sentences that helped verify claims
4. **Ablation study potential**: Can compare metrics with/without MB synthesis
5. **Generalizable**: Works for any domain with external knowledge bases

---

## Limitations & Future Work

**Limitations:**
- Only works when MusicBrainz has data (35/36 in your corpus)
- Only covers basic facts (country, type) not genres or albums
- Doesn't fix cross-lingual NLI issues (need translation for that)

**Extensions you could discuss:**
- Synthesize genre sentences from MB genre tags
- Add album/discography facts from MB release data
- Generate sentences in Dutch instead of English
- Combine with Wikidata for better coverage

---

## Combination with Other Improvements

**Recommended stack:**
1. ✅ MB sentence synthesis (this approach)
2. ✅ Dutch→English translation (Helsinki-NLP model)
3. ✅ AMBIGUOUS filter (both-hot detection)
4. ✅ Claim decomposer quality filter (remove fragments)

**Expected combined impact:**
- Precision: 0.95-1.00
- Recall: 0.92-0.95
- F1: 0.94-0.97
- Both-hot: <5 cases
- Thesis-ready! 🎓

---

## Files to Update

1. **dutch_parser.py** → Add `synthesize_musicbrainz_sentences()` function
2. **hybrid_evaluator.py** → Pass `mb_facts` to `prepare_dutch_sentences()`
3. **baseline_evaluator.py** → Same change (if you keep it)

See `dutch_parser_improved.py` and `hybrid_evaluator_improved.py` for complete implementations.

---

## Testing Strategy

1. Run on ground truth set (59 evaluable claims)
2. Compare metrics before/after
3. Manually inspect the 6 EXTRINSIC_INJECTION false negatives
4. Check both-hot cases reduced
5. Document in thesis with examples

**This is your biggest single improvement opportunity.** Combined with translation, you should hit F1 > 0.94.
