## Why

v1.0 端到端测试发现了三个问题：(1) LLM 回复中包含 emoji，TTS 会逐字读出来，体验很差；(2) 当前 prompt 策略是"自然融入翻译"，但 v1.0 目标用户是英语水平不高的家庭，孩子需要明确听到中文对应的英文表达；(3) TTS 缺少文本预处理，emoji 等非语音字符没有兜底过滤。

## What Changes

- 修改系统 prompt，禁止 LLM 回复中使用 emoji
- 修改默认 prompt 策略从"自然融入翻译"改为"显式翻译"——当用户说中文时，先翻译再回答
- 新增 TTS 文本预处理，在合成前过滤 emoji 和非语音字符
- 新增 `conversation` 配置项，支持 `strategy` 字段（当前仅 `beginner`，为 v1.1 多策略预留接口）

## Capabilities

### New Capabilities

- `text-preprocessing`: TTS 合成前的文本预处理——过滤 emoji、非语音字符，确保 TTS 只处理可朗读的文本

### Modified Capabilities

- `conversation-engine`: 修改默认 prompt 策略为显式翻译模式；prompt 模板支持策略参数化（为 v1.1 多策略预留）
- `voice-pipeline`: TTS 合成流程增加文本预处理步骤

## Impact

- `chatterbox/conversation/prompt.py` — 重写 SYSTEM_PROMPT，新增策略常量
- `chatterbox/conversation/manager.py` — 构造函数接受 strategy 参数
- `chatterbox/tts/edge_tts.py` — synthesize 方法增加文本预处理调用
- `config.yaml` — 新增 conversation.strategy 配置项
- `main.py` — 传递 strategy 参数给 ConversationManager
