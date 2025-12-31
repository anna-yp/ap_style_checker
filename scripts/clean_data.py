import json
import os
from dotenv import load_dotenv
import re
from pathlib import Path


class cleanJsonl:
    def __init__(self):
        load_dotenv()

        self.data_dir = Path(os.getenv("DATA_DIR"))
        self.raw_dir = Path(os.getenv("RAW_DATA_DIR"))
        self.clean_dir = Path(os.getenv("CLEAN_DATA_DIR"))

    def clean_text(self, text):
        '''normalizes white_space, fixes hidden dahses, and emoves space before punctation'''
        whitespace_normalized_text = re.sub(r"\s+", " ", text).strip()
        fixed_dashes_text = re.sub(r"[‐-‒–—―]", "—", whitespace_normalized_text)
        clean_punct_text = re.sub(r"\s+([.,!?;:])", r"\1", fixed_dashes_text)
        return clean_punct_text

    def write_clean_jsonl(self, jsonl_name):
        '''takes raw jsonl, clean text, write to a clean directory'''
        input_path =  self.raw_dir/f'{jsonl_name}.jsonl'
        output_path = self.clean_dir/f'{jsonl_name}_cleaned.jsonl'

        with open(input_path, "r", encoding="utf-8") as infile, open(
            output_path, "w", encoding="utf-8" ) as outfile:
            for line in infile:
                field = json.loads(line)
                for key in field.keys():
                    field[key] = self.clean_text(field[key])
                outfile.write(json.dumps(field, ensure_ascii=False) + "\n")

        return output_path

if __name__ == "__main__":
    cleaner = cleanJsonl()
    cleaner.write_clean_jsonl("2025-12-31")
