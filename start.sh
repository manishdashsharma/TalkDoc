#!/bin/bash

echo "🎙️  TalkDoc - Starting..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found!"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker is running
echo "🐳 Checking Docker status..."
if ! docker info &> /dev/null; then
    echo "⚠️  Docker is not running"
    echo "🚀 Starting Docker..."
    
    # Try to start Docker on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open -a Docker
        echo "⏳ Waiting for Docker to start (this may take 30 seconds)..."
        
        # Wait for Docker to be ready
        count=0
        while ! docker info &> /dev/null && [ $count -lt 30 ]; do
            sleep 1
            count=$((count + 1))
            echo -n "."
        done
        echo ""
        
        if ! docker info &> /dev/null; then
            echo "❌ Failed to start Docker automatically"
            echo "Please start Docker Desktop manually and run this script again"
            exit 1
        fi
        echo "✅ Docker started successfully!"
    else
        echo "Please start Docker manually and run this script again"
        exit 1
    fi
else
    echo "✅ Docker is running"
fi

# Pull FFmpeg image
echo ""
echo "📥 Checking FFmpeg image..."
if docker image inspect linuxserver/ffmpeg:latest &> /dev/null; then
    echo "✅ FFmpeg image already exists"
else
    echo "🔄 Pulling FFmpeg image (one-time download, ~500MB)..."
    docker pull linuxserver/ffmpeg:latest
    if [ $? -eq 0 ]; then
        echo "✅ FFmpeg image pulled successfully"
    else
        echo "❌ Failed to pull FFmpeg image"
        exit 1
    fi
fi

# Check if .env exists
echo ""
echo "🔑 Checking environment setup..."
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from template..."
    cp .env.example .env
    echo "❌ Please add your OPENAI_API_KEY to .env file"
    echo "Get your key from: https://platform.openai.com/api-keys"
    exit 1
fi

# Check if API key is set
if ! grep -q "^OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  OPENAI_API_KEY not configured in .env"
    echo "Please add your OpenAI API key to .env file"
    echo "Get your key from: https://platform.openai.com/api-keys"
    exit 1
fi
echo "✅ API key configured"

# Check if script.md exists
echo ""
echo "📄 Checking script.md..."
if [ ! -f script.md ]; then
    echo "⚠️  script.md not found!"
    echo "Please create script.md with your content"
    exit 1
fi
echo "✅ script.md found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
if ! command -v uv &> /dev/null; then
    echo "❌ uv not found!"
    echo "Install uv from: https://github.com/astral-sh/uv"
    exit 1
fi

uv sync --quiet
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Run TalkDoc
echo ""
echo "="*60
echo "🎬 Starting TalkDoc..."
echo "="*60
echo ""

uv run main.py

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo "="*60
    echo "✅ TalkDoc completed successfully!"
    echo "="*60
    
    # Show audio directory
    if [ -d audio ]; then
        echo ""
        echo "📂 Generated audio files:"
        ls -lh audio/*/voice_complete.mp3 2>/dev/null || echo "   Check audio/ folder for your files"
    fi
else
    echo ""
    echo "❌ TalkDoc encountered an error"
    exit 1
fi
