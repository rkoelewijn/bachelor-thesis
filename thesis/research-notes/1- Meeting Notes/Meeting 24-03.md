#meeting 
# 1. Research


# 2. Project Scope 

**First Steps:**
1. Pull the script from the Doornroosje website based on the artist snippet. 
2. Enter the ``summary`` from the newsletter into a script
3. Use XLM-RoBERTa and let it decide whether it is correct. 

### 📄 Thesis Scope: Cross-Lingual Hallucination Detection

**1. The Problem & Solution** The Cloudspeakers pipeline uses an LLM (DeepSeek) to scrape Dutch concert venues and generate English newsletters, but struggles with cross-lingual factual hallucinations. This thesis proposes a deterministic validation pipeline that replaces unreliable "LLM-as-a-judge" methods by combining **Open Web Index (OWI)** retrieval with **Cross-Lingual Natural Language Inference (XLM-RoBERTa)**.

**2. Research Question**

> _"To what extent can a deterministic validation pipeline—utilizing the Open Web Index and Cross-Lingual NLI (XLM-RoBERTa)—accurately detect factual hallucinations in LLM-generated English summaries of Dutch concert web pages?"_

**3. Strict Boundaries (Out of Scope)** To ensure this remains a tightly bound Bachelor's thesis, the following are strictly excluded:

- **No Open-World Fact-Checking:** We evaluate the LLM solely against the specific Dutch venue page retrieved from the OWI, not against external global truth (e.g., Wikipedia/Spotify).
    
- **No JSON Schema Evaluation:** We are evaluating the semantic reasoning of the English `summary` field only. We will not evaluate the LLM's ability to format strict entity lists like the `related_bands` array.
    
- **No Generative Judges:** The validation step relies entirely on deterministic classification math (NLI). Secondary generative LLMs will not be used for evaluation.