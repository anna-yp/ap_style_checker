from pathlib import Path
import sys
import os
from dotenv import load_dotenv
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.embedding import Embed  
from scripts.ingest import Ingest 
from rag.clean_data import cleanJsonl  

from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores import FAISS
load_dotenv()

class JsonlVectorPipeline:
    def __init__(self):
        self.cleaner = cleanJsonl()

        self.clean_dir = Path(os.getenv("CLEAN_DATA_DIR"))
        self.vectorstore_dir = Path(os.getenv("VECTORSTORE_DIR"))

        self.docs = []
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    def jsonl_ingest(self, jsonl_name: str):
        '''load jsonl file as langchain doc once and then twice
            with the url as metadata using langchain's loader
        '''
        file_path = self.clean_dir/f"{jsonl_name}.jsonl"
        if not file_path:
            print('JSONL hasn\'t been cleaned yet')
            return

        loader = JSONLoader(
            file_path=str(file_path),
            jq_schema=".",
            text_content=False,
            json_lines=True,
        )
        
        docs = loader.load()
    
        raw_docs = loader.load()
        docs = []
        for doc in raw_docs:
            payload = json.loads(doc.page_content) 

            header = payload.get("entry_header") or payload.get("question") or ""
            body = payload.get("text_content") or payload.get("answer") or ""

            combined_text = f"{header}\n\n{body}".strip()

            docs.append(
                Document(
                    page_content=combined_text,
                    metadata={
                        **doc.metadata,            
                        "source_url": payload.get("source_url"),
                    },
                )
            )
        return docs
    
    def prep_docs(self, jsonl_names):
        for jsonl_name in jsonl_names:
            self.cleaner.write_clean_jsonl(jsonl_name)
            doc = self.jsonl_ingest(jsonl_name)
            self.docs.extend(doc)

        return self.docs

    def build_vectorstore(self, docs):
        vectorstore = FAISS.from_documents(docs, self.embeddings)
        vectorstore.save_local(self.vectorstore_dir)

        print(f'New vectorstore: {vectorstore}')
        return vectorstore
    
    def to_similarity(score: float) -> float:
        if 0.0 <= score <= 1.0:
            return 1.0 - score
        return 1.0 / (1.0 + score)
    
    def query_vectorstore(self, query: str) -> tuple:
        vectorstore = FAISS.load_local(self.vectorstore_dir, self.embeddings, allow_dangerous_deserialization=True)
        if not vectorstore:
            print("Vectorstore hasn't been created yet")

        similar_docs = vectorstore.similarity_search_with_score(
            f"{query}",
            k=4
            )
        
        for doc, score in similar_docs:
            doc.metadata["faiss_score"] = score
             
            similarity_score = self.to_similarity(score)
            doc.metadata["similarity_score"] = similarity_score

            print(doc.metadata["source_url"], doc.metadata["similarity_score"], doc.metadata["faiss_score"], )
        return similar_docs
    
    

jsonl = JsonlVectorPipeline()
# names = ['2026-01-01blog_cleaned', '2026-01-01stylebook_cleaned', '2026-01-02editors_cleaned']
# docs = jsonl.prep_docs(names)
# jsonl.build_vectorstore(docs)

jsonl.query_vectorstore('Should i captialize principal of a school')
