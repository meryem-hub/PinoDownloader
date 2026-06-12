import requests
import re

def extract_pinterest_video(pin_url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(
            pin_url,
            headers=headers,
            timeout=20
        )

        html = response.text

        # Look for VideoObject contentUrl
        match = re.search(
            r'"contentUrl":"(https://[^"]+\.mp4)"',
            html
        )

        if match:
            return match.group(1).replace("\\/", "/")

        # Fallback: any mp4 URL
        match = re.search(
            r'https://[^"]+\.mp4',
            html
        )

        if match:
            return match.group(0)

        return None

    except Exception as e:
        print("Extractor error:", e)
        return None