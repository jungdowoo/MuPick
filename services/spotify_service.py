import requests
import os
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_access_token():
    auth_response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    )
    if auth_response.status_code != 200:
        return None
    return auth_response.json().get("access_token")

# 🔧 새로 추가: 제목 + 아티스트로 Spotify 검색
def search_song_by_title_artist(title: str, artist: str):
    access_token = get_access_token()
    if not access_token:
        return None

    headers = { "Authorization": f"Bearer {access_token}" }
    query = f'track:{title} artist:{artist}'

    params = {
        "q": query,
        "type": "track",
        "limit": 5
    }

    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)

    if response.status_code != 200:
        print("🔴 Spotify 검색 실패:", response.text)
        return None

    items = response.json().get("tracks", {}).get("items",[])

    # ✅ preview_url이 있는 곡만 선택
    for item in items:
        preview_url = item.get("preview_url")
        if preview_url:  # ✅ 미리듣기 가능한 곡만 리턴
            return {
                "title": item["name"],
                "artist": item["artists"][0]["name"],
                "url": item["external_urls"]["spotify"],
                "preview_url": preview_url
            }

    print("⚠️ preview_url이 있는 곡이 없습니다.")
    return None
