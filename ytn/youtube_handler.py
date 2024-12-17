from yt_dlp import YoutubeDL
from pathlib import Path
from pydantic import BaseModel
import tempfile
import os
import shutil
from typing import Tuple
import ffmpeg

class VideoInfo(BaseModel):
    title: str
    author: str
    description: str
    duration: int

def compress_audio(input_path: Path) -> Tuple[Path, int, int]:
    """
    Compress audio file and return the new path and sizes.
    
    Returns:
        Tuple containing:
        - Path to compressed file
        - Original size in bytes
        - Compressed size in bytes
    """
    original_size = input_path.stat().st_size
    output_path = input_path.parent / "compressed.mp3"
    
    # Compress using ffmpeg with a lower bitrate
    stream = ffmpeg.input(str(input_path))
    stream = ffmpeg.output(stream, str(output_path), 
                         acodec='libmp3lame', 
                         ab='64k',  # Lower bitrate for smaller file
                         loglevel='error')
    ffmpeg.run(stream, overwrite_output=True)
    
    compressed_size = output_path.stat().st_size
    return output_path, original_size, compressed_size

def get_video_info(url: str) -> VideoInfo:
    """Get video information and verify it exists."""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return VideoInfo(
                title=info.get('title', ''),
                author=info.get('uploader', ''),
                description=info.get('description', ''),
                duration=info.get('duration', 0)
            )
    except Exception as e:
        raise Exception(f"Error fetching video info: {str(e)}")

def get_english_subtitles(url: str) -> str | None:
    """Try to download English subtitles."""
    temp_dir = tempfile.mkdtemp()
    try:
        ydl_opts = {
            'writesubtitles': True,
            'subtitleslangs': ['en'],
            'skip_download': True,
            'outtmpl': str(Path(temp_dir) / 'subs'),
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                if info.get('subtitles') and 'en' in info['subtitles']:
                    # Download and read subtitles
                    subtitle_data = ydl.download_subtitles(info, ['en'])
                    return subtitle_data.get('en', '')
            except Exception:
                return None
            finally:
                # Cleanup downloaded files
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        return None
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return None

def download_audio(url: str) -> Tuple[Path, int, int]:
    """
    Download and compress audio from the video.
    
    Returns:
        Tuple containing:
        - Path to compressed audio file
        - Original size in bytes
        - Compressed size in bytes
    """
    temp_dir = tempfile.mkdtemp()
    output_path = Path(temp_dir) / "audio.mp3"
    
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': str(output_path.with_suffix('').as_posix()),
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
                return compress_audio(output_path)
            except Exception as e:
                raise Exception(f"Error downloading audio: {str(e)}")
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise e 