"""
Evaluation script for grammar correction model
Calculates various metrics to assess model performance
"""

import pandas as pd
import numpy as np
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import nltk
import re
from collections import Counter

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except (LookupError, OSError):
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except (LookupError, OSError):
    try:
        nltk.download('punkt_tab', quiet=True)
    except:
        pass  # punkt_tab is optional

class ModelEvaluator:
    def __init__(self):
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        self.smoothing = SmoothingFunction().method1
    
    def exact_match(self, predicted, ground_truth):
        """Check if predicted text exactly matches ground truth"""
        return predicted.strip().lower() == ground_truth.strip().lower()
    
    def character_level_accuracy(self, predicted, ground_truth):
        """Calculate character-level accuracy"""
        pred_chars = list(predicted.lower().strip())
        truth_chars = list(ground_truth.lower().strip())
        
        if len(truth_chars) == 0:
            return 1.0 if len(pred_chars) == 0 else 0.0
        
        matches = sum(1 for i, char in enumerate(pred_chars) if i < len(truth_chars) and char == truth_chars[i])
        return matches / max(len(pred_chars), len(truth_chars))
    
    def word_level_accuracy(self, predicted, ground_truth):
        """Calculate word-level accuracy"""
        pred_words = predicted.lower().strip().split()
        truth_words = ground_truth.lower().strip().split()
        
        if len(truth_words) == 0:
            return 1.0 if len(pred_words) == 0 else 0.0
        
        matches = sum(1 for word in pred_words if word in truth_words)
        return matches / max(len(pred_words), len(truth_words))
    
    def levenshtein_distance(self, s1, s2):
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def normalized_edit_distance(self, predicted, ground_truth):
        """Calculate normalized edit distance (1 - normalized Levenshtein)"""
        distance = self.levenshtein_distance(predicted.lower().strip(), ground_truth.lower().strip())
        max_len = max(len(predicted), len(ground_truth))
        if max_len == 0:
            return 1.0
        return 1.0 - (distance / max_len)
    
    def rouge_scores(self, predicted, ground_truth):
        """Calculate ROUGE scores"""
        scores = self.rouge_scorer.score(ground_truth, predicted)
        return {
            'rouge1': scores['rouge1'].fmeasure,
            'rouge2': scores['rouge2'].fmeasure,
            'rougeL': scores['rougeL'].fmeasure
        }
    
    def bleu_score(self, predicted, ground_truth):
        """Calculate BLEU score"""
        reference = [ground_truth.lower().split()]
        candidate = predicted.lower().split()
        
        try:
            score = sentence_bleu(reference, candidate, smoothing_function=self.smoothing)
            return score
        except:
            return 0.0
    
    def calculate_all_metrics(self, predicted, ground_truth):
        """Calculate all metrics for a single prediction"""
        metrics = {
            'exact_match': self.exact_match(predicted, ground_truth),
            'char_accuracy': self.character_level_accuracy(predicted, ground_truth),
            'word_accuracy': self.word_level_accuracy(predicted, ground_truth),
            'normalized_edit_distance': self.normalized_edit_distance(predicted, ground_truth),
            'bleu_score': self.bleu_score(predicted, ground_truth)
        }
        
        # Add ROUGE scores
        rouge_scores = self.rouge_scores(predicted, ground_truth)
        metrics.update(rouge_scores)
        
        return metrics
    
    def evaluate_dataset(self, df, model):
        """Evaluate model on entire dataset"""
        print("Evaluating model on test dataset...")
        results = []
        
        for idx, row in df.iterrows():
            input_text = row['Input_Text']
            ground_truth = row['Ground_Truth']
            category = row['Category']
            
            # Get model prediction
            try:
                predicted = model.correct(input_text)
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                predicted = input_text  # Fallback to original text
            
            # Calculate metrics
            metrics = self.calculate_all_metrics(predicted, ground_truth)
            
            # Store results
            result = {
                'Index': idx,
                'Category': category,
                'Input_Text': input_text,
                'Ground_Truth': ground_truth,
                'Predicted': predicted,
                **metrics
            }
            results.append(result)
            
            if (idx + 1) % 10 == 0:
                print(f"Processed {idx + 1}/{len(df)} test cases...")
        
        results_df = pd.DataFrame(results)
        return results_df
    
    def calculate_category_metrics(self, results_df):
        """Calculate aggregated metrics by category"""
        category_metrics = []
        
        for category in ['Typo', 'Grammar', 'Rephrasing']:
            cat_df = results_df[results_df['Category'] == category]
            
            if len(cat_df) == 0:
                continue
            
            metrics = {
                'Category': category,
                'Total_Test_Cases': len(cat_df),
                'Exact_Match_Rate': cat_df['exact_match'].mean(),
                'Avg_Char_Accuracy': cat_df['char_accuracy'].mean(),
                'Avg_Word_Accuracy': cat_df['word_accuracy'].mean(),
                'Avg_Normalized_Edit_Distance': cat_df['normalized_edit_distance'].mean(),
                'Avg_BLEU_Score': cat_df['bleu_score'].mean(),
                'Avg_ROUGE1': cat_df['rouge1'].mean(),
                'Avg_ROUGE2': cat_df['rouge2'].mean(),
                'Avg_ROUGEL': cat_df['rougeL'].mean(),
                'Exact_Matches': cat_df['exact_match'].sum(),
                'Improvement_Rate': (cat_df['normalized_edit_distance'] > 0.5).mean()
            }
            category_metrics.append(metrics)
        
        # Overall metrics
        overall_metrics = {
            'Category': 'Overall',
            'Total_Test_Cases': len(results_df),
            'Exact_Match_Rate': results_df['exact_match'].mean(),
            'Avg_Char_Accuracy': results_df['char_accuracy'].mean(),
            'Avg_Word_Accuracy': results_df['word_accuracy'].mean(),
            'Avg_Normalized_Edit_Distance': results_df['normalized_edit_distance'].mean(),
            'Avg_BLEU_Score': results_df['bleu_score'].mean(),
            'Avg_ROUGE1': results_df['rouge1'].mean(),
            'Avg_ROUGE2': results_df['rouge2'].mean(),
            'Avg_ROUGEL': results_df['rougeL'].mean(),
            'Exact_Matches': results_df['exact_match'].sum(),
            'Improvement_Rate': (results_df['normalized_edit_distance'] > 0.5).mean()
        }
        category_metrics.append(overall_metrics)
        
        return pd.DataFrame(category_metrics)
