## ADDED Requirements

### Requirement: TTS 文本预处理
系统 SHALL 在 TTS 合成前对文本进行预处理，过滤 emoji 和其他非语音字符，确保 TTS 只朗读可读的文本内容。

#### Scenario: 过滤 emoji
- **WHEN** LLM 回复包含 emoji，如 "Oh, you like dinosaurs! 🦕 Which one is your favorite?"
- **THEN** TTS 接收到的文本为 "Oh, you like dinosaurs! Which one is your favorite?"

#### Scenario: 纯文本不变
- **WHEN** LLM 回复不包含 emoji，如 "Cats are so cute!"
- **THEN** TTS 接收到的文本不变

#### Scenario: 混合 emoji 和文本
- **WHEN** LLM 回复包含多个 emoji，如 "Great job! 🌟👍 You're amazing!"
- **THEN** TTS 接收到的文本为 "Great job! You're amazing!"
