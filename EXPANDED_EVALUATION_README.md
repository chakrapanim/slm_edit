# Expanded Grammar Correction Evaluation

This evaluation uses an expanded dataset similar to JFLEG with 100+ examples per category, longer sentences, and 4 reference corrections for rephrasing cases. It also includes LLM-based evaluation on a 1-5 scale.

## Files Created

1. **`dataset_generator_expanded.py`** - Generates expanded test dataset with:
   - 100 typo examples (including longer sentences)
   - 100 grammar examples (including longer sentences)
   - 100 rephrasing examples with 4 reference corrections each (like JFLEG)

2. **`llm_evaluator.py`** - LLM-based evaluator that scores predictions 1-5 for each category

3. **`main_evaluation_expanded.py`** - Main evaluation script that:
   - Generates expanded dataset
   - Evaluates model on all examples
   - Performs LLM evaluation (requires OpenAI API key)
   - Generates comprehensive Excel report

4. **`test_dataset_expanded.csv`** - Generated test dataset (300 examples total)

5. **`model_evaluation_expanded_report.xlsx`** - Comprehensive evaluation report

## Dataset Features

### Typos (100 examples)
- Common misspellings
- Word confusion (their/there, affect/effect, etc.)
- Missing/extra letters
- Transposed letters
- **Longer sentences** with multiple typos

### Grammar (100 examples)
- Subject-verb agreement
- Verb tense errors
- Article errors
- Preposition errors
- Punctuation issues
- Sentence fragments
- Run-on sentences
- **Longer sentences** with complex grammar errors

### Rephrasing (100 examples)
- Wordy phrases
- Passive to active voice
- Clarity improvements
- Sentence structure
- Redundancy removal
- **4 reference corrections** for each example (like JFLEG)
- **Longer sentences** requiring rephrasing

## LLM Evaluation

The LLM evaluator scores each prediction on a scale of 1-5:
- **1** = Completely incorrect, introduced new errors, or made it worse
- **2** = Mostly incorrect, missed the error or created significant errors
- **3** = Partially correct, fixed some issues but missed others
- **4** = Mostly correct, fixed the error but may have minor issues
- **5** = Perfect correction, exactly matches ground truth or is equally valid

### Setup for LLM Evaluation

1. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

2. The evaluation will automatically use LLM evaluation if the API key is available
3. If the API key is not set, the evaluation will continue without LLM scores

**Note**: LLM evaluation incurs API costs. For 300 examples, expect ~$0.50-2.00 depending on model used.

## Usage

### Generate Dataset Only
```bash
python dataset_generator_expanded.py
```

### Run Full Evaluation
```bash
python main_evaluation_expanded.py
```

This will:
1. Generate the expanded dataset (if not already exists)
2. Load the grammar correction model
3. Evaluate all 300 examples
4. Run LLM evaluation (if API key is set)
5. Generate Excel report with all metrics

## Excel Report Structure

The report (`model_evaluation_expanded_report.xlsx`) contains:

1. **Summary_Metrics** - Aggregated metrics by category
2. **Detailed_Results** - All test cases with predictions and metrics
3. **Best_Cases** - Top 20 best corrections
4. **Worst_Cases** - Bottom 20 worst corrections
5. **Category_Analysis** - Category-wise performance analysis
6. **LLM_Evaluation** - LLM scores and explanations for each example (if available)
7. **LLM_Summary** - Summary of LLM scores by category (if available)

## Evaluation Metrics

### Standard Metrics
- Exact Match Rate
- Character-level Accuracy
- Word-level Accuracy
- Normalized Edit Distance
- BLEU Score
- ROUGE Scores (ROUGE-1, ROUGE-2, ROUGE-L)

### LLM Metrics (if available)
- LLM Score (1-5 scale)
- LLM Explanation
- Average LLM Score by category
- Score distribution (counts for each score 1-5)
- Score 4+ rate (percentage of high-quality corrections)

## Multiple References for Rephrasing

Similar to JFLEG, rephrasing examples have 4 reference corrections. The evaluation:
- Calculates metrics against the primary reference (first one)
- Also calculates best and average metrics across all 4 references
- LLM evaluation considers all references when scoring

## Notes

- The evaluation may take 30-60 minutes for 300 examples
- LLM evaluation adds additional time (~10-20 minutes for 300 examples)
- Progress is printed every 20 examples
- The same output format as `model_evaluation_report.xlsx` is maintained
- New output file: `model_evaluation_expanded_report.xlsx`
