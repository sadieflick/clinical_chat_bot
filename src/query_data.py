import argparse
from templates import PROMPT_TEMPLATE, TO_JSON_TEMPLATE
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from get_embedding_function import get_embedding_function

JSON_VECTOR_PATH = "api_vector_db"
DATA_PATH = "data"
MAIN_VECTOR_PATH = "main_vector_db"


# def main():
#     # Create CLI.
#     parser = argparse.ArgumentParser()
#     parser.add_argument("query_text", type=str, help="The query text.")
#     args = parser.parse_args()
#     query_text = args.query_text
#     query_rag(query_text)


def query_rag(query_text: str):


    # Prepare vector storage access.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=JSON_VECTOR_PATH, embedding_function=embedding_function)

    # Get relevant conditions from question concerning initial condition details
    prompt_template = ChatPromptTemplate.from_template(TO_JSON_TEMPLATE)
    prompt = prompt_template.format(question=query_text)
    model = Ollama(model="llama3.2")
    response_text = model.invoke(prompt)

    print(f"============= Llama Response:\n{response_text} ==============")

    # # Search the DB.
    # results = db.similarity_search_with_score(query_text, k=5)

    # context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    # prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    # prompt = prompt_template.format(context=context_text, question=query_text)
    # # print(prompt)

    # model = Ollama(model="llama3.2")
    # response_text = model.invoke(prompt)

    # sources = [doc.metadata.get("id", None) for doc, _score in results]
    # formatted_response = f"Response: {response_text}\nSources: {sources}"
    # print(formatted_response)
    return response_text


if __name__ == "__main__":
    main()
