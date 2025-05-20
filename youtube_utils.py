from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Any, Optional
import random
import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# List of free proxies - in production, replace with paid reliable proxies
# Format: "http://ip:port" or "http://username:password@ip:port"
DEFAULT_PROXIES = [
    # Free proxies - replace with your own
    "http://204.157.240.53:999",
    "http://52.168.34.113:80",
    "http://169.55.89.6:80",
    "http://103.152.112.162:80",
    "http://168.119.119.107:8085",
]

# Get proxies from environment variable if available
PROXY_LIST = os.getenv("PROXY_LIST", "").split(",") if os.getenv("PROXY_LIST") else DEFAULT_PROXIES

def get_random_proxy():
    """Get a random proxy from the list."""
    return random.choice(PROXY_LIST) if PROXY_LIST else None

def extract_video_id(url: str) -> str:
    """
    Extract the video ID from a YouTube URL.
    
    Args:
        url: A YouTube URL in various possible formats
        
    Returns:
        The YouTube video ID
    """
    parsed_url = urlparse(url)
    
    # Format: youtube.com/watch?v=VIDEO_ID
    if parsed_url.netloc in ('youtube.com', 'www.youtube.com') and parsed_url.path == '/watch':
        return parse_qs(parsed_url.query).get('v', [''])[0]
    
    # Format: youtu.be/VIDEO_ID
    elif parsed_url.netloc == 'youtu.be':
        return parsed_url.path.lstrip('/')
    
    # Format: youtube.com/v/VIDEO_ID
    elif parsed_url.path.startswith('/v/'):
        return parsed_url.path.split('/')[2]
    
    # Format: youtube.com/embed/VIDEO_ID
    elif parsed_url.path.startswith('/embed/'):
        return parsed_url.path.split('/')[2]
    
    # If the input is just the video ID
    elif len(url.split()) == 1 and all(c.isalnum() or c == '_' or c == '-' for c in url):
        return url
    
    raise ValueError(f"Could not extract video ID from URL: {url}")

def get_transcript(video_id: str, max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    Get the transcript for a YouTube video with proxy rotation and retries.
    
    Args:
        video_id: The YouTube video ID
        max_retries: Maximum number of retry attempts
        
    Returns:
        List of transcript segments with text and timestamp information
    """
    errors = []
    
    for attempt in range(max_retries):
        try:
            proxy = get_random_proxy()
            
            if proxy:
                print(f"Attempt {attempt+1}/{max_retries} using proxy: {proxy}")
                proxies = {
                    "http": proxy,
                    "https": proxy.replace("http://", "https://") if proxy.startswith("http://") else proxy
                }
                
                # Use the proxy with YouTubeTranscriptApi
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id,
                    proxies=proxies
                )
                
                return transcript
            else:
                # Fallback to no proxy if none available
                return YouTubeTranscriptApi.get_transcript(video_id)
                
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            # These are permanent errors, no need to retry
            raise Exception(f"Error fetching transcript: {str(e)}")
        except Exception as e:
            errors.append(f"Attempt {attempt+1} error: {str(e)}")
            time.sleep(1)  # Wait before retrying
    
    # All retries failed
    error_message = "\n".join(errors)
    raise Exception(f"Failed to fetch transcript after {max_retries} attempts with different proxies:\n{error_message}")

def get_transcript_text(video_id: str) -> str:
    """
    Get the transcript text only (without timestamps) for a YouTube video.
    
    Args:
        video_id: The YouTube video ID
        
    Returns:
        The full transcript text as a single string
    """
    transcript_data = get_transcript(video_id)
    return " ".join([segment['text'] for segment in transcript_data])

def format_seconds_to_mmss(seconds: float) -> str:
    """
    Format seconds to MM:SS format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string in MM:SS format
    """
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes:02d}:{remaining_seconds:02d}"

def test_proxies():
    """
    Test all proxies and return working ones.
    """
    working_proxies = []
    for proxy in PROXY_LIST:
        try:
            proxies = {
                "http": proxy,
                "https": proxy.replace("http://", "https://") if proxy.startswith("http://") else proxy
            }
            response = requests.get("https://www.youtube.com", proxies=proxies, timeout=5)
            if response.status_code == 200:
                working_proxies.append(proxy)
                print(f"Proxy working: {proxy}")
        except Exception as e:
            print(f"Proxy failed: {proxy} - {str(e)}")
    
    return working_proxies 