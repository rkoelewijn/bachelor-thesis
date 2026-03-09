
**Authors:** Hannah Sansford, Nicholas Richardson, Hermina Petric Maretic, Juba Nait Saada
**Year:** 2024
**Link/DOI:** https://arxiv.org/abs/2407.10793
**Tags:** #read #hallucination-evaluation #knowledge-graph #nli #fact-checking

---

## 📝 Quick Summary
This paper introduces GraphEval, a framework designed to detect "closed-domain" hallucinations (when an LLM contradicts the grounding text it was given). Instead of asking an LLM to evaluate a massive block of text, GraphEval breaks the LLM's output down into a Knowledge Graph (KG) consisting of specific, atomic "triples" (Subject-Predicate-Object). It then evaluates each individual triple against the source context using Natural Language Inference (NLI) models. This provides a highly explainable, fine-grained map of exactly *where* the model hallucinated.

## 🎯 Key Findings & Metrics
* **Core Mechanism:** Transforming the LLM's output into a structured graph of assertions before running the factual verification.
* **Main Result:** Using this Knowledge Graph approach in conjunction with state-of-the-art NLI models leads to a significant improvement in balanced accuracy on various hallucination benchmarks compared to using raw NLI models on unstructured text.
* **Efficiency:** It is computationally cheaper because it only requires a single LLM call to construct the KG, rather than repeatedly feeding massive context documents into an LLM-as-a-judge.
* **GraphCorrect:** They also introduced a follow-up method that uses the identified "faulty triples" to automatically correct the hallucinations.

## 🔗 Relevance to My Thesis
It proves scientifically that the absolute best way to catch factual errors is to combine **Graph Extraction** with **NLI Models**. 
By converting the automated newsletter's output (like "Jehnny Beth" -> "related to" -> "Gorillaz") into a graph structure and verifying those specific relationships against my Open Web Index Parquet files using an NLI model (like XLM-RoBERTa), my thesis is perfectly aligned with the 2024/2025 state-of-the-art in AI evaluation. It proves that my pipeline is more accurate, more explainable, and cheaper than standard prompt-based evaluations.

## ⚠️ Limitations / Critiques
GraphEval primarily focuses on *closed-domain* hallucination detection, meaning it relies on having the exact source context cleanly provided. In my thesis, the context is slightly messier because I am retrieving raw Dutch HTML from the Open Web Index. Furthermore, the framework relies on an initial LLM call to extract the Knowledge Graph triples, meaning the graph construction step itself could theoretically be vulnerable to extraction errors (which ties back to my earlier research on extraction misclassification).

---
**Raw Notes / Quotes:**
* *"Current metrics fall short in their ability to provide explainable decisions, systematically check all pieces of information in the response, and are often too computationally expensive..."*
* *"Our method identifies the specific triples in the KG that are prone to hallucinations and hence provides more insight into where in the response a hallucination has occurred..."*
* *"Using our approach in conjunction with state-of-the-art natural language inference (NLI) models leads to an improvement in balanced accuracy..."*