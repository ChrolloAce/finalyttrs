import os
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def generate_summary(transcript: str, max_words: int = 100) -> str:
    """
    Generate a concise summary of the transcript.
    
    Args:
        transcript: The video transcript text
        max_words: Maximum number of words in the summary
        
    Returns:
        A summary of the transcript
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant that summarizes YouTube videos. Create a concise summary (maximum {max_words} words)."},
                {"role": "user", "content": transcript}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Error generating summary: {str(e)}")

def generate_tags(transcript: str, max_tags: int = 10) -> List[str]:
    """
    Generate relevant tags for the video content.
    
    Args:
        transcript: The video transcript text
        max_tags: Maximum number of tags to generate
        
    Returns:
        A list of relevant tags
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant that generates relevant tags for YouTube videos. Create a list of up to {max_tags} tags that best represent the main topics and themes in this video. Return only a Python list of strings with no additional text."},
                {"role": "user", "content": transcript}
            ]
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse as a Python list if it's formatted that way
        try:
            if content.startswith('[') and content.endswith(']'):
                tags = eval(content)
                if isinstance(tags, list):
                    return tags
            
            # Otherwise, split by commas or newlines if not in list format
            if ',' in content:
                return [tag.strip() for tag in content.split(',') if tag.strip()]
            else:
                return [tag.strip() for tag in content.split('\n') if tag.strip()]
        except:
            # Fallback to simple split by commas
            return [tag.strip() for tag in content.split(',') if tag.strip()]
            
    except Exception as e:
        raise Exception(f"Error generating tags: {str(e)}")

def generate_topic_timestamps(transcript_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate topic breakdowns with timestamps.
    
    Args:
        transcript_data: The full transcript data including timestamps
        
    Returns:
        A list of topics with their timestamp information
    """
    # Prepare transcript with timestamps
    formatted_transcript = ""
    for item in transcript_data:
        time_str = f"{item['start']:.2f}s"
        formatted_transcript += f"[{time_str}] {item['text']}\n"
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes video transcripts. Identify the main topics or segments in this transcript and when they occur. Format your response as a JSON array of objects with 'topic', 'start_seconds', and 'start_time' (in MM:SS format) fields. Do not include any explanatory text, just the JSON."},
                {"role": "user", "content": formatted_transcript}
            ]
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        try:
            # Find JSON array in the content if there's other text
            if content.find('[') >= 0 and content.rfind(']') > content.find('['):
                json_str = content[content.find('['):content.rfind(']')+1]
                topics = json.loads(json_str)
            else:
                topics = json.loads(content)
            
            return topics
        except json.JSONDecodeError:
            # If JSON parsing fails, use a more structured prompt for a second attempt
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes video transcripts. Your output should be ONLY a valid JSON array with no additional text."},
                    {"role": "user", "content": "Identify 3-7 main topics or segments in this transcript and when they occur. Format your response ONLY as a JSON array of objects with 'topic', 'start_seconds', and 'start_time' (in MM:SS format) fields.\n\n" + formatted_transcript}
                ]
            )
            content = response.choices[0].message.content.strip()
            
            if content.find('[') >= 0 and content.rfind(']') > content.find('['):
                json_str = content[content.find('['):content.rfind(']')+1]
                return json.loads(json_str)
            
            # If still failing, return a structured error response
            return [{"error": "Could not parse topics from AI response"}]
            
    except Exception as e:
        raise Exception(f"Error generating topic timestamps: {str(e)}") 