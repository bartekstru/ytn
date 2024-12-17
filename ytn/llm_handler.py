from openai import AzureOpenAI
from typing import List
import os
from dotenv import load_dotenv
from . import youtube_handler

# Load environment variables from .env file
load_dotenv()

def get_azure_llm_client():
    """Get Azure OpenAI client configured for LLM."""
    azure_endpoint = os.getenv("YTN_AZURE_LLM_ENDPOINT")
    azure_key = os.getenv("YTN_AZURE_LLM_KEY")
    azure_model = os.getenv("YTN_AZURE_LLM_DEPLOYMENT")
    
    if not all([azure_endpoint, azure_key, azure_model]):
        raise ValueError(
            "Missing required environment variables. Please set "
            "YTN_AZURE_LLM_ENDPOINT, YTN_AZURE_LLM_KEY, and YTN_AZURE_LLM_DEPLOYMENT"
        )
    
    client = AzureOpenAI(
        api_key=azure_key,
        api_version="2024-02-15-preview",
        azure_endpoint=azure_endpoint
    )
    
    return client, azure_model

# Initialize Azure OpenAI client for LLM
client, DEFAULT_MODEL = get_azure_llm_client()

SUMMARY_PROMPT = """
You are an expert at creating clear and concise study notes. Given the following transcript 
section from a YouTube video, create a detailed summary that:
1. Captures the main concepts and key points
2. Preserves important examples and explanations
3. Uses clear formatting with headers, bullet points, and code blocks if relevant
4. Maintains academic language while being easy to understand

Transcript section:
{text}

Create a summary in markdown format:
"""

FINAL_NOTES_PROMPT = """
You are creating the final study notes from a YouTube video. Below are the video details and 
summaries of different sections. Create a coherent markdown document that:
1. Starts with a title and brief overview
2. Combines all summaries into logical sections
3. Ensures smooth transitions between topics
4. Adds a table of contents
5. Includes metadata about the video

Video Title: {title}
Author: {author}
Duration: {duration} minutes

Summaries to combine:
{summaries}

Create the final study notes in markdown format:
"""

def generate_chunk_summaries(chunks: List[str]) -> List[str]:
    """Generate summaries for each chunk of text."""
    summaries = []
    
    for chunk in chunks:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert study note creator."},
                {"role": "user", "content": SUMMARY_PROMPT.format(text=chunk)}
            ],
            temperature=0.7,
        )
        summaries.append(response.choices[0].message.content)
    
    return summaries

def create_final_notes(
    summaries: List[str],
    video_info: youtube_handler.VideoInfo,
) -> str:
    """Create final coherent notes from all summaries."""
    combined_summaries = "\n\n---\n\n".join(summaries)
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert study note creator."},
            {
                "role": "user",
                "content": FINAL_NOTES_PROMPT.format(
                    title=video_info.title,
                    author=video_info.author,
                    duration=video_info.duration // 60,
                    summaries=combined_summaries
                )
            }
        ],
        temperature=0.7,
    )
    
    return response.choices[0].message.content 