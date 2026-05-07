import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

DEFAULT_MODEL = "joeddav/xlm-roberta-large-xnli"
print(f"Loading weights from {DEFAULT_MODEL}...")
tokenizer = AutoTokenizer.from_pretrained(DEFAULT_MODEL)
model = AutoModelForSequenceClassification.from_pretrained(DEFAULT_MODEL)


def run_nli_check(premise, hypothesis):
    tokens = tokenizer(premise, hypothesis, return_tensors="pt", truncation=True)
    with torch.no_grad():
        output = model(**tokens)
    probs = torch.nn.functional.softmax(output.logits, dim=-1)[0]
    return {"ent": probs[2].item() * 100, "neu": probs[1].item() * 100, "con": probs[0].item() * 100}


def validate_claims(summary_claims, dutch_sentences, model_name=DEFAULT_MODEL):
    results = [] 

    for i, claim in enumerate(summary_claims, 1):
        # Track Entailment
        best_entail = 0
        best_ent_result = None
        best_ent_evidence = ""

        # Track Contradiction
        best_contradict = 0
        best_con_result = None
        best_con_evidence = ""

        for sentence in dutch_sentences: 
            result = run_nli_check(premise=sentence, hypothesis=claim)

            # Update highest entailment match
            if result['ent'] > best_entail: 
                best_entail = result['ent']
                best_ent_result = result
                best_ent_evidence = sentence

            # Update highest contradiction match
            if result['con'] > best_contradict:
                best_contradict = result['con']
                best_con_result = result
                best_con_evidence = sentence

        results.append({
            "claim": claim,
            "entailment_match": {
                "evidence": best_ent_evidence,
                "scores": best_ent_result
            },
            "contradiction_match": {
                "evidence": best_con_evidence,
                "scores": best_con_result
            }
        })
        
    return results