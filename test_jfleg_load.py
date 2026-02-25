"""
Quick test script to check if JFLEG dataset loads correctly
"""

from datasets import load_dataset
import pandas as pd

print("Testing JFLEG dataset loading...")
try:
    print("Loading dataset (this may take a moment to download)...")
    dataset = load_dataset("jhu-clsp/jfleg")
    
    print(f"Dataset splits: {list(dataset.keys())}")
    
    if 'test' in dataset:
        test_size = len(dataset['test'])
        print(f"Test set size: {test_size}")
        
        # Show first example
        first_example = dataset['test'][0]
        print(f"\nFirst example:")
        print(f"  Sentence: {first_example['sentence']}")
        print(f"  Corrections: {first_example['corrections']}")
        print(f"  Number of references: {len(first_example['corrections'])}")
    
    if 'dev' in dataset:
        dev_size = len(dataset['dev'])
        print(f"Dev set size: {dev_size}")
    
    print("\nDataset loaded successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
