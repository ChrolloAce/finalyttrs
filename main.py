from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any, Optional
import uvicorn
import logging

from youtube_utils import extract_video_id, get_transcript, get_transcript_text, format_seconds_to_mmss
from ai_utils import generate_summary, generate_tags, generate_topic_timestamps

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Forever API",
    description="API for extracting and analyzing YouTube video transcripts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class TranscriptResponse(BaseModel):
    video_id: str
    transcript: List[Dict[str, Any]]
    
class TranscriptTextResponse(BaseModel):
    video_id: str
    text: str
    
class SummaryResponse(BaseModel):
    video_id: str
    summary: str
    
class TagsResponse(BaseModel):
    video_id: str
    tags: List[str]
    
class TopicResponse(BaseModel):
    video_id: str
    topics: List[Dict[str, Any]]

@app.get("/", tags=["Status"])
async def root():
    """
    Root endpoint to check if the API is running.
    """
    logger.info("Root endpoint accessed")
    return {"status": "YouTube Forever API is running"}

@app.get("/transcript", response_model=TranscriptResponse, tags=["Transcript"])
async def get_video_transcript(url: str = Query(..., description="YouTube video URL")):
    """
    Get the full transcript data for a YouTube video including timestamps.
    """
    try:
        logger.info(f"Transcript endpoint accessed for URL: {url}")
        video_id = extract_video_id(url)
        logger.info(f"Extracted video ID: {video_id}")
        transcript_data = get_transcript(video_id)
        logger.info(f"Successfully retrieved transcript with {len(transcript_data)} segments")
        return {"video_id": video_id, "transcript": transcript_data}
    except ValueError as e:
        logger.error(f"Invalid URL format: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in transcript endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/text", response_model=TranscriptTextResponse, tags=["Transcript"])
async def get_video_transcript_text(url: str = Query(..., description="YouTube video URL")):
    """
    Get the transcript text only (without timestamps) for a YouTube video.
    """
    try:
        logger.info(f"Text endpoint accessed for URL: {url}")
        video_id = extract_video_id(url)
        logger.info(f"Extracted video ID: {video_id}")
        transcript_text = get_transcript_text(video_id)
        logger.info(f"Successfully retrieved transcript text with {len(transcript_text)} characters")
        return {"video_id": video_id, "text": transcript_text}
    except ValueError as e:
        logger.error(f"Invalid URL format: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in text endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary", response_model=SummaryResponse, tags=["Analysis"])
async def get_video_summary(
    url: str = Query(..., description="YouTube video URL"),
    max_words: int = Query(100, description="Maximum number of words in summary")
):
    """
    Get a concise summary of the YouTube video.
    """
    try:
        logger.info(f"Summary endpoint accessed for URL: {url} with max_words={max_words}")
        video_id = extract_video_id(url)
        transcript_text = get_transcript_text(video_id)
        summary = generate_summary(transcript_text, max_words)
        logger.info(f"Successfully generated summary with {len(summary.split())} words")
        return {"video_id": video_id, "summary": summary}
    except ValueError as e:
        logger.error(f"Invalid URL format: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in summary endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tags", response_model=TagsResponse, tags=["Analysis"])
async def get_video_tags(
    url: str = Query(..., description="YouTube video URL"),
    max_tags: int = Query(10, description="Maximum number of tags to generate")
):
    """
    Get relevant tags for the YouTube video.
    """
    try:
        logger.info(f"Tags endpoint accessed for URL: {url} with max_tags={max_tags}")
        video_id = extract_video_id(url)
        transcript_text = get_transcript_text(video_id)
        tags = generate_tags(transcript_text, max_tags)
        logger.info(f"Successfully generated {len(tags)} tags")
        return {"video_id": video_id, "tags": tags}
    except ValueError as e:
        logger.error(f"Invalid URL format: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in tags endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/topics", response_model=TopicResponse, tags=["Analysis"])
async def get_video_topics(url: str = Query(..., description="YouTube video URL")):
    """
    Get topic breakdowns with timestamps for the YouTube video.
    """
    try:
        logger.info(f"Topics endpoint accessed for URL: {url}")
        video_id = extract_video_id(url)
        transcript_data = get_transcript(video_id)
        topics = generate_topic_timestamps(transcript_data)
        logger.info(f"Successfully generated {len(topics)} topics")
        return {"video_id": video_id, "topics": topics}
    except ValueError as e:
        logger.error(f"Invalid URL format: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in topics endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 