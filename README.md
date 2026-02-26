# Grammar Correction Model Evaluation

This project evaluates the `Vennify/t5-base-grammar-correction` model for proofreading capabilities including typos, grammatical errors, and rephrasing improvements.

## Files

**Core evaluation**
- `requirements.txt` - Python dependencies (including Streamlit)
- `model_loader.py` - T5 grammar correction model (Vennify/t5-base-grammar-correction)
- `mac_foundation_model_loader.py` - Mac Foundation Model (Apple Intelligence) for Typos / Grammar / Rephrase
- `dataset_generator.py` / `dataset_generator_expanded.py` - Synthetic test datasets (typos, grammar, rephrasing)
- `evaluator.py` - Metrics (BLEU, ROUGE, edit distance, exact match, etc.)
- `main_evaluation.py` / `main_evaluation_expanded.py` - Full evaluation pipeline (T5)
- `test_dataset.csv` / `test_dataset_expanded.csv` - Test data with ground truth and 4 refs for rephrasing

**Mac vs T5 comparison**
- `mac_evaluation_with_comparison.py` - Run Mac on 300 examples, LLM eval, compare with T5 → `mac_foundation_model_evaluation.xlsx`
- `run_mac_rephrasing_only.py` - Mac rephrasing-only (new prompt) → `mac_rephrasing_only_results.xlsx`
- `build_final_comparison.py` - Build T5 vs Mac (Typos/Grammar from full run, Rephrasing from new prompt) → `final_comparison.xlsx`

**Paragraph rephrasing (longer text)**
- `dataset_paragraph_rephrasing.py` - 50 paragraph examples (up to 512 tokens, 4 refs) → `paragraph_rephrasing_dataset.csv`
- `evaluate_paragraph_rephrasing.py` - T5 + Mac + LLM on paragraphs → `paragraph_rephrasing_evaluation.xlsx`

**App & utilities**
- `app_streamlit.py` - Streamlit UI to test Mac Foundation Model (Typos / Grammar / Rephrase)
- `llm_evaluator.py` - LLM-based scoring (1–5) via Azure OpenAI / OpenAI
- `push_to_github.sh` - Push to GitHub (set `GITHUB_USER` and `GITHUB_TOKEN`)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app to test the Mac Foundation Model (Typos / Grammar / Rephrase) with your own text:
```bash
streamlit run app_streamlit.py
```
Requires macOS 26+ and Apple Intelligence. Use the full command `streamlit run app_streamlit.py` (not `run app_streamlit.py`).

3. Run the T5 evaluation:
```bash
python main_evaluation.py
```

## Evaluation Metrics

The evaluation includes:
- **Exact Match Rate**: Percentage of predictions that exactly match ground truth
- **Character-level Accuracy**: Character-by-character accuracy
- **Word-level Accuracy**: Word-by-word accuracy
- **Normalized Edit Distance**: Similarity based on edit distance
- **BLEU Score**: Translation quality metric
- **ROUGE Scores**: Recall-oriented metrics (ROUGE-1, ROUGE-2, ROUGE-L)

## Test Dataset

The synthetic test dataset includes:
- **Typos**: 50 test cases with common misspellings and typos
- **Grammar**: 50 test cases with grammatical errors
- **Rephrasing**: 50 test cases requiring clarity and readability improvements

Total: 150 test cases with ground truth labels.

## Output

The evaluation generates an Excel report with multiple sheets:
1. **Summary_Metrics**: Aggregated metrics by category
2. **Detailed_Results**: All test cases with predictions and metrics
3. **Best_Cases**: Top 20 best corrections
4. **Worst_Cases**: Bottom 20 worst corrections
5. **Category_Analysis**: Category-wise performance analysis

## JFLEG Dataset Evaluation

To evaluate on the JFLEG dataset:

```bash
python jfleg_evaluation.py
```

This will:
- Load the JFLEG test set (748 examples)
- Evaluate the model on all examples
- Save progress periodically (checkpoint every 10 examples)
- Generate `jfleg_evaluation_report.xlsx` when complete

