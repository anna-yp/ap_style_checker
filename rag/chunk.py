import os
from dotenv import load_dotenv
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
import nltk
from pathlib import Path
from build_vectorstore import JsonlVectorPipeline
import json

# --- NLTK Punkt Downloader ---
# Ensures all necessary NLTK tokenizer data is available.
nltk_resources = ['punkt', 'punkt_tab'] # List of NLTK resources to check/download

jsonl = JsonlVectorPipeline()
names = ['2026-01-01blog_cleaned', '2026-01-01stylebook_cleaned', '2026-01-02editors_cleaned']

print("--- Checking NLTK Data ---")
for resource in nltk_resources:
    try:
        # Attempt to find the resource first
        nltk.data.find(f'tokenizers/{resource}')
        print(f"NLTK '{resource}' tokenizer data already available.")
    except LookupError: # Catch the specific LookupError if resource is not found
        print(f"NLTK '{resource}' tokenizer data not found. Downloading...")
        nltk.download(resource)
        print(f"NLTK '{resource}' data downloaded.")
print("--- NLTK Data Check Complete ---\n")
# End of NLTK download block

# --- Configuration ---
# LangChain Chunker Configuration
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50

load_dotenv()
chunk_dir = Path(os.getenv("CHUNK_DIR"))

data_name = (f'{CHUNK_SIZE}:{CHUNK_OVERLAP}chunks.jsonl')
data_output_path = chunk_dir/f"{data_name}"

info_name = (f'{CHUNK_SIZE}:{CHUNK_OVERLAP}info.txt')
info_output_path = chunk_dir/f"{info_name}"

# --- Tiktoken Token Counting ---
TOKENIZER = tiktoken.encoding_for_model("gpt-5-nano")

def count_tokens(text: str) -> int:
    """Counts tokens using a tiktoken encoder."""
    return len(TOKENIZER.encode(text))

def count_sentences(text: str) -> int:
    """Counts sentences using NLTK's punkt tokenizer."""
    # Ensure text is not empty or just whitespace to avoid issues with nltk.sent_tokenize
    if not text or not text.strip():
        return 0
    sentences = nltk.sent_tokenize(text)
    return len(sentences)

def main():
    # 2. Initialize the LangChain Text Splitter 
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len, # Use character length for splitting
        separators=["\n\n", "\n", " ", ""] # Prioritize logical breaks
    )
    print("--- LangChain Chunker Initialized ---")
    print(f"Chunk Size: {CHUNK_SIZE} | Overlap: {CHUNK_OVERLAP}\n")

    # 3. Process Documents
    raw_char_count = 0
    raw_token_count = 0
    raw_sentence_count = 0 
    total_chunks_processed = 0

    documents = jsonl.prep_docs(names)

    # 4. Chunk the documents
    # The split_documents method takes a list of Document objects and returns a list of smaller Document objects
    chunks = text_splitter.split_documents(documents)

    for chunk in chunks:
        token_count = count_tokens(chunk.page_content)
        chunk.metadata['token_count'] = token_count

    num_chunks = len(chunks)
    total_chunks_processed += num_chunks

    # --- Estimate Raw Document Metrics ---
    for doc in documents:
        raw_char_count += len(doc.page_content)
        raw_token_count += count_tokens(doc.page_content)
        raw_sentence_count += count_sentences(doc.page_content)

    avg_char = raw_char_count/len(documents)
    avg_token = raw_token_count/len(documents)
    avg_sent = raw_sentence_count/len(documents)

    # 6. Write Output to File
    with data_output_path.open("w", encoding="utf-8") as f:
        for doc in chunks:
            record = {
                "page_content": doc.page_content,
                "metadata": doc.metadata,
            }
            json.dump(record, f)
            f.write("\n")

    with open(info_output_path, 'w', encoding='utf-8') as f:
        f.write(f"--- Document Chunking & Estimation Results ---\n")
        f.write(f"Chunk Size: {CHUNK_SIZE} | Overlap: {CHUNK_OVERLAP}\n\n")

        f.write(f"--- Overall Document Statistics (before chunking) ---\n")
        f.write(f"  Total Raw Characters Across All Processed Files: {raw_char_count}\n")
        f.write(f"  Total Raw Tokens (tiktoken est.) Across All Processed Files: {raw_token_count}\n")
        f.write(f"  Total Raw Estimated Sentences Across All Processed Files: {raw_sentence_count}\n")

        # Calculate averages only if files were actually processed
        f.write(f"  Average Chars per Processed Document: { avg_char:.2f}\n")
        f.write(f"  Average Tokens per Processed Document: { avg_token:.2f}\n")
        f.write(f"  Average Sentences per Processed Document: {avg_sent:.2f}\n")

        f.write(f"\n--- Detailed File Results ---\n")
        f.write(f"--- Summary ---\n")
        f.write(f"TOTAL VECTORS/CHUNKS PROCESSED ACROSS ALL DOCUMENTS: {total_chunks_processed}\n")

    print(f"\n--- Processing Complete ---")
    print(f"Total Vectors/Chunks created across all documents: {total_chunks_processed}")

if __name__ == "__main__":
    main()