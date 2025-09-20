from fastapi import FastAPI
from pydantic import BaseModel
import time
import uvicorn

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[Message]

app = FastAPI(title="Super-Gemini Local Model Runner")

@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    dummy_response_content = "This is a placeholder response from the local Super-Gemini model runner."
    return {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": dummy_response_content}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
