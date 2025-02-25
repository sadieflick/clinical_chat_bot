
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from chainlit.utils import mount_chainlit
from cl_http_body import RequestBody
from chainlit.message import Message

app = FastAPI()


@app.get("/")
def read_main():
    return RedirectResponse('/chainlit')


# TO DO: format as an API with endpoints for separate RAG processes

# @app.post('/process_prompt/')
# def rag_api(req_body: RequestBody):
#     return RedirectResponse(f'/llm_serialize/{req_body.content}')
    
# @app.get('/llm_serialize/{text}')
# def llm_serialize(text: str):
#     pass


# # Get either JSON or 
# @app.post('/similarity_search/{isText}')
# def similarity_search(isText = False):
#     # process json data for 
#     pass

# @app.post('/')

# @app.post('/send_response/')
# async def final_llm_response(message: Message):
#     return message.content


mount_chainlit(app=app, target="chainlit_app.py", path="/chainlit")



