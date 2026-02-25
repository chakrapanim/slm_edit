# Metrics Explanation with Examples

This document explains how BLEU, ROUGE-L, and LLM evaluation are calculated in this project.

## 1. BLEU Score Calculation

### What is BLEU?
BLEU (Bilingual Evaluation Understudy) measures the precision of n-grams (word sequences) between the predicted text and the reference text. It's commonly used in machine translation and text generation tasks.

### How it's calculated:
1. **N-gram Precision**: Counts how many n-grams (1-grams, 2-grams, 3-grams, 4-grams) from the prediction appear in the reference
2. **Brevity Penalty**: Penalizes predictions that are too short compared to the reference
3. **Geometric Mean**: Takes the geometric mean of n-gram precisions

### Formula:
```
BLEU = BP × (∏(i=1 to 4) precision_i)^(1/4)

Where:
- precision_i = number of i-grams in prediction that match reference / total i-grams in prediction
- BP (Brevity Penalty) = min(1, exp(1 - reference_length / prediction_length))
```

### Example:

**Input (with typo):** "I recieved your email yesterday."

**Ground Truth:** "I received your email yesterday."

**Model Prediction:** "I received your email yesterday."

Let's calculate BLEU:

**Step 1: Tokenize (split into words)**
- Reference: ["i", "received", "your", "email", "yesterday"]
- Prediction: ["i", "received", "your", "email", "yesterday"]

**Step 2: Calculate 1-gram precision**
- 1-grams in prediction: ["i", "received", "your", "email", "yesterday"] (5 total)
- 1-grams matching reference: ["i", "received", "your", "email", "yesterday"] (5 matches)
- 1-gram precision = 5/5 = 1.0

**Step 3: Calculate 2-gram precision**
- 2-grams in prediction: ["i received", "received your", "your email", "email yesterday"] (4 total)
- 2-grams matching reference: ["i received", "received your", "your email", "email yesterday"] (4 matches)
- 2-gram precision = 4/4 = 1.0

**Step 4: Calculate 3-gram and 4-gram precision**
- 3-grams: 3/3 = 1.0
- 4-grams: 2/2 = 1.0

**Step 5: Calculate Brevity Penalty**
- Reference length: 5 words
- Prediction length: 5 words
- BP = min(1, exp(1 - 5/5)) = min(1, exp(0)) = min(1, 1) = 1.0

**Step 6: Calculate BLEU**
- BLEU = 1.0 × (1.0 × 1.0 × 1.0 × 1.0)^(1/4) = 1.0 × 1.0 = **1.0**

**Example with imperfect match:**

**Ground Truth:** "I received your email yesterday."

**Model Prediction:** "I received the email yesterday."

**1-grams:**
- Prediction: ["i", "received", "the", "email", "yesterday"]
- Matches: ["i", "received", "email", "yesterday"] (4 out of 5)
- Precision = 4/5 = 0.8

**2-grams:**
- Prediction: ["i received", "received the", "the email", "email yesterday"]
- Matches: ["i received", "email yesterday"] (2 out of 4)
- Precision = 2/4 = 0.5

**3-grams:**
- Prediction: ["i received the", "received the email", "the email yesterday"]
- Matches: ["the email yesterday"] (1 out of 3)
- Precision = 1/3 ≈ 0.33

**BLEU ≈ 0.0** (very low due to low n-gram matches)

---

## 2. ROUGE-L Score Calculation

### What is ROUGE-L?
ROUGE-L (Recall-Oriented Understudy for Gisting Evaluation - Longest Common Subsequence) measures the longest common subsequence (LCS) between the prediction and reference. It focuses on **recall** - how much of the reference is captured in the prediction.

### How it's calculated:
1. **LCS (Longest Common Subsequence)**: Find the longest sequence of words that appear in both texts in the same order (but not necessarily consecutively)
2. **Recall**: LCS length / Reference length
3. **Precision**: LCS length / Prediction length
4. **F-measure**: Harmonic mean of precision and recall

### Formula:
```
ROUGE-L = F_measure = (2 × Precision × Recall) / (Precision + Recall)

Where:
- Precision = LCS_length / prediction_length
- Recall = LCS_length / reference_length
- LCS = Longest Common Subsequence
```

### Example:

**Ground Truth:** "I received your email yesterday."

**Model Prediction:** "I received the email yesterday."

**Step 1: Find LCS (Longest Common Subsequence)**
- Reference: ["i", "received", "your", "email", "yesterday"]
- Prediction: ["i", "received", "the", "email", "yesterday"]
- LCS: ["i", "received", "email", "yesterday"] (4 words)
  - These words appear in both texts in the same order

**Step 2: Calculate Recall**
- LCS length = 4
- Reference length = 5
- Recall = 4/5 = 0.8

**Step 3: Calculate Precision**
- LCS length = 4
- Prediction length = 5
- Precision = 4/5 = 0.8

**Step 4: Calculate ROUGE-L (F-measure)**
- ROUGE-L = (2 × 0.8 × 0.8) / (0.8 + 0.8) = 1.28 / 1.6 = **0.8**

**Another example:**

