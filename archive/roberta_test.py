import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# 1. Load the "Stubborn Librarian" (XLM-RoBERTa)
model_name = "joeddav/xlm-roberta-large-xnli"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def run_raw_test(category, premise, hypothesis):
    # Tokenize the pair
    tokens = tokenizer(premise, hypothesis, return_tensors="pt", truncation=True)
    
    # Run through the model (No gradients needed for inference)
    with torch.no_grad():
        output = model(**tokens)
    
    # Apply Softmax to get percentages
    # The labels for XNLI are: [0: Contradiction, 1: Neutral, 2: Entailment]
    probs = torch.nn.functional.softmax(output.logits, dim=-1)[0]
    
    print(f"\n--- {category} ---")
    print(f"PREMISE (NL): {premise}")
    print(f"HYPOTHESIS (EN): {hypothesis}")
    print(f"🔴 Contradiction: {probs[0].item()*100:.2f}%")
    print(f"🟡 Neutral:       {probs[1].item()*100:.2f}%")
    print(f"🟢 Entailment:    {probs[2].item()*100:.2f}%")

# --- THE 4 STRESS TESTS ---

# 1. THE LITERAL MATCH (Direct Logic)
run_raw_test("1. LITERAL MATCH", 
             "De band speelt een show in Doornroosje.", 
             "A musical group is performing at a venue.")

# 2. THE SEMANTIC GAP (Inference Problem)
run_raw_test("2. SEMANTIC GAP", 
             "Frank Boeijen komt naar Nijmegen met zijn nieuwe album.", 
             "Frank Boeijen is performing songs from his new album.")

# 3. THE "HELPFUL" HALLUCINATION (World Knowledge)
run_raw_test("3. EXTERNAL KNOWLEDGE", 
             "Heavy Lungs speelt in de Merleyn.", 
             "The British post-punk band Heavy Lungs performs in Nijmegen.")

# 4. THE DIRECT LIE (Fact-Check)
run_raw_test("4. DIRECT CONTRADICTION", 
             "Het concert is op 12 december.", 
             "The show takes place on December 20th.")