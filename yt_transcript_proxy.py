import requests
import json
import re
from typing import Dict, List, Any, Optional
import logging
import time
import random

logger = logging.getLogger(__name__)

class ProxyEnabledTranscriptFetcher:
    """A custom implementation of YouTube transcript fetching with proxy support."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        })
    
    def get_transcript(self, video_id: str, proxy: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Get transcript for a YouTube video with optional proxy support.
        
        Args:
            video_id: YouTube video ID
            proxy: Optional proxy configuration dictionary
            
        Returns:
            List of transcript segments
        """
        try:
            # If proxy is provided, set it in the session
            if proxy:
                self.session.proxies.update(proxy)
                logger.info(f"Using proxy: {proxy.get('http', 'unknown')}")
            else:
                # Clear any previously set proxies
                self.session.proxies.clear()
            
            # First, fetch the YouTube page to get the required data
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            response = self.session.get(youtube_url, timeout=15)
            
            if response.status_code != 200:
                raise Exception(f"Failed to fetch YouTube page, status code: {response.status_code}")
            
            # Extract the required data from the page
            html_content = response.text
            
            # Extract player_response from the HTML
            player_response_match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', html_content)
            if not player_response_match:
                raise Exception("Could not find player response data in the YouTube page")
                
            player_response_text = player_response_match.group(1)
            try:
                player_response = json.loads(player_response_text)
            except json.JSONDecodeError:
                raise Exception("Failed to parse player response JSON")
                
            # Check if captions data exists
            if 'captions' not in player_response or 'playerCaptionsTracklistRenderer' not in player_response['captions']:
                raise Exception("No captions found for this video")
                
            captions_renderer = player_response['captions']['playerCaptionsTracklistRenderer']
            
            if 'captionTracks' not in captions_renderer or not captions_renderer['captionTracks']:
                raise Exception("No caption tracks found for this video")
                
            # Find the first caption track (usually the default one)
            caption_track = captions_renderer['captionTracks'][0]
            caption_url = caption_track['baseUrl']
            
            # Add parameter to get json format
            if '?' in caption_url:
                caption_url += '&fmt=json3'
            else:
                caption_url += '?fmt=json3'
                
            # Fetch the actual transcript data
            transcript_response = self.session.get(caption_url, timeout=15)
            
            if transcript_response.status_code != 200:
                raise Exception(f"Failed to fetch transcript data, status code: {transcript_response.status_code}")
                
            transcript_data = transcript_response.json()
            
            # Parse the transcript data into the expected format
            transcript_segments = []
            
            if 'events' in transcript_data:
                for event in transcript_data['events']:
                    if 'segs' in event and 'tStartMs' in event:
                        text = ''.join(seg.get('utf8', '') for seg in event['segs'] if 'utf8' in seg)
                        if text:
                            segment = {
                                'text': text.strip(),
                                'start': event['tStartMs'] / 1000,  # Convert to seconds
                                'duration': (event.get('dDurationMs', 0) / 1000) if 'dDurationMs' in event else 0
                            }
                            transcript_segments.append(segment)
            
            if not transcript_segments:
                raise Exception("Could not parse any transcript segments from the data")
                
            return transcript_segments
            
        except Exception as e:
            logger.error(f"Error fetching transcript with proxy: {str(e)}")
            raise Exception(f"Error fetching transcript: {str(e)}")

    def get_transcript_text(self, video_id: str, proxy: Optional[Dict[str, str]] = None) -> str:
        """
        Get transcript text only for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            proxy: Optional proxy configuration dictionary
            
        Returns:
            Transcript text as a single string
        """
        segments = self.get_transcript(video_id, proxy)
        return " ".join(segment['text'] for segment in segments)

# Create a global instance
transcript_fetcher = ProxyEnabledTranscriptFetcher() 