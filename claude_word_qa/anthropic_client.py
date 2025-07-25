import os
import httpx
import time
from dotenv import load_dotenv
from typing import Optional, List
from .doc_parser import split_content_into_chunks

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
MODEL_NAME_CLAUDE_4 = "claude-sonnet-4-20250514"
MODEL_NAME_CLAUDE_35 = "claude-3-5-sonnet-20241022"

def ask_claude_single_chunk(question: str, document_chunk: str, chunk_number: int, total_chunks: int, max_tokens: int = 1500) -> Optional[str]:
    """
    Send a prompt to Claude API for a single chunk and return the response.
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
        clean_document_text = document_chunk.encode('utf-8', errors='ignore').decode('utf-8')
    except Exception:
        # Fallback: replace problematic characters
        clean_document_text = document_chunk.encode('ascii', errors='ignore').decode('ascii')
    
    chunk_info = f" (Chunk {chunk_number} of {total_chunks})" if total_chunks > 1 else ""
    
    prompt = f"""You are a helpful assistant. The following is the content of documents from a data directory{chunk_info}:

{clean_document_text}

Question: {question}

IMPORTANT: You must include citations in parentheses after every factual claim you make. Citations should include the article title, publication name, and publication date if available from the document. For example: (Title: "Article Name", Publication: "Miami Herald", Date: 2024-01-15) or (Title: "Article Name", Publication: "Miami Herald") if no date is available.

Please answer in 500 words or fewer. If this is part of a larger document, focus on the information present in this chunk."""

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
                    print(f"✓ Successfully used {model_display_name} for chunk {chunk_number}/{total_chunks}")
                    return result["content"][0]["text"].strip()
                return None
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 529:  # Overloaded error
                print(f"⚠ {model_display_name} is overloaded for chunk {chunk_number}, trying fallback...")
                continue  # Try the next model
            else:
                print(f"HTTP error occurred with {model_display_name} for chunk {chunk_number}: {e}")
                if hasattr(e, 'response'):
                    print(f"Response content: {e.response.text}")
                continue  # Try the next model
                
        except UnicodeDecodeError as e:
            print(f"Unicode decode error with {model_display_name} for chunk {chunk_number}: {e}")
            continue  # Try the next model
            
        except Exception as e:
            print(f"Error occurred with {model_display_name} for chunk {chunk_number}: {e}")
            import traceback
            traceback.print_exc()
            continue  # Try the next model
    
    # If we get here, all models failed for this chunk
    print(f"❌ All models failed for chunk {chunk_number}. Skipping this chunk.")
    return None

def ask_claude(question: str, document_text: str, max_tokens: int = 1500) -> Optional[str]:
    """
    Send a prompt to Claude API using batching for large documents.
    """
    # Clean the document text to ensure it's valid UTF-8
    try:
        # Encode and decode to remove any invalid UTF-8 characters
        clean_document_text = document_text.encode('utf-8', errors='ignore').decode('utf-8')
    except Exception:
        # Fallback: replace problematic characters
        clean_document_text = document_text.encode('ascii', errors='ignore').decode('ascii')
    
    # Split into chunks if document is too large (rough estimate: 4 chars per token)
    # Leave room for question and instructions (estimate ~1000 tokens)
    max_chars_per_chunk = (200000 - 1000) * 4  # ~796,000 characters
    chunks = split_content_into_chunks(clean_document_text, max_chars_per_chunk)
    
    if len(chunks) > 1:
        print(f"📄 Document split into {len(chunks)} chunks for processing")
    
    # Process each chunk
    chunk_responses = []
    for i, chunk in enumerate(chunks, 1):
        response = ask_claude_single_chunk(question, chunk, i, len(chunks), max_tokens)
        if response:
            chunk_responses.append(response)
        else:
            print(f"⚠ Chunk {i} failed to process, continuing with remaining chunks...")
    
    if not chunk_responses:
        print("❌ All chunks failed to process.")
        return None
    
    # If we only have one chunk or one response, return it directly
    if len(chunk_responses) == 1:
        return chunk_responses[0]
    
    # Combine multiple responses
    print(f"🔄 Combining responses from {len(chunk_responses)} chunks...")
    combined_response = combine_chunk_responses(chunk_responses, question)
    
    return combined_response

def combine_chunk_responses(responses: List[str], original_question: str) -> str:
    """
    Combine multiple chunk responses into a coherent final answer.
    """
    # If we have multiple responses, ask Claude to synthesize them
    combined_text = "\n\n---\n\n".join(responses)
    
    synthesis_prompt = f"""You are a helpful assistant. I have analyzed a large document by breaking it into chunks and asking the same question about each chunk. Here are the responses from each chunk:

{combined_text}

Original Question: {original_question}

Please synthesize these responses into a single, coherent answer that:
1. Combines all relevant information from all chunks
2. Eliminates redundancy and contradictions
3. Maintains all important citations and factual claims
4. Stays within 500 words
5. Provides a comprehensive answer to the original question

IMPORTANT: Preserve all citations in parentheses after factual claims."""

    # Use the same API call logic for synthesis
    return ask_claude_single_chunk(original_question, synthesis_prompt, 1, 1, max_tokens=2000) 