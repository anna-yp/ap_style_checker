from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import time 
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.build_vectorstore import JsonlVectorPipeline
from rag.search import Prompt

app = FastAPI()

templates = Jinja2Templates(directory="templates")

class ChatPayload(BaseModel):
      message: str


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="home.html"
    )

@app.get("/chat", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="chat.html"
    )

@app.post("/send_chat")
def chat_static(payload: ChatPayload):
    message = payload.message

    prompt = Prompt()
    response = prompt.prompt_gpt(message)
    print(message)

    answer_parts = []
    for item in response.output:
        if item.type == "message" and item.role == "assistant":
            for part in item.content:
                if part.type == "output_text":
                    answer_parts.append(part.text)
    answer_text = "".join(answer_parts)

    print(answer_text)
    return {"answer": answer_text}