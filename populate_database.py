import argparse
import os
import shutil
import pathlib
import json
import requests
# from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_community.document_loaders import JSONLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveJsonSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain.vectorstores.chroma import Chroma


API_PATH = "api_vector_db"
DATA_PATH = "data"
VECTOR_PATH = "main_vector_db"


def main():

    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Create (or update) the data store.
    if not pathlib.Path('/api_vector_db').exists():
        documents = load_documents()
        # chunks = split_documents(documents)
        add_to_api_vdb(documents)


# Define the metadata extraction function.
def metadata_func(record: dict, metadata: dict) -> dict:

    metadata["links"] = record.get("info_link_data")
    metadata["primary_name"] = record.get("primary_name")
    metadata["synonyms"] = record.get("synonyms")
    metadata["words"] = record.get("word_synonyms")
    metadata["id"] = record.get("key_id")

    return metadata

def load_documents():
    loader = JSONLoader(
    file_path='./data/clinical_tables.json',
    jq_schema='.[]',
    content_key="consumer_name",
    metadata_func=metadata_func
    )

    data = loader.load()
    return data


# def split_documents(documents: list[Document]):
#     splitter = RecursiveJsonSplitter(max_chunk_size=300)
#     json_chunks = splitter.split_json(json_data=json_data)
#     json_chunks[0]

#     return splitter.split_documents(documents)


def add_to_api_vdb(chunks: list[Document]):
    # Load the existing database.
    db = Chroma(
        persist_directory=API_PATH, embedding_function=get_embedding_function()
    )

def add_to_main_vdb(chunks: list[Document]):
    # Load the existing database.
    db = Chroma(
        persist_directory=VECTOR_PATH, embedding_function=get_embedding_function()
    )

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

    if os.path.exists(VECTOR_PATH):
        shutil.rmtree(VECTOR_PATH)


if __name__ == "__main__":
    main()
