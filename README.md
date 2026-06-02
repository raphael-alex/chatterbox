# Chatterbox

> Take the words right out of my mouth with English

AI-powered voice tool that helps non-English-speaking parents create an English language environment for their children.

## What it does

When your child speaks (in Chinese or English), Chatterbox:
1. Listens and transcribes their speech
2. Translates and responds in natural, child-friendly English
3. Speaks the English response aloud

```
Child: "我喜欢恐龙"
Chatterbox: "Oh, you like dinosaurs! Which one is your favorite?" 🔊
```

## Quick Start

### Prerequisites

- Python 3.10+
- A microphone
- An OpenAI API key (or DeepSeek API key)

### Install

```bash
git clone https://github.com/your-username/chatterbox.git
cd chatterbox
pip install -r requirements.txt
```

### Configure

```bash
# Set your API key
export OPENAI_API_KEY="sk-..."

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

### Using DeepSeek instead of OpenAI

```yaml
llm:
  engine: deepseek
  deepseek:
    api_key: ${DEEPSEEK_API_KEY}
```

```bash
export DEEPSEEK_API_KEY="your-key"
```

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

## Roadmap

- **v1.0** — Minimal loop (current)
- **v1.1** — Wake word ("hello") + age/level config
- **v1.2** — Dual mode (AI buddy / Translation assistant)
- **v1.3** — Vocabulary tracking
- **v2.0** — Voice cloning (your voice speaks English!) + Pro cloud service

## License

MIT
