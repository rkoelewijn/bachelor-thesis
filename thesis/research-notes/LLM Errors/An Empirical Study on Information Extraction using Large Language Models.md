
**Authors:** Jianhao Gao et al.
**Year:** 2024
**Link/DOI:** https://arxiv.org/abs/2305.14450
**Tags:** #read #information-extraction #llm-errors #web-scraping #taxonomy

---

## 📝 Quick Summary
This paper conducts a massive empirical evaluation of how well Large Language Models (like GPT-4) can perform Information Extraction (IE) tasks—which is the exact process of pulling structured data (like names, dates, and relationships) from unstructured text or raw website data. The authors discovered that while LLMs are great at general text generation, their performance drops significantly when forced to do strict, boundary-specific extraction. Most importantly for this thesis, they manually checked the LLM's outputs and created a formal taxonomy of the 7 specific ways LLMs fail at data extraction.

## 🎯 Key Findings & Metrics
* **The 7 Extraction Error Types:** They identified the exact failure modes: *Missing spans, Missing types, Unmentioned spans (Hallucinations), Unannotated spans, Incorrect span offsets, Undefined types, and Incorrect types.*
* **Main Result:** The paper found that **"Missing spans"** (failing to extract a piece of data that is clearly in the text) and **"Incorrect types"** (putting the right data in the wrong category) are the most dominant errors in LLM extraction pipelines.
* **Evaluation Problem:** They noted that traditional "exact string matching" is a poor way to evaluate LLMs because LLMs often generate conversational filler around the extracted data. They propose "soft-matching" strategies for evaluation.

## 🔗 Relevance to My Thesis
This paper is the missing link for my Error Analysis section. When my manual testing revealed that the newsletter LLM was pulling "past collaborators" and inserting them into the `related_artists` JSON field, I can now formally cite this paper and classify that error as an **"Incorrect Type"** extraction failure. 

Furthermore, because my pipeline uses the Open Web Index to retrieve the raw Dutch HTML, this paper proves why the newsletter LLM struggles: LLMs are prone to boundary errors when parsing complex, noisy text. This perfectly justifies why my Phase 2/3 validation pipeline breaks the text down into deterministic Knowledge Graph Triples (Subject-Predicate-Object) rather than trusting the LLM's initial extraction.

## ⚠️ Limitations / Critiques
The paper evaluates LLMs primarily on clean, standardized NLP datasets rather than raw, noisy HTML scraped from the live web. When an LLM reads actual DOM elements and HTML tags (like the Doornroosje website), the frequency of these extraction errors likely increases due to the "Parse-then-Interpret" structural noise of web code.

---
**Raw Notes / Quotes:**
* *"We summarize 7 types of errors on IE tasks by manually checking the responses... We find that 'Missing spans' and 'Unannotated spans' are the most dominant error types, accounting for more than 60% of errors in most cases."*
* *"This widespread presence of errors raises concerns about the quality of using LLMs for automated data annotation and extraction without secondary verification."*