# Comprehensive Thesis Review: Koelewijn (2026)

---

## CRITERION 1: Rigorous Spell & Grammar Check
- **Action:** Compile the document with all labels correctly defined. Audit every `\ref{}` and `\label{}` pair and ensure they resolve.

**1.20**
- **Location:** Chapter 5.2.1 caption for Figure 5.1: *"The model's predictive performance plateaus at exactly T = 0.65"*
- **Issue:** The caption states T = 0.65 but all surrounding analysis uses T = 70.0 (on a 0–100 scale). These are inconsistent representations of the same threshold.
- **Action:** Standardize to one scale throughout. If the threshold is expressed as a percentage (0–100), the caption should read T = 65 or T = 70; if expressed as a probability (0–1), it should read T = 0.70 everywhere.

---

## CRITERION 2: Captions & Labeling Check

**2.3**
- **Location:** Chapter 5.3.1: *"Figure 5.4 ."* (appears as a standalone line with no caption)
- **Issue:** Same as 2.1 — the label "Figure 5.4" in this location is a duplicate label for what appears to be the sentence-level confusion matrix. Either two figures share the same number or one label is wrong.
- **Action:** Audit all figure labels. Assign unique, sequential labels and ensure each has a substantive caption.


---

## CRITERION 3: Thesis Completeness & Consistency


**3.6**
- **Location:** Chapter 2 — missing Related Work / Literature Review section
- **Issue:** The thesis jumps from Preliminaries (conceptual definitions) directly to the pipeline description with no dedicated discussion of prior art. Key related works (SummaC, SAFE, FELM) are introduced briefly in-context but never systematically reviewed.
- **Action:** Either rename Chapter 2 to "Background and Related Work" and add a subsection (§2.5) reviewing SummaC, SAFE, FELM, and FActScore comparatively, or add a dedicated Chapter 2.5 titled "Related Work" before Chapter 3.


**3.10**
- **Location:** Chapter 3.3 — footnote 1 (the Luna Maki URL)
- **Issue:** The footnote URL `https://www.nieuwsplein33.nl/...` is a local/niche news source with no guarantee of long-term availability. It is the sole source for a factual claim used to validate the real-world relevance of the pipeline.
- **Action:** Archive the page via the Wayback Machine and cite the archived URL, or supplement with a second source confirming Luna Maki's origin.

---

## CRITERION 4: Structural Flow & Argumentation





**4.5**
- **Location:** Chapter 2 (Preliminaries) — Section 2.4 on Binary Classification Metrics
- **Issue:** Section 2.4 introduces standard classification metrics (accuracy, precision, recall, F1, FPR) in the Preliminaries, yet XLM-RoBERTa and the NLI model — which are more central to the thesis — receive less definitional space. The metrics section reads as filler for readers of a CS thesis.
- **Action:** Either shorten §2.4 to a single paragraph with equations and a reference to a textbook, or reframe it explicitly as needed groundwork for §4.7.4 evaluation choices.


---

## CRITERION 5: AI-Generated Text Detection


**5.6**
- **Location:** Chapter 6, opening sentence: *"Following the findings presented in Chapter 5, this chapter provides a deeper interpretation of the pipeline's behavior."*
- **Issue:** "Following the findings presented in X, this chapter provides a deeper interpretation" is a textbook AI-generated chapter opener used across countless AI-written theses.
- **Action:** Replace with something that immediately signals the specific analytical contribution: "The results in Chapter 5 raise two questions that metrics alone cannot answer: why does the baseline misclassify 12 supported claims as intrinsic, and why do atomic-level Knowledge Graph corrections fail to propagate upward? This chapter addresses both."

**5.7**
- **Location:** Chapter 7 (Conclusions), opening sentence: *"This research aimed to detect hallucinations in LLM-summaries of local music venues, using a hybrid cross-lingual NLI and knowledge graph architecture."*
- **Issue:** This restates the title almost verbatim. AI-generated conclusions routinely open by restating the title or abstract. A strong conclusion should open by synthesizing the most important finding.
- **Action:** Replace with: "The central finding of this thesis is that a fully deterministic hallucination detection pipeline — combining cross-lingual NLI with a structured knowledge graph — can achieve a perfect error detection rate (1.0000) on niche, localized event summaries, validating the approach as a sound alternative to circular LLM-as-a-judge evaluation."