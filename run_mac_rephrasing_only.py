"""
Run Mac Foundation Model on rephrasing test cases only, using the rephrasing-specific prompt.
Compares results to previous Mac rephrasing metrics to check for improvement.
"""

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

try:
    from mac_foundation_model_loader import MacFoundationModel, mac_foundation_model_available
except Exception:
    MacFoundationModel = None
    mac_foundation_model_available = lambda: False

from evaluator import ModelEvaluator
from llm_evaluator import LLMEvaluator
from mac_evaluation_with_comparison import evaluate_with_multiple_references, TEST_DATASET_PATH

PREVIOUS_MAC_EXCEL = "mac_foundation_model_evaluation.xlsx"
REPHRASING_ONLY_OUTPUT_EXCEL = "mac_rephrasing_only_results.xlsx"


def load_previous_rephrasing_metrics():
    """Load Mac rephrasing metrics from last full run if available."""
    try:
        summary = pd.read_excel(PREVIOUS_MAC_EXCEL, sheet_name="Mac_Summary_Metrics", engine="openpyxl")
        row = summary[summary["Category"] == "Rephrasing"]
        if row.empty:
            return None
        r = row.iloc[0]
        out = {
            "Exact_Match_Rate": float(r.get("Exact_Match_Rate", 0)),
            "Avg_BLEU_Score": float(r.get("Avg_BLEU_Score", 0)),
            "Avg_ROUGEL": float(r.get("Avg_ROUGEL", 0)),
            "Exact_Matches": int(r.get("Exact_Matches", 0)),
        }
        try:
            comp = pd.read_excel(PREVIOUS_MAC_EXCEL, sheet_name="Comparison_Table", engine="openpyxl")
            cr = comp[comp["Category"] == "Rephrasing"]
            if not cr.empty and "Mac_Avg_LLM_Score" in comp.columns:
                out["Avg_LLM_Score"] = float(cr.iloc[0]["Mac_Avg_LLM_Score"])
        except Exception:
            pass
        return out
    except Exception:
        return None


