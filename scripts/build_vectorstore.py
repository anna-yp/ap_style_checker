from pathlib import Path
import sys
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.embedding import Embed  
from rag.ingest import Ingest 
from scripts.clean_data import cleanJsonl  

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
load_dotenv()

class JsonlVectorPipeline:
    def __init__(self):
        self.cleaner = cleanJsonl()
        self.ingestor = Ingest()
        self.embedder = Embed()

    def build_vectorstore(self, jsonl_name):
        self.cleaner.write_clean_jsonl(jsonl_name)
        docs = self.ingestor.jsonl_ingest(f"{jsonl_name}_cleaned")

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large")
        
        vectorstore = FAISS.from_documents(docs, embeddings)
        
        print(vectorstore)


if __name__ == "__main__":
    pipeline = JsonlVectorPipeline()
    pipeline.build_vectorstore('2025-12-31')
