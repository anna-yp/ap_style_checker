import re
import json
from pathlib import Path

class cleanJsonl:
    # def __init__(name):
    #     jsonl_name = name
    #     base = Path("/Users/Bettina/side_quests/ap_style_app/data/")

    #     input_path = base/f'raw/{name}.jsonl'
    #     output_path = base/f'cleaned/{name}_cleaned.jsonl'

    def clean_text(self, text):
        text = re.sub(r"\s+", " ", text).strip() #normalize whitespace
        text = re.sub(r"[‐-‒–—―]", "—", text) #broken dashes
        text = re.sub(r"\s+([.,!?;:])", r"\1", text) #spaces before punctuation 
        return text

    def write_clean_jsonl(self, jsonl_name):

        base = Path("/Users/Bettina/side_quests/ap_style_app/data/")

        input_path = base/f'raw/{jsonl_name}.jsonl'
        output_path = base/f'cleaned/{jsonl_name}_cleaned.jsonl'

        with open(input_path, "r", encoding="utf-8") as file, \
            open(output_path, "w", encoding="utf-8") as out:

            for line in file:
                field = json.loads(line)

                for key in field.keys():
                    field[key] = self.clean_text(field[key])
                    print(f'value: {field[key]}')
                out.write(json.dumps(field, ensure_ascii=False) + "\n")

cleaner = cleanJsonl()
cleaner.write_clean_jsonl('2025-12-31')