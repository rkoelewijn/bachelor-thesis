# [Failure Types in LLM Systems]

**Authors:** [Vaishali Vinay]
**Year:** [2025]
**Link/DOI:** [https://arxiv.org/abs/2511.19933]
**Tags:** #LLM #LLMErros #Hallucination #Factual_Inaccurate #Overconfidence #theory #read

---

## 📝 Quick Summary
This paper set up a taxonomy of the different types of LLM failures, divided into *Reasoning Failure*, *Input and Context Failure* and *System and Operational Failure*. 

Unlike papers that just look at why an LLM hallucinates text, this paper frames LLM reliability as a system-engineering problem. It looks at what happens when LLMs are integrated into actual production workflows and automated pipelines. The author presents a system-level taxonomy of 15 hidden failure modes that occur in real-world LLM applications, addressing the gap between standard academic benchmarks and actual production stability.

## 🎯 Key Findings & Metrics
* **Metric used:** Rather than a mathematical formula, the paper proposes a qualitative **system-level taxonomy** to evaluate AI robustness, focusing on observability limitations, workflow integration, and update-induced regressions. 
* **Main result:** The paper identifies 15 unique failure modes that differ from traditional machine learning. Key failures include "multi-step reasoning drift," "latent inconsistency," "context-boundary degradation," and "incorrect tool invocation."
* **Tools/Data:** The paper outlines high-level design principles for building reliable, maintainable, and cost-aware LLM systems rather than testing a specific dataset.

**Types of Errors:**
- Reasoning: 
	- **Hallucinations & Factual inaccuracies (Relevant)**
	  **-> Presents non-factual but fluent utterance.**
	  -->> More on Hallucinations in [[A Survey on Hallucination in Large Language Models - Principles, Taxonomy, Challenges, and Open Questions]]
	- Logical inconsistency & Self contradiction 
	  -> Repeating itself or contradicts earlier turns. 
	  -> Lack of global memory consistency 
	- Multi-step planning collapse / looping 
	  -> These models can stall, skip steps, or repeat work indefinitely
	- **Overconfidence & Calibration failure** (Could relevant)
	  -> Fails with overconfidence due to not being able to express uncertainty
	- Failure to follow task constraints
	  -> when high-level instructions conflict with context or system feedback
	

## 🔗 Relevance to My Thesis
Hallucinations & Factual Inaccuracies will occur most in the LLM that is set up in the project, so more research into that will be needed. 

This paper is relevant to the engineering and automation side of the research project. The automated concert newsletter is essentially a multi-step AI pipeline: it uses an LLM to scrape different concert venues, extract data, and compile a list. Because the goal of the research is to validate the output of the LLM by using real web-data and explore how to adapt this onto other AI Agents, understanding failures like "incorrect tool invocation" or "context-boundary degradation" is crucial. When building the automated script to query the Open Web Index, this paper's design principles will help ensure the pipeline itself doesn't silently crash when the LLM makes mistakes.

The paper notes that there exists an evaluation gap in LLM Systems: 
"*Most of the assessments of large language models (LLMs) are still anchored to static benchmarks for their knowledge recall or task performance rather than model stability and operational reliability.*"


## ⚠️ Limitations / Critiques
This is an analytical and theoretical framework rather than an empirical coding tutorial. It provides a great checklist of "what could go wrong" in an AI system, but it does not provide the exact Python code or mathematical formulas needed to automatically catch these errors in our specific concert dataset. We will still have to define the exact programmatic rules to test for these failures ourselves.

---
**Raw Notes / Quotes:**


## 📖Bibtex
```
@misc{vinay2025failuremodesllmsystems,
      title={Failure Modes in LLM Systems: A System-Level Taxonomy for Reliable AI Applications}, 
      author={Vaishali Vinay},
      year={2025},
      eprint={2511.19933},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2511.19933}, 
}
```