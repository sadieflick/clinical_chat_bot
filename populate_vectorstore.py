import os
import shutil
from uuid import uuid4
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveJsonSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_community.vectorstores.chroma import Chroma

import logging
logger = logging.getLogger(__name__)

# TO DO: change to .env variables or config
JSON_VECTOR_PATH = "json_vector_db"
DATA_PATH = "./data/clinical_tables.json"
MAIN_VECTOR_PATH = "main_vector_db"


# Convert JSON list fields as strings for metadata in vectorstore
def flatten_links(nested_list):
    for i in range(len(nested_list)):
        print(nested_list[i])
        if isinstance(nested_list[i], list):
            nested_list[i] = ": ".join(nested_list[i])


# Define the metadata extraction function.
def metadata_func(record: dict, metadata: dict) -> dict:

    links = record.get("info_link_data")
    flatten_links(links)
    links = ", ".join(links)

    synonyms = record.get("synonyms")
    flatten_links(synonyms)
    synonyms = ", ".join(synonyms)

    metadata["links"] = links
    metadata["primary_name"] = record.get("primary_name")
    metadata["synonyms"] = synonyms
    metadata["words"] = record.get("word_synonyms")
    metadata["id"] = record.get("key_id")

    return metadata

# Put json data into a list of langchain Documents
def load_documents() -> list[Document]:
    loader = JSONLoader(
    file_path=DATA_PATH,
    jq_schema='.[]',
    content_key="consumer_name",
    metadata_func=metadata_func
    )

    data = loader.load()

    message = f"Loading JSON data into langchain Documents. \n Example document data: \n {data[0]}"
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


#     # Calculate Page IDs.
#     chunks_with_ids = calculate_chunk_ids(chunks)

#     # Add or Update the documents.
#     existing_items = db.get(include=[])  # IDs are always included by default
#     existing_ids = set(existing_items["ids"])
#     print(f"Number of existing documents in DB: {len(existing_ids)}")

#     # Only add documents that don't exist in the DB.
#     new_chunks = []
#     for chunk in chunks_with_ids:
#         if chunk.metadata["id"] not in existing_ids:
#             new_chunks.append(chunk)

#     if len(new_chunks):
#         print(f"👉 Adding new documents: {len(new_chunks)}")
#         new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
#         db.add_documents(new_chunks, ids=new_chunk_ids)
#         db.persist()
#     else:
#         print("✅ No new documents to add")


# def calculate_chunk_ids(chunks):

#     # This will create IDs like "data/monopoly.pdf:6:2"
#     # Page Source : Page Number : Chunk Index

#     last_page_id = None
#     current_chunk_index = 0

#     for chunk in chunks:
#         source = chunk.metadata.get("source")
#         page = chunk.metadata.get("page")
#         current_page_id = f"{source}:{page}"

#         # If the page ID is the same as the last one, increment the index.
#         if current_page_id == last_page_id:
#             current_chunk_index += 1
#         else:
#             current_chunk_index = 0

#         # Calculate the chunk ID.
#         chunk_id = f"{current_page_id}:{current_chunk_index}"
#         last_page_id = current_page_id

#         # Add it to the page meta-data.
#         chunk.metadata["id"] = chunk_id

#     return chunks


def clear_database():

    if os.path.exists(MAIN_VECTOR_PATH):
        shutil.rmtree(MAIN_VECTOR_PATH)


if __name__ == "__main__":
    main()
