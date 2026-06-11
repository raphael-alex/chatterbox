# Chatterbox

> Take the words right out of my mouth with English

AI-powered voice tool that helps non-English-speaking parents create an English language environment for their children.

## What it does

When your child speaks (in Chinese or English), Chatterbox:
1. Listens and transcribes their speech
2. Translates and responds in natural, child-friendly English
3. Speaks the English response aloud

## Quick Start

### Prerequisites

- Python 3.10+
- A microphone
- A DeepSeek API key

### Install

```bash
git clone https://github.com/raphael-alex/chatterbox.git
cd chatterbox
pip install -r requirements.txt
```

### Configure

```bash
# Set your API key
export DEEPSEEK_API_KEY="sk-..."

# Or copy and edit config.yaml
cp config.yaml my_config.yaml
# Edit my_config.yaml with your settings
```

### Run

```bash
python main.py
```

Press `Ctrl+C` to exit.

## Configuration

Edit `config.yaml` to customize:

| Setting | Options | Default |
|---------|---------|---------|
| ASR engine | `whisper-api`, `whisper-local` | `whisper-api` |
| LLM engine | `openai`, `deepseek` | `openai` |
| TTS engine | `edge-tts` | `edge-tts` |
| TTS voice | Edge-TTS voice names | `en-US-JennyNeural` |
| VAD silence duration | seconds | `1.5` |

### Using local Whisper (offline ASR)

```yaml
asr:
  engine: whisper-local
  whisper_local:
    model_size: base  # tiny, base, small, medium, large
    device: auto
```

## Architecture

```
Microphone → VAD → ASR → LLM → TTS → Speaker
```

All components use an adapter pattern — swap engines via config without code changes.

## License

MIT
