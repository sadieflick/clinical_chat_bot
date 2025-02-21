from langchain_community.document_loaders import JSONLoader
from pathlib import Path
from pprint import pprint


# Define the metadata extraction function.
def metadata_func(record: dict, metadata: dict) -> dict:

    metadata["links"] = record.get("info_link_data")
    metadata["primary_name"] = record.get("primary_name")
    metadata["synonyms"] = record.get("synonyms")
    metadata["words"] = record.get("word_synonyms")

    return metadata


loader = JSONLoader(
    file_path='./data/clinical_tables.json',
    jq_schema='.[]',
    content_key="consumer_name",
    metadata_func=metadata_func
)

data = loader.load()
pprint(data[0])