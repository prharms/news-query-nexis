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

def process_data_directory(data_dir: str = "data") -> str:
    """
    Process all files in the data directory and return combined content.
    Currently supports .docx files.
    """
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory '{data_dir}' not found.")
    
    all_content = []
    
    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)
        
        if filename.lower().endswith('.docx'):
            print(f"Processing: {filename}")
            try:
                articles = extract_articles_from_docx(file_path)
                
                for article in articles:
                    all_content.append(f"File: {filename}")
                    all_content.append(f"Title: {article['title']}")
                    all_content.append(f"Content: {article['content']}")
                    all_content.append("-" * 80)
            except Exception as e:
                print(f"Warning: Could not process {filename}: {e}")
                continue
    
    if not all_content:
        raise ValueError(f"No .docx files found in '{data_dir}' directory.")
    
    return "\n".join(all_content) 