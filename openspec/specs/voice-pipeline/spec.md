## Requirements

### Requirement: 语音识别（ASR）
系统 SHALL 将麦克风采集的音频转换为文本，支持中文和英文混合识别。

#### Scenario: 用户说中文
- **WHEN** 用户说 "我喜欢恐龙"
- **THEN** 系统将音频识别为文本 "我喜欢恐龙"

#### Scenario: 用户说英文
- **WHEN** 用户说 "I like cats"
- **THEN** 系统将音频识别为文本 "I like cats"

#### Scenario: 用户中英混合
- **WHEN** 用户说 "我喜欢 dinosaur"
- **THEN** 系统将音频识别为包含中英文的文本

### Requirement: 语音合成（TTS）
系统 SHALL 将英文文本转换为语音并播放，使用适合儿童的自然英文语音。

#### Scenario: 生成英文语音
- **WHEN** 系统生成英文回复 "Oh, you like dinosaurs! Which one is your favorite?"
- **THEN** 系统将该文本合成为英文语音并播放

#### Scenario: 播放期间暂停录音
- **WHEN** 系统正在播放 TTS 语音
- **THEN** 系统暂停麦克风录音，防止自身语音被识别为输入

### Requirement: 麦克风录音与停顿检测
系统 SHALL 持续从麦克风录音，使用 VAD 检测用户说话的停顿，停顿超过阈值后将完整录音发送至 ASR。

#### Scenario: 检测到用户说完一句话
- **WHEN** 用户说完一句话后停顿超过 1.5 秒
- **THEN** 系统将录音片段发送至 ASR 进行识别

#### Scenario: 用户说话中不停顿
- **WHEN** 用户持续说话未停顿
- **THEN** 系统继续录音，不发送至 ASR

### Requirement: ASR 引擎可配置
系统 SHALL 支持通过配置文件切换 ASR 引擎，至少支持 Whisper API 和本地 Whisper。

#### Scenario: 使用 Whisper API
- **WHEN** 配置文件中 ASR 引擎设置为 "whisper-api"
- **THEN** 系统使用 OpenAI Whisper API 进行语音识别

#### Scenario: 使用本地 Whisper
- **WHEN** 配置文件中 ASR 引擎设置为 "whisper-local"
- **THEN** 系统使用本地 Whisper 模型进行语音识别

### Requirement: TTS 引擎可配置
系统 SHALL 支持通过配置文件切换 TTS 引擎，至少支持 Edge-TTS。

#### Scenario: 使用 Edge-TTS
- **WHEN** 配置文件中 TTS 引擎设置为 "edge-tts"
- **THEN** 系统使用 Edge-TTS 进行语音合成

### Requirement: 手动启动与退出
系统 SHALL 通过命令行手动启动，启动后显示模式选择菜单，用户选择语音或文字模式后进入主循环。运行中可通过 `/voice` `/text` 切换模式。用户可通过 Ctrl+C 退出。

#### Scenario: 启动程序
- **WHEN** 用户执行 `python main.py`
- **THEN** 系统初始化后显示模式选择菜单（1. 语音 2. 文字 3. 退出）

#### Scenario: 退出程序
- **WHEN** 用户按下 Ctrl+C
- **THEN** 系统安全退出，释放音频资源
