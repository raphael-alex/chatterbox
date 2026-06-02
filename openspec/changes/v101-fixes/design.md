## Context

v1.0 已完成端到端测试，发现三个需修复的问题：emoji 被 TTS 读出、prompt 策略不符合目标用户需求、缺少 TTS 文本预处理。当前代码中 `prompt.py` 有一个硬编码的 SYSTEM_PROMPT，`edge_tts.py` 的 synthesize 方法直接将 LLM 原始输出传给 TTS，没有文本清理。

## Goals / Non-Goals

**Goals:**
- 消除 TTS 读出 emoji 的问题
- 将默认 prompt 策略改为显式翻译模式，匹配初学者需求
- 为 v1.1 多策略支持预留接口（config + ConversationManager 参数）
- TTS 合成前增加文本预处理兜底

**Non-Goals:**
- 实现多策略切换（v1.1）
- 交互模式切换（v1.2）
- 学习目标系统（v1.3）
- 词汇追踪

## Decisions

### 1. Emoji 处理：Prompt 禁止 + TTS 过滤双重保障

**选择**: prompt 中明确禁止 emoji + TTS 合成前正则过滤 emoji。

**理由**: LLM 不一定 100% 遵守"不用 emoji"的指令，必须有 TTS 层兜底。双重保障确保即使 LLM 偶尔输出 emoji，TTS 也不会读出来。

**备选**: 仅 prompt 禁止 / 仅 TTS 过滤——单层保障不够可靠。

### 2. 显式翻译策略的 prompt 设计

**选择**: 修改 prompt，要求 LLM 在用户说中文时，先用英文重述用户的意思，再回答问题。

**理由**: v1.0 目标用户是英语水平不高的家庭，孩子需要明确听到中文→英文的对应关系，这是核心教育价值。"自然融入翻译"策略更适合中级以上用户（v1.1 实现）。

**prompt 结构**:
```
用户说中文 → [英文翻译/重述] + [思考停顿] + [回答]
用户说英文 → [直接互动回应]
```

### 3. 策略参数化预留

**选择**: config.yaml 新增 `conversation.strategy` 字段，ConversationManager 构造函数接受 strategy 参数。

**理由**: 为 v1.1 多策略做准备，但 v1.0.1 只实现 `beginner` 一种策略。接口先定义好，后续加策略只加 prompt 常量即可。

### 4. TTS 文本预处理工具

**选择**: 新增 `chatterbox/tts/preprocessing.py`，提供 `clean_for_tts(text) -> str` 函数，过滤 emoji 和非语音字符。

**理由**: 文本预处理是独立关注点，和具体 TTS 引擎无关，单独模块便于复用和测试。

## Risks / Trade-offs

- **[显式翻译可能显得啰嗦]** 初学者策略的回复会偏长 → 用 prompt 控制"翻译部分简短，1 句话即可"
- **[正则过滤 emoji 可能误杀]** 某些 Unicode 字符可能被误判 → 使用成熟的 emoji 库或保守的正则，只过滤明确的 emoji 范围
