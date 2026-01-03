from pathlib import Path
import sys
import os
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.embedding import Embed  
from scripts.ingest import Ingest 
from rag.clean_data import cleanJsonl  

from langchain_openai import OpenAIEmbeddings
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
        '''load jsonl file as langchain doc using langchain's loader'''
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
        return loader.load()
    
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
    
    def query_vectorstore(self, query: str) -> tuple:
        vectorstore = FAISS.load_local(self.vectorstore_dir, self.embeddings, allow_dangerous_deserialization=True)
        if not vectorstore:
            print("Vectorstore hasn't been created yet")

        similar_docs = vectorstore.similarity_search_with_score(
            f"{query}",
            k=5
            )
        
        # print(similar_docs[:3])
        return similar_docs
    

# json = JsonlVectorPipeline()
# json.query_vectorstore('Should i captialize principal of a school')
