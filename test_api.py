import requests
import json
import argparse
import sys

def test_api(base_url, youtube_url):
    """
    Test all endpoints of the YouTube Forever API
    """
    print(f"Testing API at {base_url} with YouTube URL: {youtube_url}")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print("\n✅ Root Endpoint:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"\n❌ Root Endpoint Error: {str(e)}")
    
    # Test transcript endpoint
    try:
        response = requests.get(f"{base_url}/transcript", params={"url": youtube_url})
        data = response.json()
        print("\n✅ Transcript Endpoint:")
        print(f"Video ID: {data['video_id']}")
        print(f"Transcript length: {len(data['transcript'])} segments")
        print(f"First 2 segments: {json.dumps(data['transcript'][:2], indent=2)}")
    except Exception as e:
        print(f"\n❌ Transcript Endpoint Error: {str(e)}")
    
    # Test text endpoint
    try:
        response = requests.get(f"{base_url}/text", params={"url": youtube_url})
        data = response.json()
        print("\n✅ Text Endpoint:")
        print(f"Video ID: {data['video_id']}")
        text_preview = data['text'][:100] + "..." if len(data['text']) > 100 else data['text']
        print(f"Text preview: {text_preview}")
    except Exception as e:
        print(f"\n❌ Text Endpoint Error: {str(e)}")
    
    # Test summary endpoint
    try:
        response = requests.get(f"{base_url}/summary", params={"url": youtube_url, "max_words": 50})
        data = response.json()
        print("\n✅ Summary Endpoint:")
        print(f"Video ID: {data['video_id']}")
        print(f"Summary: {data['summary']}")
    except Exception as e:
        print(f"\n❌ Summary Endpoint Error: {str(e)}")
    
    # Test tags endpoint
    try:
        response = requests.get(f"{base_url}/tags", params={"url": youtube_url, "max_tags": 5})
        data = response.json()
        print("\n✅ Tags Endpoint:")
        print(f"Video ID: {data['video_id']}")
        print(f"Tags: {data['tags']}")
    except Exception as e:
        print(f"\n❌ Tags Endpoint Error: {str(e)}")
    
    # Test topics endpoint
    try:
        response = requests.get(f"{base_url}/topics", params={"url": youtube_url})
        data = response.json()
        print("\n✅ Topics Endpoint:")
        print(f"Video ID: {data['video_id']}")
        print(f"Topics: {json.dumps(data['topics'], indent=2)}")
    except Exception as e:
        print(f"\n❌ Topics Endpoint Error: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the YouTube Forever API")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--youtube", default="https://www.youtube.com/watch?v=dQw4w9WgXcQ", 
                        help="YouTube URL to test with")
    
    args = parser.parse_args()
    test_api(args.url, args.youtube) 