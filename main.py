from openai import OpenAI
from dotenv import load_dotenv
import re
import os
import subprocess
from pathlib import Path

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("❌ Error: OPENAI_API_KEY not found in .env file!")
    print("Please create a .env file and add: OPENAI_API_KEY=your-key-here")
    exit(1)

client = OpenAI()

def sanitize_folder_name(title):
    safe_name = re.sub(r'[^\w\s-]', '', title)
    safe_name = re.sub(r'[-\s]+', '-', safe_name)
    return safe_name.strip('-')

def check_docker_available():
    try:
        result = subprocess.run(['docker', 'info'],
                              capture_output=True,
                              timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def clean_markdown_for_speech(text):
    title_match = re.search(r'^# (.+)$', text, flags=re.MULTILINE)
    main_title = title_match.group(1) if title_match else "this topic"

    intro = f"Hello! Let me walk you through {main_title}. I'll explain everything step by step. Let's begin.\n\n"

    text = re.sub(r'\n---+\n', '\n\nMoving to the next section. \n\n', text)
    text = re.sub(r'^# (.+)$', r'\1. ', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'Now, \1. ', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r"\1. ", text, flags=re.MULTILINE)
    text = re.sub(r'^#### (.+)$', r"\1. ", text, flags=re.MULTILINE)

    text = re.sub(r'📚|📊|🎯|👨‍🎓|📋|🌟|🗄️|🎓', '', text)

    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)

    def replace_code_block(match):
        code = match.group(1)
        return f"Here's an example. {code}."
    text = re.sub(r'```[\w]*\n(.*?)\n```', replace_code_block, text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)

    text = re.sub(r'^\- ', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\* ', '', text, flags=re.MULTILINE)

    text = re.sub(r'\|(.+?)\|', r'\1. ', text)

    text = re.sub(r'Example:', r'For example', text, flags=re.IGNORECASE)
    text = re.sub(r'Note:', r'Note that', text, flags=re.IGNORECASE)
    text = re.sub(r'Important:', r'Importantly', text, flags=re.IGNORECASE)

    text = text.replace('→', ' to ')
    text = text.replace('✓', ' correct, ')
    text = text.replace('✅', ' yes, ')
    text = text.replace('❌', ' no, ')
    text = text.replace('⚠️', ' note: ')
    text = text.replace('⭐', ' ')
    text = text.replace('↓', ' requires ')
    text = text.replace('←', ' from ')

    text = re.sub(r'\n{3,}', '\n\n', text)

    outro = f"\n\nAnd that's the complete overview of {main_title}. I hope this explanation was clear and helpful. Thank you for using TalkDoc, created by Manish. If you found this useful, feel free to share it with your team. Have a great day!"

    return intro + text + outro

if not os.path.exists("script.md"):
    print("❌ Error: script.md not found!")
    print("Please create a script.md file with your content.")
    exit(1)

print("📖 Reading script.md...")
with open("script.md", "r") as f:
    script_content = f.read()

title_match = re.search(r'^# (.+)$', script_content, flags=re.MULTILINE)
if not title_match:
    print("⚠️  Warning: No H1 heading found in script.md. Using default folder name.")
    doc_title = "untitled"
else:
    doc_title = title_match.group(1)

print(f"📄 Document: {doc_title}")

safe_title = sanitize_folder_name(doc_title)
audio_dir = Path("audio") / safe_title
audio_dir.mkdir(parents=True, exist_ok=True)
print(f"📁 Audio folder: {audio_dir}")

print("🔄 Converting markdown to conversational speech...")
speech_script = clean_markdown_for_speech(script_content)

script_output = audio_dir / "speech_script.txt"
with open(script_output, "w") as f:
    f.write(speech_script)
print(f"💾 Saved speech script to {script_output}")

def chunk_text(text, max_chars=4000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1
        if current_length + word_length > max_chars:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

chunks = chunk_text(speech_script)
print(f"\n🎙️  Split into {len(chunks)} chunks for TTS API\n")

for i, chunk in enumerate(chunks, 1):
    print(f"🔊 Processing chunk {i}/{len(chunks)}...")

    try:
        speech = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=chunk
        )

        filename = audio_dir / f"voice_part_{i:03d}.mp3"
        with open(filename, "wb") as f:
            f.write(speech.read())

        print(f"   ✓ Saved {filename}")
    except Exception as e:
        print(f"   ✗ Error processing chunk {i}: {e}")

print("\n" + "="*60)
print("✅ All audio chunks generated successfully!")
print(f"📂 Location: {audio_dir}/")
print(f"📊 Total files: {len(chunks)} MP3 files")
print("="*60)

docker_available = check_docker_available()

if docker_available:
    print("\n🐳 Docker detected! Auto-combining audio files...")

    filelist_path = audio_dir / "filelist.txt"
    with open(filelist_path, "w") as f:
        for i in range(1, len(chunks) + 1):
            f.write(f"file 'voice_part_{i:03d}.mp3'\n")

    try:
        output_file = audio_dir / "voice_complete.mp3"
        subprocess.run([
            'docker', 'run', '--rm',
            '-v', f'{audio_dir.absolute()}:/tmp',
            '-w', '/tmp',
            'linuxserver/ffmpeg',
            '-f', 'concat', '-safe', '0',
            '-i', 'filelist.txt',
            '-c', 'copy',
            'voice_complete.mp3'
        ], check=True, capture_output=True)

        print(f"✅ Combined audio saved: {output_file}")

        file_size = output_file.stat().st_size / (1024 * 1024)
        print(f"📦 File size: {file_size:.2f} MB")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error combining files: {e}")
        print("You can manually combine using the command below.")
else:
    print("\n⚠️  Docker not detected.")
    print("To combine audio files, run:")
    print(f"\ncd {audio_dir}")
    print("docker run --rm -v \"$(pwd):/tmp\" -w /tmp linuxserver/ffmpeg \\")
    print("  -f concat -safe 0 -i filelist.txt -c copy voice_complete.mp3")

print("\n🎉 TalkDoc completed! Enjoy your audio explanation! 🎧")
