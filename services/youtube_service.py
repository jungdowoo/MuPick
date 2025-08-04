import os
import requests
from dotenv import load_dotenv


load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def search_youtube_video(title:str, artist:str):
    query = f"{title} {artist}"
    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q":query,
        "type": "video",
        "maxResults":1,
        "key":YOUTUBE_API_KEY
    }

    res = requests.get(url, params=params)
    if res.status_code != 200:
        print("유튜브 검색실패:",res.text)
        return None

    items =res.json().get("items", [])
    if not items:
        return None

    video = items[0]
    video_id = video["id"]["videoId"]
    snippet = video["snippet"]

    return {
        "title":snippet["title"],
        "channel": snippet["channelTitle"],
        "videoId":video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "thumbnail":snippet["thumbnails"]["high"]["url"]
    }