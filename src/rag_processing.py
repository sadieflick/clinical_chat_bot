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

    # Validate relevance and remove unrelated search terms
    remove_unrelated_conditions(api_search_data, prompt_text)

    # Get data from weblinks, parse, chunk by web page, retain metadata
    api_response_data = fetchRelevantData(api_search_data)

    # Embed any new doc chunks into main vectorDB with appropriate doc metadata
    addEmbedChunks(api_response_data)

    # prepare document context for refined prompt
    context = getDocsFromLLMTerms(api_search_data)

    # Prepare final response with 'sources' (weblinks) appended to the LLM reply
    #    - uses similarity search, a prompt template, the original user prompt
    ragged_response = getRefinedResponse(prompt_text, context)

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

    try:
        json_object = json.loads(response_text)
        return json_object
    except json.JSONDecodeError as e:
         return f"Error decoding JSON: {e}"

    # prompt_template = ChatPromptTemplate.from_template("""
    # Please take the following text, verify that it is in syntactically correct json format, and if it is, 
    # just answer this prompt with 'valid', otherwise, please correct any errors and respond only with the exact data from the text, but with
    # correct json syntax / format. Please omit any next-line formatting.
    # {json}
    # """)
    # prompt = prompt_template.format(json=response_text)
    # model = OllamaLLM(model="llama3.2")
    # response_text = model.invoke(prompt)
    finally:
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
        # print(f'============= Condition: {condition['primary_name']}============')
        vectors: list[Document] = json_db.similarity_search_with_score(condition['primary_name'], k=5)

        # Store related, and add condition id to ids list
        for vector_tuple in vectors:
            vector = vector_tuple[0]
            related_vectors[vector.metadata['id']] = vector
            ids.append(vector.metadata['id'])
            
    # pprint(related_vectors)

    

    # print(f'========== json similarity search related_vectors ==========\n')
    # pprint(related_vectors)
    # print('\n===========================\n')
    

    return related_vectors

# Use LLM to check relevance of search terms and remove unrelated terms
def remove_unrelated_conditions(vectors: dict[Document], prompt_text) -> dict[Document]:
    context_data = {}
    keys = {}

    for key in vectors:
        vector = vectors[key]
        context_data[vector.metadata["primary_name"]] = vector.metadata["clinical_desc"]
        keys[vector.metadata["primary_name"]] = vector.metadata["id"]

    # Remove conditions that are assessed as unrelated based on general LLM training
    prompt_template = ChatPromptTemplate.from_template(GET_UNRELATED_INDEXES)
    prompt = prompt_template.format(prompt=prompt_text, related_conditions=context_data)
    model = OllamaLLM(model="llama3.2")
    response_text = model.invoke(prompt)

    removal_list = []
    if response_text != 'None':
        removal_list = response_text.split(', ')
    print(f'====== KEYS to REMOVE: {removal_list} =====')
    print(f'Original vectors: \n{[vectors[key].metadata['primary_name'] for key in vectors]}')

    for key in removal_list:
        condition_id = keys[key]
        vectors.pop(condition_id)

    print(f'NEW LIST: \n{[vectors[key].metadata['primary_name'] for key in vectors]}')

    return vectors

    

def fetchRelevantData(related_vectors: dict[Document]) -> dict[Document]:

    # Get ids of those docs already in the the vector db
    db = Chroma(persist_directory=MAIN_VECTOR_PATH, embedding_function=get_embedding_function())
    filter_dict = filter_dict = {"id": {"$in": list(related_vectors.keys())}}
    base_retriever = db.as_retriever(search_kwargs={'k': 10, 'filter': filter_dict})
    main_db = base_retriever.invoke('')
    v_ids = [vector.metadata['id'] for vector in main_db]

    docs = {}


    # Add only new docs to the vector DB
    for key, vector in related_vectors.items():
        vector_id = vector.metadata['id']
        if vector_id not in v_ids:
        
            # Get medical condition information from web links, preserving metadata
            vector = related_vectors[key]
            link = vector.metadata['links']

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
                    docs[vector.id] = Document(
                                page_content=content,
                                metadata=vector.metadata
                            )

    return docs

    

def addEmbedChunks(chunks: dict[Document], path: str=MAIN_VECTOR_PATH):

    print(f'=========== INFO DOCS FROM WEB: \n{[chunks[chunk].metadata['primary_name'] for chunk in chunks]}')
    
    # Load the existing database.
    db = Chroma(
        persist_directory=MAIN_VECTOR_PATH, embedding_function=get_embedding_function()
    )


    # # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_metadata = set()
    
    print(existing_items)

    # get a list of records to compare condition ids
    if len(existing_items['ids']):
        existing_metadata = set(existing_items)
    
    print(f"Number of existing documents in DB: {len(existing_metadata)}\n")
    print(f"==========METADATA LIST: \n{existing_metadata}")

    # Get list of duplicate records
    filter_dict = filter_dict = {"id": {"$in": list(chunks.keys())}}
    # dup_vectors = db.get(where=filter_dict, include=["metadatas"])
    dup_vectors = db.get_by_ids(list(chunks.keys()))

    print(f'===========DUPLICATE VECT: \n {dup_vectors}')
    

    # # Only add documents that don't exist in the DB.
    dup_keys = [doc.id for doc in dup_vectors]
    new_chunks = []
    new_chunk_ids = set()
    
    for key, chunk in chunks.items():
        chunk_id = chunk.id
        # print(chunk.metadata)
        if chunk_id not in dup_keys and chunk_id not in new_chunk_ids:
            new_chunks.append(chunk)
            new_chunk_ids.add(chunk_id)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("✅ No new documents to add")

def getDocsFromLLMTerms(docs: dict[Document]) -> dict:
    print(f'========= SEARCH key ids AT FETCH ========\n {docs.keys()}')

    # Load Doc DB
    db = Chroma(
    persist_directory=MAIN_VECTOR_PATH, embedding_function=get_embedding_function()
    )
    
    # Get corresponding docs to create context
    filter_dict = filter_dict = {"id": {"$in": list(docs.keys())}}
    context_docs = db.get(where=filter_dict, include=["documents", "metadatas"], limit=10)

    print(f'======== getting docs... : \n{[md for md in context_docs['ids']]} =========')

    return context_docs

# Ready doc context for prompt template as string
def getRefinedResponse(query_text, data=None) -> str:

    print(f'======== FINAL CONTEXT DOCS METADATA: \n{[md['primary_name'] for md in data['metadatas']]} =========')

    context_text = "\n\n---\n\n".join([doc for doc in data['documents']])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)

    model = OllamaLLM(model="llama3.2")
    response_text = model.invoke(prompt)

    sources = [doc.get("links", None) for doc in data['metadatas']]
    formatted_response = f"Response: {response_text}\n\nThese are the sources I used in answering your question: \n{sources}"
    print(formatted_response)
    
    return formatted_response



if __name__ == "__main__":
    main()
