## 1. 项目初始化

- [x] 1.1 创建项目目录结构（chatterbox/、asr/、llm/、tts/、conversation/、audio/）
- [x] 1.2 创建 requirements.txt（pyaudio、openai、edge-tts、webrtcvad、pyyaml 等）
- [x] 1.3 创建 config.yaml 模板（ASR 引擎、LLM 引擎、TTS 引擎、API Key 占位符、VAD 阈值等）
- [x] 1.4 创建 config.py（加载 config.yaml、环境变量覆盖、校验必填项）

## 2. 音频输入输出

- [x] 2.1 实现 audio/recorder.py：麦克风录音，使用 PyAudio 采集音频流
- [x] 2.2 实现 VAD 停顿检测：使用 webrtcvad 检测语音活动，停顿超阈值返回完整录音片段
- [x] 2.3 实现 audio/player.py：音频播放，支持播放期间暂停录音

## 3. ASR 语音识别

- [x] 3.1 实现 asr/base.py：ASR 适配器基类，定义 transcribe(audio_data) -> str 接口
- [x] 3.2 实现 asr/whisper.py：Whisper API 适配器，调用 OpenAI Whisper API
- [x] 3.3 实现 asr/whisper_local.py：本地 Whisper 适配器，使用 faster-whisper 或 whisper.cpp

## 4. LLM 对话引擎

- [x] 4.1 实现 llm/base.py：LLM 适配器基类，定义 chat(messages) -> str 接口
- [x] 4.2 实现 llm/openai_adapter.py：OpenAI API 适配器
- [x] 4.3 实现 llm/deepseek_adapter.py：DeepSeek API 适配器
- [x] 4.4 实现 conversation/prompt.py：Chatterbox 系统 prompt 模板，定义角色和回复规则
- [x] 4.5 实现对话上下文管理：维护消息历史列表，支持多轮对话

## 5. TTS 语音合成

- [x] 5.1 实现 tts/base.py：TTS 适配器基类，定义 synthesize(text) -> audio_data 接口
- [x] 5.2 实现 tts/edge_tts.py：Edge-TTS 适配器，调用 edge-tts 库

## 6. 主循环集成

- [x] 6.1 实现 main.py：主循环（录音 → VAD → ASR → LLM → TTS → 播放），串联所有模块
- [x] 6.2 实现 Ctrl+C 优雅退出：释放音频资源，打印告别语

## 7. 测试与文档

- [x] 7.1 端到端测试：手动启动，用中文和英文分别测试完整对话流
- [x] 7.2 创建 README.md：30 秒看懂产品、5 分钟安装运行、配置说明、demo 截图占位
- [x] 7.3 创建 .env.example：API Key 模板文件
