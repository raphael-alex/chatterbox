## 1. TTS 文本预处理

- [x] 1.1 创建 chatterbox/tts/preprocessing.py：实现 clean_for_tts(text) -> str，正则过滤 emoji 和非语音字符
- [x] 1.2 修改 chatterbox/tts/edge_tts.py：synthesize 方法在合成前调用 clean_for_tts

## 2. Prompt 策略修改

- [x] 2.1 重写 chatterbox/conversation/prompt.py：新增 BEGINNER_PROMPT（显式翻译策略），禁止 emoji，保留原 SYSTEM_PROMPT 为 INTERMEDIATE_PROMPT（为 v1.1 预留）
- [x] 2.2 修改 chatterbox/conversation/manager.py：构造函数接受 strategy 参数，根据策略选择对应 prompt

## 3. 配置更新

- [x] 3.1 修改 config.yaml：新增 conversation.strategy 字段，默认值 beginner
- [x] 3.2 修改 chatterbox/config.py：加载 conversation 配置项（无需修改，yaml 自动加载）
- [x] 3.3 修改 main.py：从配置读取 strategy，传递给 ConversationManager

## 4. 验证

- [x] 4.1 端到端测试：说中文验证显式翻译回复
- [x] 4.2 验证回复中无 emoji 且 TTS 不读出 emoji
