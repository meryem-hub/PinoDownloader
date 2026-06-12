import requests

def extract_tiktok_video(url):
    try:
        response = requests.get(
            f"https://tikwm.com/api/",
            params={"url": url},
            timeout=15
        )
        
        data = response.json()
        
        video_url = data.get('data', {}).get('play')
        
        return video_url
        
    except Exception as e:
        print("TikTok error:", e)
        return None