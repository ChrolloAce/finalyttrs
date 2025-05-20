import requests
import json
import re
import logging
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YouTubeTranscriptFetcher:
    """
    A class to fetch YouTube video transcripts directly using requests,
    bypassing some of the limitations of youtube-transcript-api.
    """
    
    @staticmethod
    def fetch_transcript(video_id: str) -> List[Dict[str, Any]]:
        """
        Get the transcript for a YouTube video by directly accessing YouTube's API.
        
        Args:
            video_id: The YouTube video ID
            
        Returns:
            List of transcript segments with text and timestamp information
        """
        logger.info(f"Attempting to fetch transcript with direct method for video ID: {video_id}")
        
        # Get the video page first
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        try:
            response = requests.get(video_url, headers=headers)
            response.raise_for_status()
            
            # Extract the ytInitialPlayerResponse from the HTML
            player_response_match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', response.text)
            
            if not player_response_match:
                logger.error("Could not find player response in YouTube page")
                raise Exception("Could not extract player data from YouTube")
                
            player_response_text = player_response_match.group(1)
            player_response = json.loads(player_response_text)
            
            # Check if captions are available
            if 'captions' not in player_response or 'playerCaptionsTracklistRenderer' not in player_response['captions']:
                logger.error("No captions available in player response")
                raise Exception("This video does not have captions available")
            
            # Get the captions track URL
            captions_renderer = player_response['captions']['playerCaptionsTracklistRenderer']
            
            if 'captionTracks' not in captions_renderer or not captions_renderer['captionTracks']:
                logger.error("No caption tracks found")
                raise Exception("No caption tracks available for this video")
            
            # Prefer English captions if available, otherwise use the first available
            caption_track = None
            for track in captions_renderer['captionTracks']:
                if track.get('languageCode') == 'en':
                    caption_track = track
                    break
            
            if not caption_track:
                caption_track = captions_renderer['captionTracks'][0]
            
            base_url = caption_track['baseUrl']
            
            # Fetch the transcript data
            logger.info(f"Fetching transcript from URL: {base_url}")
            transcript_response = requests.get(base_url + '&fmt=json3')
            transcript_response.raise_for_status()
            
            transcript_data = transcript_response.json()
            
            # Process the transcript data into our standard format
            formatted_transcript = []
            
            if 'events' in transcript_data:
                for event in transcript_data['events']:
                    if 'segs' in event:
                        text_parts = []
                        for seg in event['segs']:
                            if 'utf8' in seg:
                                text_parts.append(seg['utf8'])
                        
                        if text_parts:
                            start_time = event.get('tStartMs', 0) / 1000.0
                            duration = event.get('dDurationMs', 0) / 1000.0
                            
                            formatted_transcript.append({
                                'text': ' '.join(text_parts).strip(),
                                'start': start_time,
                                'duration': duration
                            })
            
            if not formatted_transcript:
                logger.error("Failed to parse transcript data")
                raise Exception("Failed to parse the transcript data")
            
            logger.info(f"Successfully fetched transcript with {len(formatted_transcript)} segments")
            return formatted_transcript
            
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Network error when fetching transcript: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise Exception(f"Failed to parse YouTube response: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise Exception(f"Error fetching transcript: {str(e)}") 