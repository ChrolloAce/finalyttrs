from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptAvailable
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Any, Optional
import random
import time

# List of common user agents to rotate through
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
]

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

def get_transcript(video_id: str, retries: int = 3) -> List[Dict[str, Any]]:
    """
    Get the transcript for a YouTube video with retries and user-agent rotation.
    
    Args:
        video_id: The YouTube video ID
        retries: Number of retry attempts
        
    Returns:
        List of transcript segments with text and timestamp information
    """
    attempt = 0
    last_error = None
    
    while attempt < retries:
        try:
            # Select a random user agent
            user_agent = random.choice(USER_AGENTS)
            
            # Add a small delay between retries to avoid rate limiting
            if attempt > 0:
                time.sleep(2)
            
            # Try with different language options if available
            try:
                # First try with default language
                return YouTubeTranscriptApi.get_transcript(video_id, proxies=None)
            except (TranscriptsDisabled, NoTranscriptAvailable):
                # Then try with auto-generated transcripts
                return YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US', 'en-GB', 'es', 'fr', 'de'], proxies=None)
                
        except Exception as e:
            last_error = e
            attempt += 1
    
    # If all retries failed, raise the last error
    if video_id == "":
        raise ValueError("Empty video ID provided")
        
    raise Exception(f"Error fetching transcript after {retries} attempts: {str(last_error)}")

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