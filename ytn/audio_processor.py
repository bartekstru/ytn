from openai import AzureOpenAI
from pathlib import Path
import os
from dotenv import load_dotenv
import shutil

# Load environment variables from .env file
load_dotenv()

def get_azure_whisper_client():
    """Get Azure OpenAI client configured for Whisper."""
    azure_endpoint = os.getenv("YTN_AZURE_WHISPER_ENDPOINT")
    azure_key = os.getenv("YTN_AZURE_WHISPER_KEY")
    azure_whisper_deployment = os.getenv("YTN_AZURE_WHISPER_DEPLOYMENT")
    
    if not all([azure_endpoint, azure_key, azure_whisper_deployment]):
        raise ValueError(
            "Missing required environment variables. Please set "
            "YTN_AZURE_WHISPER_ENDPOINT, YTN_AZURE_WHISPER_KEY, and YTN_AZURE_WHISPER_DEPLOYMENT"
        )
    
    client = AzureOpenAI(
        api_key=azure_key,
        api_version="2024-02-15-preview",
        azure_endpoint=azure_endpoint
    )
    
    return client, azure_whisper_deployment

def transcribe_audio(audio_path: Path) -> str:
    """Transcribe audio file using Azure OpenAI Whisper API."""
    try:
        # Get Azure Whisper client and deployment
        client, deployment_id = get_azure_whisper_client()
        
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model=deployment_id,
                file=audio_file
            )
        
        return transcript.text
        
    except Exception as e:
        raise Exception(f"Error transcribing audio: {str(e)}")
    finally:
        # Cleanup: remove the audio file and its parent directory
        try:
            if audio_path.exists():
                parent_dir = audio_path.parent
                audio_path.unlink()
                shutil.rmtree(parent_dir, ignore_errors=True)
        except Exception:
            pass 