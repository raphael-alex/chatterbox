## ADDED Requirements

### Requirement: 翻译与回复生成
系统 SHALL 将用户的中文或英文输入翻译为英文，并生成自然、适合儿童的英语对话回复。回复中自然融入翻译内容，不使用机械的 "You just said..." 模式。

#### Scenario: 用户说中文
- **WHEN** 用户输入 "我喜欢恐龙"
- **THEN** 系统生成英文回复，自然融入翻译，如 "Oh, you like dinosaurs! Which one is your favorite?"

#### Scenario: 用户说英文
- **WHEN** 用户输入 "I like cats"
- **THEN** 系统生成英文回复延续对话，如 "Cats are so cute! Do you have a cat at home?"

#### Scenario: 用户中英混合
- **WHEN** 用户输入 "我喜欢 dinosaur"
- **THEN** 系统生成英文回复，如 "Dinosaurs are awesome! Which dinosaur do you like best?"

### Requirement: 回复风格适合儿童
系统 SHALL 使用简单词汇和简短句子（1-2 句）生成回复，语气鼓励、友好、适合儿童理解。

#### Scenario: 简单词汇回复
- **WHEN** 用户输入任何内容
- **THEN** 系统使用基础英语词汇生成回复，避免复杂句式和生僻词汇

#### Scenario: 鼓励性回复
- **WHEN** 用户表达喜好或成就
- **THEN** 系统在回复中包含鼓励性表达，如 "That's cool!" "Awesome!" "Great!"

### Requirement: 对话上下文保持
系统 SHALL 在单次会话内保持对话上下文，支持多轮对话。

#### Scenario: 多轮对话
- **WHEN** 用户说 "我喜欢恐龙" 后系统回复 "Oh, you like dinosaurs! Which one is your favorite?"，用户再说 "霸王龙"
- **THEN** 系统基于上下文理解 "霸王龙" 是对上一轮问题的回答，生成如 "T-Rex is so cool! It's the king of dinosaurs!" 的回复

#### Scenario: 会话重置
- **WHEN** 程序重新启动
- **THEN** 对话上下文清空，开始全新会话

### Requirement: LLM 引擎可配置
系统 SHALL 支持通过配置文件切换 LLM 引擎，至少支持 OpenAI API 和 DeepSeek API。

#### Scenario: 使用 OpenAI API
- **WHEN** 配置文件中 LLM 引擎设置为 "openai"
- **THEN** 系统使用 OpenAI API 生成回复

#### Scenario: 使用 DeepSeek API
- **WHEN** 配置文件中 LLM 引擎设置为 "deepseek"
- **THEN** 系统使用 DeepSeek API 生成回复
