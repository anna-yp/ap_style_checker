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
import tiktoken
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
        '''
        load jsonl file as langchain doc and add url and token 
        as metadata using langchain's loader
        '''
        encoding = tiktoken.encoding_for_model("gpt-5-nano")

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

        for doc in docs:
            payload = json.loads(doc.page_content) 
            
            header = payload.get("entry_header") or payload.get("question") or ""
            body = payload.get("text_content") or payload.get("answer") or ""

            combined_text = f"{header}\n\n{body}".strip()
            token_count = len(encoding.encode(combined_text))

            doc.page_content = combined_text
            doc.metadata["source_url"] = payload.get("source_url")
            doc.metadata["token_count"] = token_count

        print(docs[-1])
        return docs
    
    def prep_docs(self, jsonl_names):
        for jsonl_name in jsonl_names:
            # self.cleaner.write_clean_jsonl(jsonl_name)
            doc = self.jsonl_ingest(jsonl_name)
            self.docs.extend(doc)

        return self.docs

    def build_vectorstore(self, docs):
        vectorstore = FAISS.from_documents(docs, self.embeddings)
        vectorstore.save_local(self.vectorstore_dir)

        print(f'New vectorstore: {vectorstore}')
        return vectorstore
    
    def to_similarity(self, score: float) -> float:
        if 0.0 <= score <= 1.0:
            return 1.0 - score
        return 1.0 / (1.0 + score)
    
    def metadata_func(self, record, metadata):
        return record.get("metadata", {})
    
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

            # doc.metadata['token_count'], doc.metadata["source_url"], doc.metadata["similarity_score"], doc.metadata["faiss_score"], 
            # print(doc)
            print(query)
            print(doc.metadata['token_count'], doc.metadata["source_url"], doc.metadata["similarity_score"], doc.metadata["faiss_score"])
        return similar_docs
    

jsonl = JsonlVectorPipeline()
names = ['2026-01-01blog_cleaned', '2026-01-01stylebook_cleaned', '2026-01-02editors_cleaned']
test_names = ['2026-01-01blog_cleaned']

# docs = jsonl.prep_docs(test_names)
# jsonl.build_vectorstore(docs)

# docs = []
# path = Path('/Users/Bettina/side_quests/ap_style_app/data/chunks/400:50chunks.jsonl')
# with open(path) as f:
#     for line in f:
#         record = json.loads(line)
#         docs.append(
#             Document(
#                 page_content=record["page_content"],
#                 metadata=record["metadata"],
#             )
#         )
        
# chunked_docs = docs
# print(chunked_docs[-1])
# jsonl.build_vectorstore(chunked_docs)

# jsonl.query_vectorstore('Should i captialize professor at a school')