def main():
    if not mac_foundation_model_available() or MacFoundationModel is None:
        print("Mac Foundation Model not available. Requires macOS 26+, Apple Intelligence, pip install apple-foundation-models")
        return

    print("=" * 70)
    print("Mac Foundation Model – Rephrasing-only evaluation (new prompt)")
    print("=" * 70)

    # Load test data and keep only Rephrasing
    print("\nStep 1: Loading rephrasing test cases...")
    test_df = pd.read_csv(TEST_DATASET_PATH)
    test_df["All_References"] = test_df["All_References"].apply(
        lambda x: x.split("|") if isinstance(x, str) and "|" in x else ([x] if pd.notna(x) and x else [])
    )
    rephrase_df = test_df[test_df["Category"] == "Rephrasing"].copy()
    n = len(rephrase_df)
    print(f"Loaded {n} rephrasing examples.")

    # Previous metrics for comparison
    previous = load_previous_rephrasing_metrics()
    if previous:
        print("\nPrevious Mac rephrasing metrics (single proofreading prompt):")
        print(f"  Exact match rate: {previous['Exact_Match_Rate']:.4f}  ({previous['Exact_Matches']}/100)")
        print(f"  Avg BLEU:         {previous['Avg_BLEU_Score']:.4f}")
        print(f"  Avg ROUGE-L:      {previous['Avg_ROUGEL']:.4f}")
        if "Avg_LLM_Score" in previous:
            print(f"  Avg LLM score:    {previous['Avg_LLM_Score']:.2f}")
    else:
        print("\n(No previous Mac rephrasing metrics found in Excel.)")

    # Run Mac model with category="Rephrasing" (rephrasing prompt)
    print("\nStep 2: Running Mac Foundation Model with rephrasing prompt...")
    model = MacFoundationModel()
    evaluator = ModelEvaluator()
    results = []
    for idx, row in rephrase_df.iterrows():
        input_text = row["Input_Text"]
        ground_truth = row["Ground_Truth"]
        all_references = row["All_References"]
        try:
            predicted = model.correct(input_text, category="Rephrasing")
        except Exception as e:
            print(f"  Error row {idx}: {e}")
            predicted = input_text
        primary_metrics = evaluator.calculate_all_metrics(predicted, ground_truth)
        multi_ref_metrics = {}
        if all_references:
            multi_ref_metrics = evaluate_with_multiple_references(
                predicted, all_references, evaluator, max_refs=4
            )
        results.append({
            "Index": idx,
            "Category": "Rephrasing",
            "Input_Text": input_text,
            "Ground_Truth": ground_truth,
            "Predicted": predicted,
            "All_References": "|".join(all_references) if all_references else "",
            **primary_metrics,
            **{k: v for k, v in multi_ref_metrics.items() if k.startswith("avg_") or k == "best_ref_score"},
        })
        if len(results) % 20 == 0:
            print(f"  Processed {len(results)}/{n}...")
    results_df = pd.DataFrame(results)
    if hasattr(model, "close"):
        model.close()

    # Category metrics for rephrasing
    cat_metrics = evaluator.calculate_category_metrics(results_df)
    rephrase_row = cat_metrics[cat_metrics["Category"] == "Rephrasing"].iloc[0]
    new_exact_rate = float(rephrase_row["Exact_Match_Rate"])
    new_bleu = float(rephrase_row["Avg_BLEU_Score"])
    new_rougel = float(rephrase_row["Avg_ROUGEL"])
    new_exact_count = int(rephrase_row["Exact_Matches"])

    # LLM evaluation on rephrasing results
    print("\nStep 3: Running LLM evaluation on rephrasing outputs...")
    try:
        llm_evaluator = LLMEvaluator()
        results_df = llm_evaluator.evaluate_batch(
            results_df,
            category_col="Category",
            input_col="Input_Text",
            truth_col="Ground_Truth",
            pred_col="Predicted",
            refs_col="All_References",
        )
        new_llm_avg = results_df["LLM_Score"].mean()
        new_high_quality = (results_df["LLM_Score"] >= 4).sum()
    except Exception as e:
        print(f"  LLM evaluation failed: {e}")
        new_llm_avg = None
        new_high_quality = None

    # Comparison
    print("\n" + "=" * 70)
    print("REPHRASING RESULTS (new rephrasing-specific prompt)")
    print("=" * 70)
    print(f"  Exact match rate: {new_exact_rate:.4f}  ({new_exact_count}/100)")
    print(f"  Avg BLEU:         {new_bleu:.4f}")
    print(f"  Avg ROUGE-L:      {new_rougel:.4f}")
    if new_llm_avg is not None:
        print(f"  Avg LLM score:    {new_llm_avg:.2f}")
        print(f"  High quality (≥4): {new_high_quality}")

    if previous:
        print("\n" + "-" * 70)
        print("COMPARISON (previous proofreading prompt vs new rephrasing prompt)")
        print("-" * 70)
        print(f"  Exact match:  {previous['Exact_Match_Rate']:.4f}  →  {new_exact_rate:.4f}  ({new_exact_rate - previous['Exact_Match_Rate']:+.4f})")
        print(f"  Avg BLEU:     {previous['Avg_BLEU_Score']:.4f}  →  {new_bleu:.4f}  ({new_bleu - previous['Avg_BLEU_Score']:+.4f})")
        print(f"  Avg ROUGE-L:  {previous['Avg_ROUGEL']:.4f}  →  {new_rougel:.4f}  ({new_rougel - previous['Avg_ROUGEL']:+.4f})")
        if new_llm_avg is not None and "Avg_LLM_Score" in previous:
            print(f"  Avg LLM:      {previous['Avg_LLM_Score']:.2f}  →  {new_llm_avg:.2f}  ({new_llm_avg - previous['Avg_LLM_Score']:+.2f})")
        improved = (
            new_exact_rate >= previous["Exact_Match_Rate"]
            and new_bleu >= previous["Avg_BLEU_Score"]
            and new_rougel >= previous["Avg_ROUGEL"]
        )
        print("\n  Improvement: Yes" if improved else "  Mixed or no improvement on exact match / BLEU / ROUGE-L.")

    # Save rephrasing-only results to Excel
    print("\nStep 4: Saving rephrasing results to Excel...")
    summary_sheet = cat_metrics[cat_metrics["Category"] == "Rephrasing"].copy()
    detailed_cols = [
        "Index", "Category", "Input_Text", "Ground_Truth", "Predicted",
        "exact_match", "char_accuracy", "word_accuracy", "normalized_edit_distance",
        "bleu_score", "rouge1", "rouge2", "rougeL", "All_References",
    ]
    if "LLM_Score" in results_df.columns:
        detailed_cols.extend(["LLM_Score", "LLM_Explanation"])
    detailed_df = results_df[[c for c in detailed_cols if c in results_df.columns]].copy()
    detailed_df.columns = [
        "Index", "Category", "Input_Text", "Ground_Truth", "Predicted",
        "Exact_Match", "Char_Accuracy", "Word_Accuracy", "Normalized_Edit_Distance",
        "BLEU_Score", "ROUGE1", "ROUGE2", "ROUGEL", "All_References",
    ] + (["LLM_Score", "LLM_Explanation"] if "LLM_Score" in results_df.columns else [])
    with pd.ExcelWriter(REPHRASING_ONLY_OUTPUT_EXCEL, engine="openpyxl") as writer:
        summary_sheet.to_excel(writer, sheet_name="Rephrasing_Summary", index=False)
        detailed_df.to_excel(writer, sheet_name="Rephrasing_Detailed", index=False)
    print(f"  Saved to {REPHRASING_ONLY_OUTPUT_EXCEL}")

    print("\nDone.")


if __name__ == "__main__":
    main()
