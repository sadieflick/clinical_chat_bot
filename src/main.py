
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from chainlit.utils import mount_chainlit
app = FastAPI()


@app.get("/")
def read_main():
    return RedirectResponse('/chainlit')

mount_chainlit(app=app, target="chainlit_app.py", path="/chainlit")



