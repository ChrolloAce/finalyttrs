from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Any, Optional
import logging
from proxy_utils import proxy_manager
from yt_transcript_proxy import transcript_fetcher
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a static list of proxies as backup in case the ProxyScrape API fails
PROXY_LIST = [
    "159.65.69.186:9300",
    "167.71.5.83:3128",
    "178.128.177.142:8080",
    "139.59.1.14:3128",
    "165.22.6.221:8080",
    "159.203.61.169:3128",
    "157.230.177.3:8888"
]

def test_proxies(url: str = "https://www.youtube.com") -> List[str]:
    """
    Test which proxies in the PROXY_LIST are currently working.
    
    Args:
        url: The URL to test the proxies against
        
    Returns:
        List of working proxy strings
    """
    working_proxies = []
    
    for proxy_str in PROXY_LIST:
        proxy = {
            "http": f"http://{proxy_str}",
            "https": f"http://{proxy_str}"
        }
        
        try:
            logger.info(f"Testing proxy: {proxy_str}")
            response = requests.get(url, proxies=proxy, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"Proxy {proxy_str} is working")
                working_proxies.append(proxy_str)
            else:
                logger.warning(f"Proxy {proxy_str} returned status code: {response.status_code}")
        except Exception as e:
            logger.warning(f"Proxy {proxy_str} failed: {str(e)}")
    
    logger.info(f"Found {len(working_proxies)} working proxies out of {len(PROXY_LIST)}")
    return working_proxies

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

def _fetch_transcript_with_proxy(video_id: str, proxy: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    """
    Internal function to fetch transcript with optional proxy.
    
    Args:
        video_id: The YouTube video ID
        proxy: Optional proxy dictionary to use
        
    Returns:
        List of transcript segments with text and timestamp information
    """
    try:
        # Use our custom transcript fetcher with proxy support
        return transcript_fetcher.get_transcript(video_id, proxy)
    except Exception as e:
        logger.error(f"Custom transcript fetcher failed: {str(e)}")
        # Fallback to original method if our custom fetcher fails
        try:
            logger.info("Falling back to original YouTubeTranscriptApi...")
            return YouTubeTranscriptApi.get_transcript(video_id)
        except Exception as fallback_e:
            raise Exception(f"Both transcript fetching methods failed. Error: {str(fallback_e)}")

def get_transcript(video_id: str) -> List[Dict[str, Any]]:
    """
    Get the transcript for a YouTube video with proxy rotation if needed.
    
    Args:
        video_id: The YouTube video ID
        
    Returns:
        List of transcript segments with text and timestamp information
    """
    try:
        # Use proxy rotation for fetching transcript
        result, used_proxy = proxy_manager.execute_with_proxy_rotation(
            _fetch_transcript_with_proxy, 
            video_id
        )
        
        if used_proxy:
            logger.info(f"Successfully fetched transcript with proxy: {used_proxy}")
        else:
            logger.info("Successfully fetched transcript with direct connection")
            
        return result
    except Exception as e:
        logger.error(f"Failed to fetch transcript for video ID {video_id}: {str(e)}")
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