import os
from docx import Document
from typing import List, Dict

def extract_articles_from_docx(docx_path: str) -> List[Dict[str, str]]:
    """
    Extract articles from a Word document. Each article starts with a header and is separated by a section break.
    Returns a list of dicts: [{"title": ..., "content": ...}, ...]
    """
    try:
        doc = Document(docx_path)
    except Exception as e:
        raise ValueError(f"Error reading Word document '{docx_path}': {e}")
    
    articles = []
    current_article = {"title": None, "content": []}
    
    for para in doc.paragraphs:
        if para.style.name.startswith("Heading"):
            if current_article["title"] and current_article["content"]:
                articles.append({
                    "title": current_article["title"],
                    "content": "\n".join(current_article["content"]).strip()
                })
                current_article = {"title": None, "content": []}
            current_article["title"] = para.text.strip()
        else:
            current_article["content"].append(para.text)
    
    if current_article["title"] and current_article["content"]:
        articles.append({
            "title": current_article["title"],
            "content": "\n".join(current_article["content"]).strip()
        })
    
    return articles

def split_content_into_chunks(content: str, max_chars_per_chunk: int = 700000, articles: List[Dict[str, str]] = None) -> List[str]:
    """
    Split large content into chunks that fit within token limits.
    Tries to split at natural boundaries (articles) when possible.
    """
    if len(content) <= max_chars_per_chunk:
        return [content]
    
    # If we have article information, split by articles first
    if articles:
        chunks = []
        current_chunk = ""
        
        for article in articles:
            article_content = f"Title: {article['title']}\nContent: {article['content']}"
            
            # If adding this article would exceed the limit
            if len(current_chunk) + len(article_content) + 2 > max_chars_per_chunk:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = article_content
                else:
                    # If a single article is too long, fall back to paragraph splitting
                    chunks.extend(split_content_into_chunks(article_content, max_chars_per_chunk))
            else:
                current_chunk += "\n\n" + article_content if current_chunk else article_content
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    # Fallback to paragraph splitting if no article information
    chunks = []
    current_chunk = ""
    
    # Split by double newlines (paragraphs) first
    paragraphs = content.split('\n\n')
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed the limit
        if len(current_chunk) + len(paragraph) + 2 > max_chars_per_chunk:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                # If a single paragraph is too long, split it by sentences
                sentences = paragraph.split('. ')
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 2 > max_chars_per_chunk:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = sentence
                        else:
                            # If a single sentence is too long, split by words
                            words = sentence.split()
                            for word in words:
                                if len(current_chunk) + len(word) + 1 > max_chars_per_chunk:
                                    if current_chunk:
                                        chunks.append(current_chunk.strip())
                                        current_chunk = word
                                    else:
                                        # If a single word is too long, truncate it
                                        chunks.append(word[:max_chars_per_chunk])
                                else:
                                    current_chunk += " " + word if current_chunk else word
                    else:
                        current_chunk += ". " + sentence if current_chunk else sentence
        else:
            current_chunk += "\n\n" + paragraph if current_chunk else paragraph
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def process_data_directory(data_dir: str = "data") -> str:
    """
    Process all files in the data directory and return combined content.
    Currently supports .docx files.
    """
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory '{data_dir}' not found.")
    
    all_content = []
    all_articles = []
    
    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)
        
        if filename.lower().endswith('.docx'):
            print(f"Processing: {filename}")
            try:
                articles = extract_articles_from_docx(file_path)
                
                for article in articles:
                    # Add file information to article
                    article_with_file = {
                        "title": f"{filename}: {article['title']}",
                        "content": article['content']
                    }
                    all_articles.append(article_with_file)
                    
                    all_content.append(f"File: {filename}")
                    all_content.append(f"Title: {article['title']}")
                    all_content.append(f"Content: {article['content']}")
                    all_content.append("-" * 80)
            except Exception as e:
                print(f"Warning: Could not process {filename}: {e}")
                continue
    
    if not all_content:
        raise ValueError(f"No .docx files found in '{data_dir}' directory.")
    
    # Store articles for chunking
    process_data_directory.all_articles = all_articles
    
    return "\n".join(all_content) 