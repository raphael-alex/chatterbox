## Context

Chatterbox 是一个全新项目，没有任何现有代码。v1.0 的目标是验证核心假设：AI 能否让孩子在自然的语音对话中接触英语。当前项目目录为空，仅有 OpenSpec 配置。

目标用户为有技术背景的家庭（开源版先行），运行环境为 macOS / Linux / 树莓派。

## Goals / Non-Goals

**Goals:**
- 实现 ASR → LLM → TTS 的最小闭环，手动启动即可运行
- 用户（孩子）说中文或英文，系统用英语回复，自然融入翻译
- 配置简单：一个配置文件放 API Key，`pip install && python main.py` 即可运行
- 代码结构清晰，为后续版本（唤醒词、双模式、词汇追踪等）留出扩展空间

**Non-Goals:**
- 唤醒词检测（v1.1）
- 双模式切换（v1.2）
- 词汇追踪和自主学习（v1.3+）
- 声音克隆（v2.0）
- 云端服务和家长面板（v2.0）
- 年龄/水平配置（v1.1，v1.0 硬编码为中等难度儿童英语）
- 声纹识别、多人说话处理（v2.x）

## Decisions

### 1. 不依赖语音助手框架，纯自建最小流水线

**选择**: 自建 ASR → LLM → TTS 流水线，不使用 wukong-robot / open-voicebox-pi 等框架。

**理由**: v1.0 的核心是验证假设，不需要唤醒词、插件系统、智能家居等框架能力。自建流水线代码量最小，依赖最少，调试最直接。框架集成留给 v1.4，届时根据社区反馈决定。

**备选**: wukong-robot（功能过多，Python < 3.10 限制）、open-voicebox-pi（项目太新，不够稳定）。

### 2. ASR 引擎：OpenAI Whisper API（默认）+ 本地 Whisper（可选）

**选择**: 默认使用 OpenAI Whisper API 进行语音识别，支持中英文混合识别。提供本地 Whisper (whisper.cpp / faster-whisper) 作为离线备选。

**理由**: Whisper API 零配置、识别质量高、中英文混合识别能力强。本地 Whisper 供有隐私需求或网络不稳定的用户使用。ASR 引擎通过适配器模式抽象，后续可替换为讯飞等国内服务。

### 3. LLM 引擎：通过适配器支持多种 LLM API

**选择**: 默认支持 OpenAI API（GPT-4o-mini），同时支持 DeepSeek API。通过适配器模式，用户可在配置文件中选择。

**理由**: v1.0 的核心是 prompt 工程，LLM 能力是关键。GPT-4o-mini 成本低且中英文能力均衡。DeepSeek 作为国产替代，价格更低。适配器模式为后续扩展其他模型留出空间。

### 4. TTS 引擎：Edge-TTS（默认）+ 其他可选

**选择**: 默认使用 edge-tts（微软 Edge TTS 的 Python 封装），免费且英文语音质量高。

**理由**: edge-tts 免费、无需 API Key、英文语音自然度高、支持流式输出。适合 MVP 阶段。后续可扩展为讯飞 TTS、CosyVoice 等。

### 5. 项目结构：模块化单进程

**选择**: 单进程 Python 应用，模块化文件组织，不使用微服务或进程间通信。

**理由**: v1.0 功能简单，单进程足够。模块化保证代码清晰，后续可拆分。

```
chatterbox/
├── main.py              # 入口，启动主循环
├── config.py            # 配置加载
├── config.yaml          # 用户配置文件（API Key 等）
├── asr/
│   ├── base.py          # ASR 适配器基类
│   └── whisper.py       # Whisper ASR 实现
├── llm/
│   ├── base.py          # LLM 适配器基类
│   ├── openai_adapter.py
│   └── deepseek_adapter.py
├── tts/
│   ├── base.py          # TTS 适配器基类
│   └── edge_tts.py      # Edge-TTS 实现
├── conversation/
│   └── prompt.py        # Prompt 模板和对话管理
├── audio/
│   ├── recorder.py      # 麦克风录音
│   └── player.py        # 音频播放
└── requirements.txt
```

### 6. 音频流管理：录音 → 停顿检测 → 处理 → 播放

**选择**: 使用 VAD（Voice Activity Detection）检测停顿，停顿超过阈值则将录音发送至 ASR。播放期间暂停录音，避免自说自听。

**理由**: 亲子对话是轮流说话的模式，VAD 停顿检测足够用。播放期间暂停录音是防止系统自身语音被识别为输入的基本要求。

### 7. Prompt 设计：自然融入翻译

**选择**: LLM prompt 不使用 "You just said..." 的机械翻译模式，而是引导 LLM 自然地将翻译融入英语回复中。

**理由**: 对孩子来说，"Oh, you like dinosaurs! Which one is your favorite?" 比 "You said you like dinosaurs. That's cool!" 更自然。后者是翻译确认，前者是对话互动。v1.0 先用自然融合模式，v1.1+ 根据年龄配置可选切换。

## Risks / Trade-offs

- **[延迟]** ASR + LLM + TTS 三次 API 调用串行，预计延迟 3-5 秒 → 使用流式 TTS 减少感知延迟，播放时边生成边输出
- **[Whisper API 成本]** 按使用量计费，长时间运行可能产生费用 → 提供本地 Whisper 选项，config 中可切换
- **[录音质量]** 家庭环境噪音影响 ASR 识别率 → prompt 设计允许 LLM 容忍轻微识别错误，v1.2 加入语法守门
- **[Edge-TTS 稳定性]** 非官方 API，可能被限流 → 后续版本提供官方 TTS API 备选
- **[单进程瓶颈]** 三个 API 调用串行，无法并行处理 → v1.0 可接受，v1.x 可引入异步
