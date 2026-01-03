from dotenv import load_dotenv
import os
from pathlib import Path
import time

from langchain_classic.embeddings import CacheBackedEmbeddings  
from langchain_classic.storage import LocalFileStore 
from langchain_openai import OpenAIEmbeddings



class Embed():
    def __init__(self):
        load_dotenv()

        self.embed_dir = Path(os.getenv("EMBED_DATA_DIR"))
        if not os.getenv("OPENAI_API_KEY"):
            print('OpenAI API key missing')

        self.underlying_embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            # reminder to checkout other models
            )

    def cached_embed(self, text, query=None):
        store = LocalFileStore(self.embed_dir)

        cached_embedder = CacheBackedEmbeddings.from_bytes_store(
                                self.underlying_embeddings,
                                store,
                                query_embedding_cache=True,
                                namespace=self.underlying_embeddings.model
                            )
        tic = time.time()
        cached_embedder.embed_documents(text)
        print(f"Embedded text: {text}, took {time.time() - tic:.2f}")

        if query:
            tic = time.time()
            cached_embedder.embed_query(query)
            print(f"Embedded query: {query}, took {time.time() - tic:.2f}")
            

if __name__ == "__main__":
    embed = Embed()
    embed.cached_embed(text=["hi anna"])