import os
import httpx
import time
from dotenv import load_dotenv
from typing import Optional

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
MODEL_NAME_CLAUDE_4 = "claude-sonnet-4-20250514"
MODEL_NAME_CLAUDE_35 = "claude-3-5-sonnet-20241022"

def ask_claude(question: str, document_text: str, max_tokens: int = 1500) -> Optional[str]:
    """
    Send a prompt to Claude 4 Sonnet API and return the response.
    """
    # Try to load from .env file in current directory and parent directories
    load_dotenv(dotenv_path=".env", verbose=True)
    load_dotenv(dotenv_path="../.env", verbose=True)
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        # Provide more helpful error message
        raise RuntimeError(
            "ANTHROPIC_API_KEY not found in environment.\n"
            "Please create a .env file with: ANTHROPIC_API_KEY=your_api_key_here\n"
            "Or set the environment variable directly."
        )

    # Clean the document text to ensure it's valid UTF-8
    try:
        # Encode and decode to remove any invalid UTF-8 characters
        clean_document_text = document_text.encode('utf-8', errors='ignore').decode('utf-8')
    except Exception:
        # Fallback: replace problematic characters
        clean_document_text = document_text.encode('ascii', errors='ignore').decode('ascii')
    
    prompt = f"""You are a helpful assistant. The following is the content of documents from a data directory:

{clean_document_text}

Question: {question}

IMPORTANT: You must include citations in parentheses after every factual claim you make. Citations should include the article title, publication name, and publication date if available from the document. For example: (Title: "Article Name", Publication: "Miami Herald", Date: 2024-01-15) or (Title: "Article Name", Publication: "Miami Herald") if no date is available.

Please answer in 500 words or fewer."""

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # Try Claude 4 first, then fallback to Claude 3.5 if overloaded
    models_to_try = [
        (MODEL_NAME_CLAUDE_4, "Claude 4 Sonnet"),
        (MODEL_NAME_CLAUDE_35, "Claude 3.5 Sonnet")
    ]
    
    for model_name, model_display_name in models_to_try:
        data = {
            "model": model_name,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            with httpx.Client(timeout=60) as client:
                response = client.post(CLAUDE_API_URL, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                
                if "content" in result and result["content"]:
                    print(f"✓ Successfully used {model_display_name}")
                    return result["content"][0]["text"].strip()
                return None
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 529:  # Overloaded error
                print(f"⚠ {model_display_name} is overloaded, trying fallback...")
                continue  # Try the next model
            else:
                print(f"HTTP error occurred with {model_display_name}: {e}")
                if hasattr(e, 'response'):
                    print(f"Response content: {e.response.text}")
                continue  # Try the next model
                
        except UnicodeDecodeError as e:
            print(f"Unicode decode error with {model_display_name}: {e}")
            continue  # Try the next model
            
        except Exception as e:
            print(f"Error occurred with {model_display_name}: {e}")
            import traceback
            traceback.print_exc()
            continue  # Try the next model
    
    # If we get here, all models failed
    print("❌ All models failed or are overloaded. Please try again later.")
    return None 