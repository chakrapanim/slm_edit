"""
Test script to verify Azure OpenAI API connection and credentials
"""

import os
from dotenv import load_dotenv
from llm_evaluator import LLMEvaluator

# Load environment variables from .env file
load_dotenv()

def test_llm_connection():
    """Test if LLM evaluator can connect and make a simple API call"""
    print("=" * 80)
    print("Testing LLM Connection")
    print("=" * 80)
    print()
    
    # Check environment variables
    print("Checking environment variables...")
    print("-" * 80)
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_version = os.getenv("AZURE_OPENAI_API_VERSION")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print(f"AZURE_OPENAI_API_KEY: {'✓ Set' if azure_key else '✗ Not set'}")
    print(f"AZURE_OPENAI_ENDPOINT: {'✓ Set' if azure_endpoint else '✗ Not set'}")
    print(f"AZURE_OPENAI_DEPLOYMENT_NAME: {'✓ Set' if azure_deployment else '✗ Not set'}")
    print(f"AZURE_OPENAI_API_VERSION: {'✓ Set' if azure_version else '✗ Not set (will use default)'}")
    print(f"OPENAI_API_KEY: {'✓ Set' if openai_key else '✗ Not set'}")
    print()
    
    # Try to initialize LLM evaluator
    print("Initializing LLM Evaluator...")
    print("-" * 80)
    try:
        llm_evaluator = LLMEvaluator()
        print("✓ LLM Evaluator initialized successfully!")
        print(f"  Using: {'Azure OpenAI' if llm_evaluator.use_azure else 'OpenAI'}")
        print(f"  Model/Deployment: {llm_evaluator.model}")
        if llm_evaluator.use_azure:
            print(f"  Endpoint: {llm_evaluator.endpoint}")
            print(f"  API Version: {llm_evaluator.api_version}")
        print()
    except Exception as e:
        print(f"✗ Failed to initialize LLM Evaluator: {e}")
        return False
    
    # Test with a simple evaluation
    print("Testing API call with a simple example...")
    print("-" * 80)
    try:
        # Test typo evaluation
        test_input = "I recieved your email."
        test_truth = "I received your email."
        test_predicted = "I received your email."
        
        print(f"Test Input: '{test_input}'")
        print(f"Ground Truth: '{test_truth}'")
        print(f"Model Prediction: '{test_predicted}'")
        print()
        print("Making API call...")
        
        result = llm_evaluator.evaluate_typo(test_input, test_truth, test_predicted)
        
        print("✓ API call successful!")
        print()
        print("Result:")
        print(f"  Score: {result['score']}/5")
        print(f"  Explanation: {result['explanation']}")
        print()
        
        # Verify the result structure
        if 'score' in result and 'explanation' in result:
            if 1 <= result['score'] <= 5:
                print("✓ Result structure is valid!")
                return True
            else:
                print(f"✗ Invalid score: {result['score']} (should be 1-5)")
                return False
        else:
            print("✗ Invalid result structure")
            return False
            
    except Exception as e:
        print(f"✗ API call failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_llm_connection()
    
    print("=" * 80)
    if success:
        print("✓ All tests passed! LLM connection is working correctly.")
        print("You can now run the full evaluation with LLM scoring.")
    else:
        print("✗ Tests failed. Please check your .env file and API credentials.")
    print("=" * 80)
