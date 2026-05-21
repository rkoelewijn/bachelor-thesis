import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# --- CONFIGURATION ---
DEFAULT_MODEL = "joeddav/xlm-roberta-large-xnli"
ENT_THRESHOLD = 60.0
CON_THRESHOLD = 60.0

print(f"Loading weights from {DEFAULT_MODEL}...")
tokenizer = AutoTokenizer.from_pretrained(DEFAULT_MODEL)
model = AutoModelForSequenceClassification.from_pretrained(DEFAULT_MODEL)

def run_nli_check(premise, hypothesis):
    """Calculates probabilities for a single premise-hypothesis pair."""
    tokens = tokenizer(premise, hypothesis, return_tensors="pt", truncation=True)
    with torch.no_grad():
        output = model(**tokens)
    probs = torch.nn.functional.softmax(output.logits, dim=-1)[0]
    return {"ent": probs[2].item() * 100, "neu": probs[1].item() * 100, "con": probs[0].item() * 100}

def validate_claims(summary_claims, dutch_sentences):
    """Evaluates a list of claims against the source text."""
    results = [] 

    for claim in summary_claims:
        best_ent, best_con = 0, 0
        best_ent_evidence, best_con_evidence = "", ""

        for sentence in dutch_sentences: 
            res = run_nli_check(premise=sentence, hypothesis=claim)

            if res['ent'] > best_ent: 
                best_ent = res['ent']
                best_ent_evidence = sentence

            if res['con'] > best_con:
                best_con = res['con']
                best_con_evidence = sentence

        # NLI Threshold Logic
        if best_ent < ENT_THRESHOLD and best_con < CON_THRESHOLD:
            verdict = "UNSUPPORTED"
            evidence = None
        elif best_con > best_ent:
            verdict = "CONTRADICTION"
            evidence = best_con_evidence
        else:
            verdict = "ENTAILMENT"
            evidence = best_ent_evidence

        results.append({
            "claim": claim,
            "nli_verdict": verdict,
            "best_ent_score": best_ent,
            "best_con_score": best_con,
            "evidence_used": evidence
        })
        
    return results