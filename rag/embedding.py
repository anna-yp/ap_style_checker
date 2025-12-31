import getpass
from dotenv import load_dotenv
import os
import time
from langchain_classic.embeddings import CacheBackedEmbeddings  
from langchain_classic.storage import LocalFileStore 
from langchain_openai import OpenAIEmbeddings

class Embed():

    def __init__(self):
        load_dotenv()
        if not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

        self.store = LocalFileStore("/Users/Bettina/side_quests/ap_style_app/data/embeddings/") 
        self.underlying_embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            # With the `text-embedding-3` class
            # of models, you can specify the size
            # of the embeddings you want returned.
            # dimensions=1024
        )

    def cached_embed(self, text):
        cached_embedder = CacheBackedEmbeddings.from_bytes_store(
                                self.underlying_embeddings,
                                self.store,
                                query_embedding_cache=True,
                                namespace=self.underlying_embeddings.model
                            )
        
        tic = time.time()
        print(f"Second call took: {time.time() - tic:.2f} seconds")
        return cached_embedder.embed_query(text)
    
    
embed = Embed()
embed.cached_embed("i'm anna")

    # Example: caching a query embedding
    # tic = time.time()
    # print(cached_embedder.embed_query("Hello, world!"))
    # print(f"First call took: {time.time() - tic:.2f} seconds")

    # Subsequent calls use the cache
    # tic = time.time()
    # print(cached_embedder.embed_query("Hello, world!"))
    # print(f"Second call took: {time.time() - tic:.2f} seconds")