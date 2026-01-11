from pathlib import Path
import sys
import os
from dotenv import load_dotenv
import time
import datetime
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

from rag.build_vectorstore import JsonlVectorPipeline
from openai import OpenAI


class Prompt:
    def __init__(self):
        self.client = OpenAI()
        self.pipeline = JsonlVectorPipeline()

    def prompt_gpt(self, query):
        similar_docs = self.pipeline.query_vectorstore(query)
        for doc in similar_docs:
            print(doc)

        start = time.perf_counter()

        response = self.client.responses.create(
            model="gpt-4.1-nano",
            prompt={
                "id": "pmpt_69558e4ff7d08194ace89b24d12f6d630a5b47b0d1492450",
                "version": "4",
                "variables": {
                    "context": f"{similar_docs}",
                    "question": f"{query}"
                },
            },
            max_output_tokens=1500
        )

        duration = start - time.perf_counter()

        log_dir = Path(os.getenv("LOG_DIR"))
        log_dir.mkdir(exist_ok=True)

        doc_stats = []
        usage = response.usage or {}

        for doc, score in similar_docs:
            doc_stats.append({
                "source_url": doc.metadata['source_url'],
                "tokens": doc.metadata['token_count']
            })

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "question": query,
            "doc_stats": doc_stats,
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "total_tokens": usage.total_tokens,
            "model_output": response.output_text,
            "raw_response": response.to_dict(),
            "response_time_seconds": duration
        }
        with (log_dir / "rag_calls.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record))
            f.write("\n")

        print(query)
        print(f'output: {response.output_text}')
        # print(response)
        return response


# prompt = Prompt()
# prompt.prompt_gpt('Should i capitalize professor in ap style?')