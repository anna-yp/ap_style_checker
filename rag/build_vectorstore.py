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

        self.docs = None
        self.vectorstore = None

    def prep_docs(self, jsonl_name):
        self.cleaner.write_clean_jsonl(jsonl_name)
        docs = self.ingestor.jsonl_ingest(f"{jsonl_name}_cleaned")
        
        self.docs = docs
        return docs

    def build_vectorstore(self, docs):
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small")
        
        vectorstore = FAISS.from_documents(docs, embeddings)

        print(vectorstore)
        self.vectorstore = vectorstore
        return vectorstore
    
    def query_vectorstore(self, query: str) -> tuple:
        similar_docs = self.vectorstore.similarity_search_with_score(
            f"{query}"
            )
        for doc, score in similar_docs:
            print(doc, score)

        self.similar_docs = similar_docs
        return similar_docs
    

query = JsonlVectorPipeline()
docs = query.prep_docs('2025-12-31')
query.build_vectorstore(docs)
question = "How  does AP handle titles for retired professors like ‘Professor Emeritus Susan Johnson’ when writing about Pride events?"
query.query_vectorstore(question)


# class QueryVectorstore():
#     def __init__(self, jsonl_name: str):
#         pipeline = JsonlVectorPipeline()
#         self.docs = pipeline.prep_docs(jsonl_name) if not pipeline.docs else pipeline.docs
#         self.vectorstore = pipeline.build_vectorstore(jsonl_name)
#         self.similar_docs = None

#     def to_relevance(score: float) -> float:
#         if 0.0 <= score <= 1.0:
#             return 1.0 - score
#         return 1.0 / (1.0 + score)

#     def query_vectorstore(self, query: str) -> tuple:
#         similar_docs = self.vectorstore.similarity_search_with_score(
#             f"{query}"
#             )
#         for doc, score in similar_docs:
#             print(doc, score)

#         self.similar_docs = similar_docs
#         return similar_docs
    
#     def synthesize_similar_docs(self):
#         pass
    
    

    
