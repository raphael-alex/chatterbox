## MODIFIED Requirements

### Requirement: 语音合成（TTS）
系统 SHALL 将英文文本转换为语音并播放，使用适合儿童的自然英文语音。在合成前 SHALL 对文本进行预处理，过滤 emoji 和非语音字符。

#### Scenario: 生成英文语音
- **WHEN** 系统生成英文回复 "Oh, you like dinosaurs! Which one is your favorite?"
- **THEN** 系统将该文本合成为英文语音并播放

#### Scenario: 合成前过滤 emoji
- **WHEN** 系统生成包含 emoji 的回复 "Great job! 🌟 You're amazing!"
- **THEN** 系统先将文本预处理为 "Great job! You're amazing!"，再进行语音合成

#### Scenario: 播放期间暂停录音
- **WHEN** 系统正在播放 TTS 语音
- **THEN** 系统暂停麦克风录音，防止自身语音被识别为输入
