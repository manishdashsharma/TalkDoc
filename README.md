# 🎙️ TalkDoc

**Convert your markdown documents into professional AI-powered voice explanations**

TalkDoc transforms your markdown documentation into engaging audio explanations that sound like a lead explaining concepts to their team.

---

## ✨ Features

- 🗣️ **Conversational AI Voice**: Sounds like a real person explaining, not reading
- 📁 **Smart Organization**: Automatically organizes audio files by document title
- 🐳 **Docker Integration**: Auto-detects Docker and combines audio files automatically
- 🎯 **Multiple Voices**: Choose from 6 different AI voices
- 📝 **Markdown Support**: Handles headings, lists, code blocks, tables, and more
- ⚡ **Fast Processing**: Processes large documents efficiently in chunks

---

## 🚀 Quick Start

### Option 1: One-Command Start (Recommended)

```bash
./start.sh
```

This will automatically:
- ✅ Check and start Docker
- ✅ Pull FFmpeg image
- ✅ Verify setup
- ✅ Install dependencies
- ✅ Run TalkDoc

### Option 2: Manual Setup

### 1. Installation

```bash
cd talkdoc
uv sync
```

### 2. Setup OpenAI API Key

Create a `.env` file:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

### 3. Create Your Script

Edit `script.md` with your content:

```markdown
# My Amazing Product

This is the introduction to my product...

## Features

- Feature 1
- Feature 2
```

### 4. Generate Audio

```bash
uv run main.py
```

Your audio files will be in `audio/My-Amazing-Product/`

---

## 📂 Project Structure

```
talkdoc/
├── README.md
├── start.sh              ⭐ One-command starter
├── script.md
├── main.py
├── .env
├── audio/
│   └── [Document-Title]/
│       ├── voice_part_001.mp3
│       ├── voice_part_002.mp3
│       ├── voice_complete.mp3
│       └── speech_script.txt
└── pyproject.toml
```

---

## 🐳 Docker Integration

TalkDoc automatically detects if Docker is running:

**Docker Available**: Automatically combines all audio parts into `voice_complete.mp3`

**Docker Not Available**: Manual combine command will be shown

### Manual Combine Command
```bash
cd audio/Your-Document-Title/
docker run --rm -v "$(pwd):/tmp" -w /tmp linuxserver/ffmpeg \
  -f concat -safe 0 -i filelist.txt -c copy voice_complete.mp3
```

---

## 🎤 Voice Options

Change the voice in `main.py`:

```python
voice="alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer
```

**Voice Characteristics:**
- **alloy**: Neutral, professional (default)
- **echo**: Clear, articulate
- **fable**: Warm, friendly
- **onyx**: Deep, authoritative
- **nova**: Energetic, engaging
- **shimmer**: Soft, calm

---

## 📝 Writing Tips

1. **Use Clear Headings**: H1 for title, H2 for sections, H3 for subsections
2. **Short Paragraphs**: Keep paragraphs concise for better pacing
3. **Lists Work Great**: Bullet points are naturally explained
4. **Add Context**: This is an explanation, not just reading text
5. **Examples Help**: Use code blocks to illustrate points

---

## 🐛 Troubleshooting

**"OPENAI_API_KEY not found"**
- Make sure `.env` file exists with `OPENAI_API_KEY=sk-...`

**"script.md not found"**
- Create `script.md` in the project root

**Docker Not Detected**
- Make sure Docker Desktop is running
- Try `docker info` to verify

---

## 💡 Use Cases

- Product Documentation
- Training Materials
- Onboarding Guides
- Technical Explanations
- Meeting Prep
- Educational Content

---

## 👨‍💻 Author

**Manish**

TalkDoc - Transforming documentation into engaging audio experiences.

---

**Made with ❤️ for better documentation experiences**
