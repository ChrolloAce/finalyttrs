from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Any, Optional

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

def get_transcript(video_id: str) -> List[Dict[str, Any]]:
    """
    Get the transcript for a YouTube video.
    
    Args:
        video_id: The YouTube video ID
        
    Returns:
        List of transcript segments with text and timestamp information
    """
    try:
        return YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        raise Exception(f"Error fetching transcript: {str(e)}")

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