"""
Quick check: is Azure OpenAI endpoint responding?
Makes one simple API call with a short timeout. No evaluation.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check():
    print("Checking Azure OpenAI endpoint...")
    print("-" * 50)
    
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not api_key:
        print("FAIL: AZURE_OPENAI_API_KEY not set in .env")
        return False
    if not endpoint:
        print("FAIL: AZURE_OPENAI_ENDPOINT not set in .env")
        return False
    if not deployment:
        print("FAIL: AZURE_OPENAI_DEPLOYMENT_NAME not set in .env")
        return False
    
    print(f"Endpoint: {endpoint}")
    print(f"Deployment: {deployment}")
    print("Making one simple request (timeout=15s)...")
    print()
    
    try:
        from openai import AzureOpenAI
        client = AzureOpenAI(
            api_key=api_key,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=endpoint,
            timeout=15.0,
        )
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": "Reply with exactly: OK"}],
            max_tokens=10,
            timeout=15.0,
        )
        text = (response.choices[0].message.content or "").strip()
        print("SUCCESS: Azure OpenAI responded.")
        print(f"Response: {text[:100]}")
        return True
    except Exception as e:
        print("FAIL: Azure OpenAI did not respond successfully.")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    ok = check()
    print()
    print("=" * 50)
    sys.exit(0 if ok else 1)
