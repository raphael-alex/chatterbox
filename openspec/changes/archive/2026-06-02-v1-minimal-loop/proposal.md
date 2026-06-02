## Why

英语水平不高的中国家长难以在家中为孩子建立英语语言环境。现有工具（英语课程、AI 口语 App）要么依赖屏幕、要么需要家长本身具备英语能力。Chatterbox 旨在通过语音交互，让家长即使不会说英语，也能通过 AI 与孩子进行自然的英语对话——"take the words right out of my mouth with English"。v1.0 需要验证最核心的假设：AI 能否让孩子在自然的语音对话中接触并学习英语？

## What Changes

- 新增一个命令行语音对话工具，手动启动后持续监听
- 接收用户（孩子）的中文或英文语音输入，通过 ASR 转为文字
- LLM 将输入翻译为英文并生成自然的英语对话回复（自然融入翻译，不机械说 "You just said..."）
- 通过 TTS 将英文回复转为语音播放
- 单模式运行，无唤醒词、无模式切换、无声音克隆、无词汇追踪

## Capabilities

### New Capabilities
- `voice-pipeline`: 语音交互流水线——ASR 语音识别 → LLM 翻译+回复生成 → TTS 语音合成，支持中英文混合输入，英文输出
- `conversation-engine`: 对话引擎——LLM prompt 工程，生成适合儿童的英语回复，自然融入翻译，保持对话互动性

### Modified Capabilities

（无，v1.0 是全新项目）

## Impact

- 新项目，无现有代码受影响
- 依赖外部 API：ASR 服务（如 Whisper API）、LLM 服务（如 DeepSeek/GPT）、TTS 服务（如 Edge-TTS）
- 用户需要自行配置 API Key（环境变量或配置文件）
- Python 项目，目标运行环境为 macOS / Linux / 树莓派
