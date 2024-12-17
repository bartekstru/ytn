# YouTube Notes (YTN)

A CLI tool to generate study notes from YouTube videos using Azure OpenAI services. YTN automatically transcribes the video content (or uses subtitles when available) and creates well-structured study notes in markdown format.

## Features

- 📝 Automatic transcription using Azure Whisper API
- 🔍 Intelligent summarization using Azure OpenAI
- 📚 Well-structured study notes with table of contents
- 🎯 Uses subtitles when available for better accuracy
- 🗜️ Automatic audio compression for efficient processing
- 🧹 Automatic cleanup of temporary files

## Prerequisites

- Python 3.9 or higher
- FFmpeg installed on your system
- Azure OpenAI account with access to:
  - GPT model deployment (for summarization)
  - Whisper model deployment (for transcription)

## Installation

1. Install FFmpeg:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # macOS
   brew install ffmpeg

   # Windows (using Chocolatey)
   choco install ffmpeg
   ```

2. Install the package:
   ```bash
   pip install ytn
   ```

   Or install from source:
   ```bash
   git clone https://github.com/yourusername/ytn.git
   cd ytn
   pip install poetry
   poetry install
   ```

## Configuration

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your Azure OpenAI credentials in `.env`:
   ```plaintext
   # Azure OpenAI Configuration for LLM (Chat Model)
   YTN_AZURE_LLM_ENDPOINT=https://your-llm-resource.openai.azure.com
   YTN_AZURE_LLM_KEY=your-llm-api-key
   YTN_AZURE_LLM_DEPLOYMENT=gpt-35-turbo

   # Azure OpenAI Configuration for Whisper (Speech-to-Text)
   YTN_AZURE_WHISPER_ENDPOINT=https://your-whisper-resource.openai.azure.com
   YTN_AZURE_WHISPER_KEY=your-whisper-api-key
   YTN_AZURE_WHISPER_DEPLOYMENT=whisper
   ```

## Usage

Basic usage:
```bash
ytn process "https://youtube.com/watch?v=VIDEO_ID"
```

Specify output file:
```bash
ytn process "https://youtube.com/watch?v=VIDEO_ID" -o notes.md
