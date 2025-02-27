import argparse
import json
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from templates import *
from langchain_chroma.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain.schema.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from get_embedding_function import get_embedding_function
from populate_vectorstore import load_documents

JSON_VECTOR_PATH = "../json_vector_db"
DATA_PATH = "data"
MAIN_VECTOR_PATH = "main_vector_db"

def getResponse(prompt_text: str):

    # Get guesses for relevant json vectors
    llm_json = jsonifyPrompt(prompt_text)

    # Return relevant dictionaries (vector similarity)
    api_search_data = jsonSimilaritySearch(llm_json)

    # Get data from weblinks, parse, chunk by web page, retain metadata
    api_response_data = fetchRelevantData(api_search_data)
    # if len(api_response_data): print(api_response_data[0])
    # else: print("-----------------Did not fetch any data")

    # Embed doc chunks into main vectorDB with appropriate doc metadata
    addEmbedChunks(api_response_data)

    # Prepare final response with 'sources' (weblinks) appended to the LLM reply
    #    - uses similarity search, a prompt template, the original user prompt
    ragged_response = getRefinedResponse(prompt_text)

    return ragged_response



def jsonifyPrompt(prompt_text: str):

    # Get relevant conditions from question concerning initial condition details
    prompt_template = ChatPromptTemplate.from_template(TO_JSON_TEMPLATE)
    prompt = prompt_template.format(question=prompt_text)
    model = OllamaLLM(model="llama3.2")
    response_text = model.invoke(prompt)

    print(f'========== jsonified prompt ==========\n')
    print(prompt_text)
    pprint(response_text)
    print('\n===========================\n')
    
    return response_text

    
def jsonSimilaritySearch(response_text: str) -> dict[Document]:

    parsed_data = json.loads(response_text)
    related_vectors = {}
    ids = []

    # Prepare vector storage access.
    embedding_function = get_embedding_function()
    json_db = Chroma(persist_directory=JSON_VECTOR_PATH, embedding_function=embedding_function)

    # Get all related json Document vectors
    for condition in parsed_data['conditions']:
        print(f'============= Condition: {condition['primary_name']}============')
        vectors: list[Document] = json_db.similarity_search_with_score(condition['primary_name'], k=5)

        # Store related, and add condition id to ids list
        for vector_tuple in vectors:
            vector = vector_tuple[0]
            related_vectors[vector.metadata['id']] = vector
            ids.append(vector.metadata['id'])
            
    # pprint(related_vectors)

    db = Chroma(persist_directory=MAIN_VECTOR_PATH, embedding_function=embedding_function)
    filter_dict = filter_dict = {"id": {"$in": ids}}
    base_retriever = db.as_retriever(search_kwargs={'k': 10, 'filter': filter_dict})
    main_db = base_retriever.invoke('')

    print(main_db[0].metadata['id'])

    for duplicate_vector in main_db:
        dup_id = duplicate_vector.metadata['id']
        if dup_id in related_vectors:
            related_vectors.pop(dup_id)

    print(f'========== json similarity search related_vectors ==========\n')
    pprint(related_vectors)
    print('\n===========================\n')

    return related_vectors

def fetchRelevantData(vectors: dict[Document]) -> list[Document]:

    
    # Get medical condition information from web links, preserving metadata
    docs = []

    for key in vectors:

        # get html page
        vector = vectors[key]
        link = vector.metadata['links']
        # print(link)
        if len(link):
            response = requests.get(link)

            # parse for summary section
            if response.status_code == 200:
                print("response is 200")
                soup = BeautifulSoup(response.text, 'html.parser')
                # section = soup.find(id="topsum_section")
                section = soup.article
                content = section.get_text() if section else soup.get_text()

                # add article and meta data
                docs.append(Document(
                            page_content=content,
                            metadata={"source": link} | vector.metadata
                        ))

    return docs
    

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

# def chunkRawRespDocs(resp: list[dict]) -> list[Document]:

#     pass

def addEmbedChunks(chunks: list[Document], path: str=MAIN_VECTOR_PATH):
    
    # Load the existing database.
    db = Chroma(
        persist_directory=MAIN_VECTOR_PATH, embedding_function=get_embedding_function()
    )


    # # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # # Only add documents that don't exist in the DB.
    new_chunks = []
    new_chunk_ids = set()
    for chunk in chunks:
        chunk_id = chunk.metadata["id"]
        if chunk_id not in existing_ids and chunk_id not in new_chunk_ids:
            new_chunks.append(chunk)
            new_chunk_ids.add(chunk_id)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("✅ No new documents to add")

# Ready context for template as string (optional 2nd sim search, chunks back to str, adds metadata)
def getRefinedResponse(query_text) -> str:

    # Load the existing database.
    db = Chroma(
        persist_directory=MAIN_VECTOR_PATH, embedding_function=get_embedding_function()
    )
    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)

    model = OllamaLLM(model="llama3.2")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("links", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    
    return formatted_response

# def getRefinedResponse(prompt: str, context: str, static_template=PROMPT_TEMPLATE):
#     # call LLM with template which adds weblink references, 
#     # other metadata and appropriate constraints
#     pass



if __name__ == "__main__":
    main()
