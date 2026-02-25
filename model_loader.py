"""
Model loader for Vennify/t5-base-grammar-correction
Downloads and loads the model for grammar correction tasks
"""

from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

class GrammarCorrectionModel:
    def __init__(self, model_name="Vennify/t5-base-grammar-correction"):
        """
        Initialize the grammar correction model
        
        Args:
            model_name: HuggingFace model identifier
        """
        print(f"Loading model: {model_name}")
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Load tokenizer and model
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        print("Model loaded successfully!")
    
    def correct(self, text, max_length=512, num_beams=4):
        """
        Correct grammar, typos, and improve text
        
        Args:
            text: Input text to correct
            max_length: Maximum length of generated text
            num_beams: Number of beams for beam search
            
        Returns:
            Corrected text
        """
        # Prepare input
        input_text = f"grammar: {text}"
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
        input_ids = input_ids.to(self.device)
        
        # Generate correction
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids,
                max_length=max_length,
                num_beams=num_beams,
                early_stopping=True,
                no_repeat_ngram_size=2
            )
        
        # Decode output
        corrected_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return corrected_text
    
    def batch_correct(self, texts, max_length=512, num_beams=4, batch_size=8):
        """
        Correct multiple texts in batches
        
        Args:
            texts: List of input texts
            max_length: Maximum length of generated text
            num_beams: Number of beams for beam search
            batch_size: Batch size for processing
            
        Returns:
            List of corrected texts
        """
        corrected_texts = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_corrected = []
            
            for text in batch:
                corrected = self.correct(text, max_length, num_beams)
                batch_corrected.append(corrected)
            
            corrected_texts.extend(batch_corrected)
        
        return corrected_texts
