import typer
from pathlib import Path
from typing import Optional
from . import youtube_handler
from . import audio_processor
from . import text_processor
from . import llm_handler
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = typer.Typer()

@app.command()
def process(
    url: str,
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path for the notes (default: video_title.md)",
    ),
):
    """
    Generate study notes from a YouTube video.
    
    Required environment variables (in .env file):
    - YTN_AZURE_LLM_ENDPOINT, YTN_AZURE_LLM_KEY, and YTN_AZURE_LLM_DEPLOYMENT for chat model
    - YTN_AZURE_WHISPER_ENDPOINT, YTN_AZURE_WHISPER_KEY, and YTN_AZURE_WHISPER_DEPLOYMENT for speech-to-text
    """
    try:
        # Check if video exists and get video info
        video_info = youtube_handler.get_video_info(url)
        
        # Clean the title to be safe for filenames on all platforms
        safe_title = "".join(c for c in video_info.title if c.isalnum() or c in (' ', '-', '_')).strip()
        
        # Try to get English subtitles
        subtitle_text = youtube_handler.get_english_subtitles(url)
        
        if subtitle_text:
            typer.echo("Found English subtitles, processing...")
            full_text = subtitle_text
        else:
            typer.echo("No English subtitles found, downloading audio...")
            audio_path, original_size, compressed_size = youtube_handler.download_audio(url)
            
            # Show compression results
            typer.echo(f"Audio size: {original_size/1024/1024:.1f}MB")
            typer.echo(f"Compressed size: {compressed_size/1024/1024:.1f}MB")
            typer.echo(f"Compression ratio: {original_size/compressed_size:.1f}x")
            
            typer.echo("Transcribing audio with Azure Whisper API...")
            full_text = audio_processor.transcribe_audio(audio_path)
            # Cleanup is now handled in transcribe_audio
        
        # Process the text into chunks
        chunks = text_processor.create_chunks(full_text)
        
        # Generate summaries for each chunk
        typer.echo("Generating summaries for each section...")
        summaries = llm_handler.generate_chunk_summaries(chunks)
        
        # Create final coherent notes
        typer.echo("Creating final study notes...")
        final_notes = llm_handler.create_final_notes(summaries, video_info)
        
        # Save to file
        if not output_file:
            output_file = Path.cwd().joinpath(f"{safe_title}.md")
        
        # Ensure the directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write with UTF-8 encoding
        with open(output_file, "w", encoding="utf-8", newline='\n') as f:
            f.write(final_notes)
            
        typer.echo(f"✨ Study notes saved to: {output_file}")
        
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 