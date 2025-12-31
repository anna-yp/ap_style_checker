import os
from dotenv import load_dotenv
from pathlib import Path

from langchain_community.document_loaders import JSONLoader


class Ingest:
    def __init__(self):
        load_dotenv()
        self.clean_dir = Path(os.getenv("CLEAN_DATA_DIR"))

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


if __name__ == "__main__":
    ingest = Ingest()
    ingest.jsonl_ingest("2025-12-31_cleaned")
