import os
import re
import requests
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict
from urllib.parse import quote

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gpt_recommend_song(messages: List[Dict]) -> Dict:
    system_prompt = """
당신은 감성적인 챗봇이자 음악 큐레이터입니다.
사용자의 대화에서 감정을 파악하고, 필요할 때 곡을 한 곡 추천해 주세요.

반드시 다음 두 요소가 포함되도록 응답하세요:
- 자연스러운 공감 또는 안내 멘트
- 노래 제목과 아티스트를 문장 속에 자연스럽게 포함

예:
"그런 밤에는 '조지 - Boat' 같은 곡이 잘 어울려요."
또는:
"그 기분에는 백예린의 '그건 아마 우리의 잘못은 아닐 거야'를 추천해요."

※ 응답 형식은 자유롭게, 단 문장 중에 제목과 아티스트가 함께 포함되도록 하세요.
"""
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=full_messages,
        temperature=0.8,
        max_tokens=300,
    )

    return parse_song_recommendation(response.choices[0].message.content)

def parse_song_recommendation(text: str) -> Dict:
    result = {
        "reply": text.strip(),
        "title": "",
        "artist": "",
    }

    # Case 1: '아티스트 - 제목'
    match = re.search(r"[\"']?([^\n\-\–\"']+?)\s*[-\–]\s*([^\n\"']+?)[\"']?", text)

    # Case 2: "아티스트의 '제목'" 또는 "아티스트의 “제목”"
    if not match:
        match = re.search(r"(?:\b|\s)([가-힣a-zA-Z0-9]+)\s*의\s*[\"“']([^\"”']+)[\"”']", text)

    if match:
        artist = match.group(1).strip()
        title = match.group(2).strip()
        result["artist"] = artist
        result["title"] = title

        # ✅ YouTube 검색 요청 후 videoId 추출
        query = f"{artist} {title}"
        yt_data = search_youtube_video(query)
        if yt_data:
            result["videoId"] = yt_data["videoId"]
            result["url"] = f"https://www.youtube.com/watch?v={yt_data['videoId']}"

    return result

def search_youtube_video(query: str) -> Dict:
    search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(search_url, headers=headers, timeout=5)
        if response.status_code == 200:
            match = re.search(r"watch\?v=([a-zA-Z0-9_-]{11})", response.text)
            if match:
                video_id = match.group(1)
                return {"videoId": video_id}
    except Exception as e:
        print("❌ YouTube 검색 오류:", e)
    return {}