**Ground Truth:** "The weather is beautiful today."

**Model Prediction:** "Today the weather is beautiful."

**LCS:**
- Reference: ["the", "weather", "is", "beautiful", "today"]
- Prediction: ["today", "the", "weather", "is", "beautiful"]
- LCS: ["the", "weather", "is", "beautiful"] (4 words)
  - Note: "today" is in different positions, so it's not in the LCS

**Recall = 4/5 = 0.8**
**Precision = 4/5 = 0.8**
**ROUGE-L = 0.8**

**Key difference from BLEU:**
- BLEU focuses on **precision** (exact n-gram matches)
- ROUGE-L focuses on **recall** (capturing content from reference)
- ROUGE-L is more flexible with word order

---

## 3. LLM Evaluation Prompts

The LLM evaluator uses different prompts for each category. Here are the exact prompts used:

### 3.1 Typo Correction Prompt

```
You are evaluating a grammar correction model's performance on typo correction.

Original text with typo: "{input_text}"
Corrected text (ground truth): "{ground_truth}"
Model's prediction: "{predicted}"

Rate the model's performance on a scale of 1-5:
1 = Completely incorrect, introduced new errors, or made it worse
2 = Mostly incorrect, missed the typo or created significant errors
3 = Partially correct, fixed some issues but missed others or introduced minor errors
4 = Mostly correct, fixed the typo but may have minor issues
5 = Perfect correction, exactly matches the ground truth or is equally valid

Respond in JSON format:
{
    "score": <1-5>,
    "explanation": "<brief explanation>"
}
```

**Example:**
- Input: "I recieved your email."
- Ground Truth: "I received your email."
- Prediction: "I received your email."
- Expected Score: 5 (perfect match)

### 3.2 Grammar Correction Prompt

```
You are evaluating a grammar correction model's performance on grammatical error correction.

Original text with grammar error: "{input_text}"
Corrected text (ground truth): "{ground_truth}"
Model's prediction: "{predicted}"

Rate the model's performance on a scale of 1-5:
1 = Completely incorrect, introduced new errors, or made it worse
2 = Mostly incorrect, missed the grammar error or created significant errors
3 = Partially correct, fixed some issues but missed others or introduced minor errors
4 = Mostly correct, fixed the grammar error but may have minor issues
5 = Perfect correction, exactly matches the ground truth or is equally valid

Respond in JSON format:
{
    "score": <1-5>,
    "explanation": "<brief explanation>"
}
```

**Example:**
- Input: "The team are working hard."
- Ground Truth: "The team is working hard."
- Prediction: "The team is working hard."
- Expected Score: 5 (perfect correction)

### 3.3 Rephrasing Prompt (with Multiple References)

```
You are evaluating a grammar correction model's performance on text rephrasing for clarity and readability.

Original text: "{input_text}"
Primary corrected text (ground truth): "{ground_truth}"
Valid reference corrections:
- {reference_1}
- {reference_2}
- {reference_3}
- {reference_4}
Model's prediction: "{predicted}"

Rate the model's performance on a scale of 1-5:
1 = Poor rephrasing, unclear, or worse than original
2 = Below average, minimal improvement in clarity
3 = Acceptable rephrasing with some improvement
4 = Good rephrasing, clear and readable improvement
5 = Excellent rephrasing, significantly improved clarity and readability

Consider: clarity, readability, conciseness, natural flow, and whether it matches any valid reference.

Respond in JSON format:
{
    "score": <1-5>,
    "explanation": "<brief explanation>"
}
```

**Example:**
- Input: "Due to the fact that it was raining, we stayed home."
- Ground Truth: "Because it was raining, we stayed home."
- Valid References:
  - "Because it was raining, we stayed home."
  - "Since it was raining, we stayed home."
  - "We stayed home because it was raining."
  - "It was raining, so we stayed home."
- Prediction: "Because it was raining, we stayed home."
- Expected Score: 5 (matches a valid reference, excellent rephrasing)

### LLM Evaluation Settings

- **Model**: Azure OpenAI (gpt-5 deployment)
- **Temperature**: 0.3 (low for consistent scoring)
- **Response Format**: JSON (structured output)
- **System Message**: "You are an expert grammar evaluator. Respond only with valid JSON."

### Scoring Criteria Summary

| Score | Meaning |
|-------|---------|
| 5 | Perfect - exactly matches ground truth or equally valid |
| 4 | Mostly correct - fixed the issue but may have minor problems |
| 3 | Partially correct - fixed some issues but missed others |
| 2 | Mostly incorrect - missed the error or created significant errors |
| 1 | Completely incorrect - made it worse or introduced new errors |

---

## Summary

- **BLEU**: Measures precision of n-gram matches (1-4 grams). Higher when prediction closely matches reference word-for-word.
- **ROUGE-L**: Measures recall via longest common subsequence. Higher when prediction captures most content from reference, even with different word order.
- **LLM Score**: Human-like evaluation on 1-5 scale considering context, clarity, and correctness. More nuanced than automated metrics.

These metrics complement each other:
- BLEU catches exact matches
- ROUGE-L catches semantic similarity
- LLM score provides human-like judgment
