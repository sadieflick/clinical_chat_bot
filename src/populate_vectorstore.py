import os
import shutil
from pprint import pprint
from uuid import uuid4
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveJsonSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma

import logging
logger = logging.getLogger(__name__)

# TO DO: change to .env variables or config
JSON_VECTOR_PATH = "../json_vector_db"
DATA_PATH = "../data/clinical_tables.json"
MAIN_VECTOR_PATH = "../main_vector_db"


# Convert JSON list fields as strings for metadata in vectorstore
def flatten_links(nested_list):
    for i in range(len(nested_list)):
        nested_list[i] = nested_list[i][0]
    return nested_list

# Define the metadata extraction function.
def load_clinical_tables_metadata(record: dict, metadata: dict) -> dict:

    links = record.get("info_link_data")
    links = '' if len(links) == 0 else flatten_links(links)
    
    links = ", ".join(links)

    synonyms = record.get("synonyms")
    # flatten_list(synonyms)
    synonyms = ", ".join(synonyms)

    metadata["links"] = links
    metadata["primary_name"] = record.get("primary_name")
    metadata["synonyms"] = synonyms
    metadata["words"] = record.get("word_synonyms")
    metadata["id"] = record.get("key_id")
    
    if record.get('term_icd9_text'):
        metadata['clinical_desc'] = record.get('term_icd9_text')
    else:
        metadata["clinical_desc"] = ''

    return metadata

# Put json data into a list of langchain Documents
def load_documents(metadata_func=load_clinical_tables_metadata) -> list[Document]:
    loader = JSONLoader(
    file_path=DATA_PATH,
    jq_schema='.[]',
    content_key="consumer_name",
    metadata_func=metadata_func
    )

    data = loader.load()

    message = f"Loading JSON data into langchain Documents. \n Example document data: \n {data[20]}"
    print(message)
    logger.info(message)

    return data


# def split_documents(documents: list[Document]):
#     splitter = RecursiveJsonSplitter(max_chunk_size=300)
#     json_chunks = splitter.split_json(json_data=json_data)
#     print(json_chunks[0])

#     return splitter.split_documents(documents)


def add_to_json_vectors(documents: list[Document]):
    # Load the existing database.
    vector_store = Chroma(
        persist_directory=JSON_VECTOR_PATH, embedding_function=get_embedding_function()
    )
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=uuids)

    message = f"Adding documents and UUIDs to json vector storage. \nExample uuid: {uuids[0]}, {uuids[1]}"
    print(message)
    logger.info(message)

def add_to_main_vdb(documents: list[Document]):
    # Load the existing database.
    vector_store = Chroma(
        persist_directory=MAIN_VECTOR_PATH, embedding_function=get_embedding_function()
    )
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=uuids)



def clear_database():
    if os.path.exists(MAIN_VECTOR_PATH):
        shutil.rmtree(MAIN_VECTOR_PATH)


if __name__ == "__main__":
    main()
