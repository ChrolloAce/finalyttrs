# YouTube Forever API

A FastAPI-based service that extracts YouTube video transcripts and generates summaries, tags, and topic breakdowns with timestamps using OpenAI.

## Features

- **Transcript Extraction**: Pulls complete transcripts from YouTube videos
- **Text Summarization**: Creates concise video summaries
- **Tag Generation**: Extracts relevant tags from video content
- **Topic Timestamps**: Identifies key topics with timestamps

## API Endpoints

- `GET /` - Check API status
- `GET /transcript?url={youtube_url}` - Get full transcript with timestamps
- `GET /text?url={youtube_url}` - Get transcript text only
- `GET /summary?url={youtube_url}&max_words={max_words}` - Get video summary
- `GET /tags?url={youtube_url}&max_tags={max_tags}` - Get relevant tags
- `GET /topics?url={youtube_url}` - Get topic breakdowns with timestamps

Full API documentation available at `/docs` when running the server.

## Setup

### Prerequisites

- Python 3.8+
- OpenAI API key

### Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
4. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```
5. Visit `http://localhost:8000/docs` for API documentation

### Docker Deployment

To run using Docker:

```bash
# Build the Docker image
docker build -t youtube-forever-api .

# Run the container
docker run -p 8000:8000 -e OPENAI_API_KEY=your_openai_api_key_here youtube-forever-api
```

## Deployment Options

### Railway

1. Push your code to GitHub
2. Go to [Railway](https://railway.app/)
3. Create a new project from your GitHub repo
4. Add your `OPENAI_API_KEY` as an environment variable
5. Deploy your application

### Render

1. Push your code to GitHub
2. Go to [Render](https://render.com/)
3. Create a new Web Service from your GitHub repo
4. Select "Docker" as the environment
5. Add your `OPENAI_API_KEY` as an environment variable
6. Deploy your application

### Fly.io

1. Install the Fly CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```
2. Login to Fly.io:
   ```bash
   fly auth login
   ```
3. Launch your app:
   ```bash
   fly launch
   ```
4. Set your OpenAI API key:
   ```bash
   fly secrets set OPENAI_API_KEY=your_openai_api_key_here
   ```
5. Deploy your app:
   ```bash
   fly deploy
   ```

## Usage Examples

### Get Video Summary

```javascript
const response = await fetch('https://your-api-url.com/summary?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ');
const data = await response.json();
console.log(data.summary);
```

### Get Video Topics with Timestamps

```javascript
const response = await fetch('https://your-api-url.com/topics?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ');
const data = await response.json();
console.log(data.topics);
```

## Cost Considerations

- OpenAI's GPT-3.5 Turbo costs approximately $0.002 per 1K tokens
- For most videos, the API costs should be minimal
- Consider using a model with smaller context (e.g., gpt-3.5-turbo instead of gpt-4) for cost efficiency

## License

MIT 