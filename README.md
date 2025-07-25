# News Query Nexis

A command-line tool that allows you to ask questions about documents stored in a data directory using Anthropic's Claude 4 Sonnet API with automatic fallback to Claude 3.5 Sonnet. Built for forensic-level accuracy with comprehensive anti-hallucination protocols.

## Features

- Processes all `.docx` files in a data directory
- Extracts articles and content from Word documents
- Sends questions to Claude 4 Sonnet API with automatic fallback to Claude 3.5 Sonnet
- Intelligent document batching to process large files without truncation
- **Forensic-level anti-hallucination protocols** ensuring only explicitly stated information is reported
- **Zero creativity mode** - AI forbidden from creating, inventing, or inferring information
- **Exact quote verification** - Only uses quotation marks for text that appears exactly in source material
- Requires citations with title, publication name, and date for all factual claims
- Saves output as professionally formatted Word documents with timestamps
- Returns concise responses (500 words or fewer)
- Simple executable command (`claude-qa`) instead of complex Python module calls
- Robust error handling and fallback mechanisms
- **Comprehensive technical details** in output documents showing processing workflow
- **Legal liability awareness** - designed for use in professional and legal contexts
- Follows Python best practices and PEP 8 style guide

## Requirements

- Python 3.8 or higher
- Anthropic API key
- Word documents in `.docx` format

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/prharms/news-query-nexis.git
   cd news-query-nexis
   ```
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Create a `.env` file in the project root with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

### Basic Usage

Ask a question about all documents in the default `data/` directory:

```bash
claude-qa "What is the main topic discussed in these documents?"
```

### Custom Data Directory

Specify a different directory containing your documents:

```bash
claude-qa "Summarize the key points" --data-dir /path/to/your/documents
```

### Example Questions

- "What are the main themes across all documents?"
- "Which document contains information about [specific topic]?"
- "Summarize the key findings from these documents"
- "What are the common patterns or trends mentioned?"
- "What public policy positions has [person] taken on [issue]?"

## Project Structure

```
claude_word_qa/
├── __init__.py          # Package initialization
├── cli.py              # Command-line interface
├── doc_parser.py       # Document processing logic
├── anthropic_client.py # Claude API communication with fallback
├── pyproject.toml      # Project configuration
└── README.md           # This file

data/                   # Default directory for documents
└── Files(50).docx     # Example document

output/                 # Generated Word documents
└── claude_qa_*.docx   # Timestamped output files

.env                    # Environment variables (create this)
```

## How It Works

1. **Document Processing**: The tool scans the specified data directory for `.docx` files
2. **Content Extraction**: Each document is parsed to extract articles and their content
3. **Forensic Analysis**: AI operates as a forensic document examiner conducting critical legal analysis
4. **Question Submission**: Your question and the combined document content are sent to Claude 4 Sonnet
5. **Intelligent Batching**: Large documents are automatically split into manageable chunks and processed separately
6. **Response Synthesis**: Multiple chunk responses are intelligently combined into a coherent final answer
7. **Automatic Fallback**: If Claude 4 is overloaded, automatically tries Claude 3.5 Sonnet
8. **Anti-Hallucination Verification**: Every claim is verified against source material before inclusion
9. **Response with Citations**: Claude returns a concise answer with required citations (title, publication, date)
10. **Word Document Output**: Results are saved as professionally formatted Word documents with timestamps and technical details

## Anti-Hallucination Protocols

The tool implements rigorous anti-hallucination measures:

- **Zero Creativity**: AI is forbidden from creating, inventing, or inferring information not explicitly present
- **Exact Text Only**: Quotation marks are only used for text that appears exactly as written in source material
- **Verification Required**: Every statement must be verified against the source material before inclusion
- **No Inference**: No conclusions, connections, or implications beyond what is explicitly stated
- **Citation Mandatory**: Every factual claim must include exact article title, publication name, and date
- **Legal Liability Awareness**: Designed for use in legal proceedings with professional consequences for fabricated information
- **Explicit Limitations**: When information is not found, explicitly states "The source material does not contain information about [topic]"

## Error Handling

The tool handles various error conditions:
- Missing data directory
- No `.docx` files found
- Large documents exceeding token limits (automatic batching and chunking)
- API overload conditions (automatic fallback to Claude 3.5)
- API connection issues and timeouts (exponential backoff retry logic)
- Invalid API responses
- UTF-8 encoding issues
- Failed chunk processing (continues with remaining chunks)
- Network timeouts (120-second timeout with retry mechanism)

## Configuration

### Environment Variables

Create a `.env` file with:
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### API Model

The tool uses Claude 4 Sonnet by default with automatic fallback to Claude 3.5 Sonnet if the primary model is overloaded. Large documents are automatically split into chunks and processed separately, then intelligently combined into a comprehensive answer. This ensures no information is lost and provides reliable operation even during high-demand periods and with very large document sets.

### Technical Details

Output documents include comprehensive technical details:
- LLM model version used for each chunk
- Document processing workflow (chunks created, processed, failed)
- Chunk-by-chunk processing details with sizes and models
- Response synthesis status
- Processing timestamps and performance metrics

## Development

To run tests (when implemented):
```bash
pytest
```

## Repository

- **GitHub**: [https://github.com/prharms/news-query-nexis](https://github.com/prharms/news-query-nexis)
- **Issues**: Report bugs or request features via GitHub Issues
- **Contributions**: Pull requests welcome

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Support

For issues or questions, please check the error messages or review the documentation. You can also open an issue on the GitHub repository. 