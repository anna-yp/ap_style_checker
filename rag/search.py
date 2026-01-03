from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.build_vectorstore import JsonlVectorPipeline
from openai import OpenAI


class Prompt:
    def __init__(self):
        self.client = OpenAI()
        self.pipeline = JsonlVectorPipeline()

    def prompt_gpt(self, query):
        similar_docs = self.pipeline.query_vectorstore(query)

        response = self.client.responses.create(
            model="gpt-5-nano",
            prompt={
                "id": "pmpt_69558e4ff7d08194ace89b24d12f6d630a5b47b0d1492450",
                "version": "4",
                "variables": {
                    "context": f"{similar_docs}",
                    "question": f"{query}"
                },
            },
        )

        print(f'output: {response.output_text}')
        print(f'response: {response}')
        return response


# prompt = Prompt()
# prompt.prompt_gpt('Is it 3-year-old or 3 year old in AP Style when describing a child, and does it change if the phrase follows the noun?')