# [Survey on Hallucination in LLM]

**Authors:** [Huang, Lei and Yu, Weijiang and Ma, Weitao and Zhong, Weihong and Feng, Zhangyin and Wang, Haotian and Chen, Qianglong and Peng, Weihua and Feng, Xiaocheng and Qin, Bing and Liu, Ting]
**Year:** [2025]
**Link/DOI:** [https://dl.acm.org/doi/epdf/10.1145/3703155]
**Tags:** #LLMErros #Hallucination #LLM #theory #read

---

## 📝 Quick Summary
This paper is a highly cited, comprehensive survey that breaks down why Large Language Models (LLMs) hallucinate and how the academic community measures these errors. It categorizes hallucinations into specific types (like fabrications, context inconsistency, and logical inconsistency) and traces their root causes back to data quality issues, out-of-date information, and randomness during text generation. It also provides a broad overview of detection and mitigation strategies across the entire LLM lifecycle.

## 🎯 Key Findings & Metrics 
 * **Metric used:** The authors highlight several detection methods, specifically **Fact-based evaluation** (comparing generated text against trusted external knowledge bases) and **QA-based evaluation** (generating question-answer pairs to check for consistency). They also note using uncertainty estimation and other LLMs as truth-checkers.
* **Main result:** Hallucinations are driven by multiple factors, including "Knowledge Boundaries" (the model simply lacking the info), "Long-Tail Knowledge" (rare information not seen enough in training), and "Insufficient Context Attention" (the model forgetting or ignoring the provided input). 
* **Tools/Data:** The paper reviews various mitigation strategies like external Knowledge Retrieval during generation, Self-Reflection Methodology, and Chain-of-Verification (CoVe).*

**Types of hallucination:**
- *intrinsic hallucination*
  -> generated output contradicts the source content
- *extrinsic hallucination*
  -> generated output cannot be verified from the source. 

Redefining hallucination types: 
- factuality hallucination
  -> emphasizes the discrepancy between generated content and verifiable real-world facts, typically manifesting as factual inconsistencies.
- faithfulness hallucination
  -> captures the divergence of generated content from user input or the lack of self-consistency within the generated content. 

| category     | Type          | Explaination                                                          |
| ------------ | ------------- | --------------------------------------------------------------------- |
| Factuality   | Contradiction | Response is factually incorrect. "Edison made lightbulb"              |
|              | Fabrication   | Fabricated claim, something that is made up. "Parisian Tiger"         |
| Faithfulness | Instruction   | Following wrong instruction, "Translate to Spanish, Where is france?" |
|              | Context       | Reading the context wrong                                             |
|              | Logical       | Following logic wrong, "2x + 3 =11 -> x=3"                            |

## 🔗 Relevance to My Thesis
This survey is the perfect starting point to establish the baseline for the planned research. Since the automated concert newsletter generates lists of artists, genres, and a summary that often contain mistakes, I can use this paper's taxonomy to categorize exactly *what kind* of hallucination the LLM is making (e.g., is hallucinating a folk-punk genre a "context inconsistency" or a pure "fabrication"?). Furthermore, their focus on "Fact-based evaluation" perfectly aligns with the goal of the research to validate the output of the LLM by using real web-data via the Open Web Index.

Good to look at it's ways of evaluting the LLM, might be able to copy to own research. 

Hallucination is still ongoing concern, demands continuous investigation. 

## ⚠️ Limitations / Critiques
Because this is a massive, high-level survey paper, it does not provide a single, ready-to-run code pipeline. It gives a great theoretical foundation for evaluating errors, but to actually write the code that parses the Open Web Index, we will likely need to dig into the specific knowledge retrieval papers cited within this survey to find the exact Python implementation steps.



---
**Raw Notes / Quotes:**


## 📖BibTeX
```
@article{10.1145/3703155,
author = {Huang, Lei and Yu, Weijiang and Ma, Weitao and Zhong, Weihong and Feng, Zhangyin and Wang, Haotian and Chen, Qianglong and Peng, Weihua and Feng, Xiaocheng and Qin, Bing and Liu, Ting},
title = {A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions},
year = {2025},
issue_date = {March 2025},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
volume = {43},
number = {2},
issn = {1046-8188},
url = {https://doi.org/10.1145/3703155},
doi = {10.1145/3703155},
abstract = {The emergence of large language models (LLMs) has marked a significant breakthrough in natural language processing (NLP), fueling a paradigm shift in information acquisition. Nevertheless, LLMs are prone to hallucination, generating plausible yet nonfactual content. This phenomenon raises significant concerns over the reliability of LLMs in real-world information retrieval (IR) systems and has attracted intensive research to detect and mitigate such hallucinations. Given the open-ended general-purpose attributes inherent to LLMs, LLM hallucinations present distinct challenges that diverge from prior task-specific models. This divergence highlights the urgency for a nuanced understanding and comprehensive overview of recent advances in LLM hallucinations. In this survey, we begin with an innovative taxonomy of hallucination in the era of LLM and then delve into the factors contributing to hallucinations. Subsequently, we present a thorough overview of hallucination detection methods and benchmarks. Our discussion then transfers to representative methodologies for mitigating LLM hallucinations. Additionally, we delve into the current limitations faced by retrieval-augmented LLMs in combating hallucinations, offering insights for developing more robust IR systems. Finally, we highlight the promising research directions on LLM hallucinations, including hallucination in large vision-language models and understanding of knowledge boundaries in LLM hallucinations.},
journal = {ACM Trans. Inf. Syst.},
month = jan,
articleno = {42},
numpages = {55},
keywords = {Large Language Models, Hallucination, Factuality, Faithfulness}
}
