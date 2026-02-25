"""
LLM-based evaluator for grammar correction outputs
Scores predictions on a scale of 1-5 for each category
Supports both OpenAI and Azure OpenAI
"""

import os
import openai
from typing import List, Dict, Optional

class LLMEvaluator:
    def __init__(self, api_key: Optional[str] = None, api_endpoint: Optional[str] = None, 
                 api_version: Optional[str] = None, model: Optional[str] = None, use_azure: bool = False):
        """
        Initialize LLM evaluator
        
        Args:
            api_key: API key (OpenAI or Azure OpenAI)
            api_endpoint: Azure OpenAI endpoint URL (required for Azure)
            api_version: Azure OpenAI API version (default: "2024-02-15-preview")
            model: Model/deployment name to use
            use_azure: Whether to use Azure OpenAI (default: auto-detect from env vars)
        """
        # Check for Azure OpenAI credentials
        azure_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = api_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        azure_model = model or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        # Check for regular OpenAI credentials
        openai_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Determine which to use
        if use_azure or (azure_key and azure_endpoint):
            # Use Azure OpenAI
            if not azure_key:
                raise ValueError("Azure OpenAI API key required. Set AZURE_OPENAI_API_KEY in .env file.")
            if not azure_endpoint:
                raise ValueError("Azure OpenAI endpoint required. Set AZURE_OPENAI_ENDPOINT in .env file.")
            if not azure_model:
                raise ValueError("Azure OpenAI deployment name required. Set AZURE_OPENAI_DEPLOYMENT_NAME in .env file.")
            
            self.use_azure = True
            self.api_key = azure_key
            self.endpoint = azure_endpoint
            self.api_version = azure_version
            self.model = azure_model
            
            self.client = openai.AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
            print(f"Using Azure OpenAI with deployment: {self.model}")
        elif openai_key:
            # Use regular OpenAI
            self.use_azure = False
            self.api_key = openai_key
            self.model = model or "gpt-4o-mini"
            
            self.client = openai.OpenAI(api_key=self.api_key)
            print(f"Using OpenAI with model: {self.model}")
        else:
            raise ValueError(
                "API key required. Set either:\n"
                "  - AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_NAME (for Azure)\n"
                "  - OPENAI_API_KEY (for OpenAI)"
            )
    
    def evaluate_typo(self, input_text: str, ground_truth: str, predicted: str) -> Dict:
        """
        Evaluate typo correction on scale of 1-5
        
        Returns:
            Dict with 'score' (1-5) and 'explanation'
        """
        prompt = f"""You are evaluating a grammar correction model's performance on typo correction.

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
{{
    "score": <1-5>,
    "explanation": "<brief explanation>"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert grammar evaluator. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
                timeout=120.0,
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return {
                'score': int(result.get('score', 3)),
                'explanation': result.get('explanation', '')
            }
        except Exception as e:
            print(f"Error in LLM evaluation: {e}")
            return {'score': 3, 'explanation': f'Evaluation error: {str(e)}'}
    
    def evaluate_grammar(self, input_text: str, ground_truth: str, predicted: str) -> Dict:
        """Evaluate grammar correction on scale of 1-5"""
        prompt = f"""You are evaluating a grammar correction model's performance on grammatical error correction.

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
{{
    "score": <1-5>,
    "explanation": "<brief explanation>"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert grammar evaluator. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
                timeout=120.0,
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return {
                'score': int(result.get('score', 3)),
                'explanation': result.get('explanation', '')
            }
        except Exception as e:
            print(f"Error in LLM evaluation: {e}")
            return {'score': 3, 'explanation': f'Evaluation error: {str(e)}'}
    
    def evaluate_rephrasing(self, input_text: str, ground_truth: str, predicted: str, all_references: List[str] = None) -> Dict:
        """Evaluate rephrasing on scale of 1-5, considering multiple valid references"""
        references_text = ""
        if all_references:
            references_text = "\nValid reference corrections:\n" + "\n".join([f"- {ref}" for ref in all_references])
        
        prompt = f"""You are evaluating a grammar correction model's performance on text rephrasing for clarity and readability.

Original text: "{input_text}"
Primary corrected text (ground truth): "{ground_truth}"
{references_text}
Model's prediction: "{predicted}"

Rate the model's performance on a scale of 1-5:
1 = Poor rephrasing, unclear, or worse than original
2 = Below average, minimal improvement in clarity
3 = Acceptable rephrasing with some improvement
4 = Good rephrasing, clear and readable improvement
5 = Excellent rephrasing, significantly improved clarity and readability

Consider: clarity, readability, conciseness, natural flow, and whether it matches any valid reference.

Respond in JSON format:
{{
    "score": <1-5>,
    "explanation": "<brief explanation>"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert writing evaluator. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
                timeout=120.0,
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return {
                'score': int(result.get('score', 3)),
                'explanation': result.get('explanation', '')
            }
        except Exception as e:
            print(f"Error in LLM evaluation: {e}")
            return {'score': 3, 'explanation': f'Evaluation error: {str(e)}'}
    
    def evaluate_batch(self, results_df, category_col='Category', input_col='Input_Text',
                      truth_col='Ground_Truth', pred_col='Predicted', refs_col='All_References',
                      progress_callback=None):
        """
        Evaluate a batch of results

        progress_callback: optional callable(completed, total) called after each example.
        
        Returns:
            DataFrame with added columns: LLM_Score, LLM_Explanation
        """
        import pandas as pd
        llm_scores = []
        llm_explanations = []
        total = len(results_df)
        
        for idx, row in results_df.iterrows():
            category = row[category_col]
            input_text = row[input_col]
            ground_truth = row[truth_col]
            predicted = row[pred_col]
            
            # Get references if available
            all_references = None
            if refs_col in row and pd.notna(row[refs_col]):
                refs_str = str(row[refs_col])
                if '|' in refs_str:
                    all_references = refs_str.split('|')
                elif isinstance(row[refs_col], list):
                    all_references = row[refs_col]
            
            # Evaluate based on category
            if category == 'Typo':
                result = self.evaluate_typo(input_text, ground_truth, predicted)
            elif category == 'Grammar':
                result = self.evaluate_grammar(input_text, ground_truth, predicted)
            elif category == 'Rephrasing':
                result = self.evaluate_rephrasing(input_text, ground_truth, predicted, all_references)
            else:
                result = {'score': 3, 'explanation': 'Unknown category'}
            
            llm_scores.append(result['score'])
            llm_explanations.append(result['explanation'])
            
            completed = len(llm_scores)
            if progress_callback is not None:
                try:
                    progress_callback(completed, total)
                except Exception:
                    pass
            if completed % 10 == 0:
                print(f"LLM evaluated {completed}/{total} examples...")
        
        results_df = results_df.copy()
        results_df['LLM_Score'] = llm_scores
        results_df['LLM_Explanation'] = llm_explanations
        
        return results_df
