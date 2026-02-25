"""
Main evaluation script
Downloads model, generates test dataset, evaluates model, and creates Excel report
"""

import pandas as pd
from model_loader import GrammarCorrectionModel
from dataset_generator import DatasetGenerator
from evaluator import ModelEvaluator
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import os

def format_excel_report(filename):
    """Format the Excel report with styling"""
    wb = load_workbook(filename)
    
    # Define styles
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    category_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # Format header row
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = border
        
        # Format data rows
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            for cell in row:
                cell.border = border
                cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
                
                # Highlight category column
                if cell.column == 2:  # Category column
                    cell.fill = category_fill
                    cell.font = Font(bold=True)
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Freeze header row
        ws.freeze_panes = 'A2'
    
    wb.save(filename)
    print(f"Excel report formatted and saved to {filename}")

def main():
    print("=" * 80)
    print("Grammar Correction Model Evaluation")
    print("=" * 80)
    print()
    
    # Step 1: Generate test dataset
    print("Step 1: Generating synthetic test dataset...")
    print("-" * 80)
    generator = DatasetGenerator()
    test_df = generator.save_to_csv("test_dataset.csv")
    print()
    
    # Step 2: Load model
    print("Step 2: Loading grammar correction model...")
    print("-" * 80)
    model = GrammarCorrectionModel()
    print()
    
    # Step 3: Evaluate model
    print("Step 3: Evaluating model on test dataset...")
    print("-" * 80)
    evaluator = ModelEvaluator()
    results_df = evaluator.evaluate_dataset(test_df, model)
    print()
    
    # Step 4: Calculate aggregated metrics
    print("Step 4: Calculating aggregated metrics...")
    print("-" * 80)
    category_metrics_df = evaluator.calculate_category_metrics(results_df)
    print(category_metrics_df.to_string(index=False))
    print()
    
    # Step 5: Create Excel report
    print("Step 5: Creating Excel evaluation report...")
    print("-" * 80)
    
    excel_filename = "model_evaluation_report.xlsx"
    
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        # Sheet 1: Summary Metrics by Category
        category_metrics_df.to_excel(writer, sheet_name='Summary_Metrics', index=False)
        
        # Sheet 2: Detailed Results
        detailed_results = results_df[[
            'Index', 'Category', 'Input_Text', 'Ground_Truth', 'Predicted',
            'exact_match', 'char_accuracy', 'word_accuracy', 'normalized_edit_distance',
            'bleu_score', 'rouge1', 'rouge2', 'rougeL'
        ]].copy()
        
        # Rename columns for better readability
        detailed_results.columns = [
            'Index', 'Category', 'Input_Text', 'Ground_Truth', 'Predicted',
            'Exact_Match', 'Char_Accuracy', 'Word_Accuracy', 'Normalized_Edit_Distance',
            'BLEU_Score', 'ROUGE1', 'ROUGE2', 'ROUGEL'
        ]
        
        detailed_results.to_excel(writer, sheet_name='Detailed_Results', index=False)
        
        # Sheet 3: Best and Worst Cases
        best_cases = results_df.nlargest(20, 'normalized_edit_distance')[
            ['Category', 'Input_Text', 'Ground_Truth', 'Predicted', 'normalized_edit_distance']
        ].copy()
        best_cases.columns = ['Category', 'Input_Text', 'Ground_Truth', 'Predicted', 'Score']
        best_cases.to_excel(writer, sheet_name='Best_Cases', index=False)
        
        worst_cases = results_df.nsmallest(20, 'normalized_edit_distance')[
            ['Category', 'Input_Text', 'Ground_Truth', 'Predicted', 'normalized_edit_distance']
        ].copy()
        worst_cases.columns = ['Category', 'Input_Text', 'Ground_Truth', 'Predicted', 'Score']
        worst_cases.to_excel(writer, sheet_name='Worst_Cases', index=False)
        
        # Sheet 4: Category-wise Analysis
        category_analysis = []
        for category in ['Typo', 'Grammar', 'Rephrasing']:
            cat_df = results_df[results_df['Category'] == category]
            if len(cat_df) > 0:
                exact_matches = cat_df[cat_df['exact_match'] == True]
                category_analysis.append({
                    'Category': category,
                    'Total_Cases': len(cat_df),
                    'Exact_Matches': len(exact_matches),
                    'Exact_Match_Rate': len(exact_matches) / len(cat_df),
                    'Avg_BLEU': cat_df['bleu_score'].mean(),
                    'Avg_ROUGE1': cat_df['rouge1'].mean(),
                    'Avg_ROUGEL': cat_df['rougeL'].mean(),
                    'High_Quality_Corrections': len(cat_df[cat_df['normalized_edit_distance'] > 0.8])
                })
        
        category_analysis_df = pd.DataFrame(category_analysis)
        category_analysis_df.to_excel(writer, sheet_name='Category_Analysis', index=False)
    
    # Format the Excel file
    format_excel_report(excel_filename)
    
    print()
    print("=" * 80)
    print("Evaluation Complete!")
    print("=" * 80)
    print(f"\nFiles generated:")
    print(f"  1. test_dataset.csv - Test dataset with ground truth")
    print(f"  2. {excel_filename} - Comprehensive evaluation report")
    print()
    print("Summary:")
    print(f"  Total test cases: {len(results_df)}")
    print(f"  Exact matches: {results_df['exact_match'].sum()} ({results_df['exact_match'].mean()*100:.2f}%)")
    print(f"  Average BLEU score: {results_df['bleu_score'].mean():.4f}")
    print(f"  Average ROUGE-L score: {results_df['rougeL'].mean():.4f}")
    print(f"  Average normalized edit distance: {results_df['normalized_edit_distance'].mean():.4f}")

if __name__ == "__main__":
    main()
