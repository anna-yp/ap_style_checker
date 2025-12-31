from langchain_community.document_loaders import JSONLoader

class Ingest:
    def jsonl_ingest(self, docs):
      '''uses langchain loaders'''
      loader = JSONLoader(
          file_path="/Users/Bettina/side_quests/ap_style_app/data/cleaned/2025-12-31_cleaned.jsonl",
          jq_schema=".",
          text_content=False,
          json_lines=True,
      )

      docs = loader.load()
      return docs

