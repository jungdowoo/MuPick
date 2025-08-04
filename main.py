
from typing import Dict, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel



from services.gpt_service import gpt_recommend_song
from services.youtube_service import search_youtube_video

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    messages: List[Dict]

@app.post("/chat")
async def chat(request: ChatRequest):
    print("/chat 호출됨")


    gpt_result = gpt_recommend_song(request.messages)
    print("GPT 응답:", gpt_result)

    track_data = None
    if gpt_result["title"] and gpt_result["artist"]:

        track_data = search_youtube_video(gpt_result["title"], gpt_result["artist"])
        print(" 유튜브 트랙:", track_data)

        if track_data:
            track_data["title"] = gpt_result["title"]
            track_data["artist"] = gpt_result["artist"]

    return {
        "reply": gpt_result["reply"],
        "track": track_data
    }