**Note**: The evaluation takes 30-60 minutes. Progress is saved automatically, so you can safely interrupt and resume.

### Monitoring Progress

Use the monitoring script to check evaluation progress:

```bash
# Single check
python monitor_jfleg.py

# Continuous monitoring (updates every 30 seconds)
python monitor_jfleg.py --watch 30
```

The monitor shows:
- Process status (running/completed)
- Progress percentage and progress bar
- Current metrics from completed examples
- Estimated time remaining
- Output file status

## Mac Foundation Model Evaluation (macOS Tahoe)

On **macOS 26+ (Tahoe)** with **Apple Intelligence** enabled, you can evaluate the on-device Mac Foundation Model on the same expanded test dataset and compare it with T5-base-grammar-correction.

### Requirements

- macOS 26 (Tahoe) or later
- Apple Intelligence enabled in System Settings
- T5 evaluation already run (so `model_evaluation_expanded_report.xlsx` exists for comparison)
- `.env` configured for LLM evaluation (Azure OpenAI or OpenAI)

### Setup

```bash
pip install apple-foundation-models
```

### Run

```bash
python mac_evaluation_with_comparison.py
```

This will:

1. Load the same expanded test dataset (300 examples: Typos, Grammar, Rephrasing).
2. Run the Mac Foundation Model on each example (proofreading prompt).
3. Compute the same metrics (BLEU, ROUGE-L, normalized edit distance, exact match, high-quality count).
4. Run LLM evaluation (1–5 scale) on Mac outputs.
5. Load T5 results from `model_evaluation_expanded_report.xlsx`.
6. Write **`mac_foundation_model_evaluation.xlsx`** with:

**Progress while running:** The script updates **`mac_eval_progress.json`** as it runs. To see how many of the 300 evaluations are done:
```bash
cat mac_eval_progress.json
```
Example: `"phase": "mac_model", "completed": 150, "total": 300, "message": "150/300"`. Phases: `mac_model` (Mac Foundation Model), then `llm_eval` (LLM scoring). The file is removed when the run finishes.
   - **Mac_Summary_Metrics** – Mac model metrics by category
   - **Mac_Detailed_Results** – All 300 examples with Mac predictions and metrics
   - **Mac_LLM_Evaluation** – LLM scores and explanations for Mac outputs
   - **Mac_LLM_Summary** – LLM score summary by category
   - **Comparison_Table** – Side-by-side: T5 vs Mac (Exact Match, BLEU, ROUGE-L, LLM score, High Quality count) per category
   - **Comparison_Detailed** – Per-metric comparison rows (T5 vs Mac) for each category

Rephrasing uses a dedicated prompt; for rephrase-only evaluation and the final comparison file, see below.

### Rephrasing-only and final comparison

After the full Mac run, you can re-run rephrasing with a rephrasing-specific prompt and build the final comparison:

```bash
python run_mac_rephrasing_only.py    # 100 rephrasing examples, new prompt → mac_rephrasing_only_results.xlsx
python build_final_comparison.py     # T5 vs Mac (Typos/Grammar from full run, Rephrasing from rephrase-only) → final_comparison.xlsx
```

`final_comparison.xlsx` contains **Comparison_Table** and **LLM_Evaluation_Comparison** (avg LLM score, 4+ count, 5 count for T5 vs Mac).

### Paragraph rephrasing (50 longer examples)

For paragraph-length text (up to 512 tokens) with 4 reference rephrasings:

```bash
python dataset_paragraph_rephrasing.py   # optional: (re)generate paragraph_rephrasing_dataset.csv
python evaluate_paragraph_rephrasing.py  # T5 + Mac + LLM on 50 paragraphs → paragraph_rephrasing_evaluation.xlsx
```

Output Excel: Input_Dataset, T5_Results, Mac_Results, LLM_Comparison (per example), LLM_Summary (T5 vs Mac).
