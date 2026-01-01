from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.build_vectorstore import JsonlVectorPipeline
from openai import OpenAI


class Prompt:
    def __init__(self, jsonl_name):
        self.client = OpenAI()
        self.pipeline = JsonlVectorPipeline(jsonl_name)

    def prompt_gpt(self, query):
        docs = self.pipeline.query_vectorstore(query)

        response = self.client.responses.create(
            model="gpt-5-nano",
            prompt={
                "id": "pmpt_69558e4ff7d08194ace89b24d12f6d630a5b47b0d1492450",
                "version": "4",
                "variables": {
                    "context": f"{docs}",
                    "question": f"{query}"
                },
            },
        )
        
        print(f'response: {response}')
        return response
