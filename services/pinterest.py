import requests
import re


def extract_pinterest_video(url: str):
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=20)
        html = r.text

        match = re.search(r'"contentUrl":"(https://[^"]+\.mp4)"', html)
        if match:
            return match.group(1).replace("\\/", "/")


        match = re.search(r'https://[^"]+\.mp4', html)
        if match:
            return match.group(0)

        return None

    except Exception as e:
        print("Pinterest error:", e)
        return None