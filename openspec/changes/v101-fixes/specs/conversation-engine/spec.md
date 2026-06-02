## MODIFIED Requirements

### Requirement: 翻译与回复生成
系统 SHALL 将用户的中文输入翻译为英文，并生成自然、适合儿童的英语对话回复。当用户说中文时，系统 SHALL 先用英文重述/翻译用户的意思，再回答问题，让孩子明确听到中文对应的英文表达。

#### Scenario: 用户说中文（显式翻译）
- **WHEN** 用户输入 "今天星期几"
- **THEN** 系统生成包含翻译和回答的英文回复，如 "You're asking what day is it today? Let me see... it's Tuesday!"

#### Scenario: 用户说英文（直接互动）
- **WHEN** 用户输入 "I like cats"
- **THEN** 系统直接用英文回复，不需要翻译，如 "Cats are so cute! Do you have a cat at home?"

#### Scenario: 用户中英混合
- **WHEN** 用户输入 "我喜欢 dinosaur"
- **THEN** 系统生成英文回复，翻译中文部分并回应，如 "You like dinosaurs! Which one do you like best?"

### Requirement: 回复风格适合儿童
系统 SHALL 使用简单词汇和简短句子生成回复，语气鼓励、友好、适合儿童理解。回复中 SHALL NOT 包含 emoji。

#### Scenario: 无 emoji 回复
- **WHEN** 系统生成任何回复
- **THEN** 回复文本中不包含 emoji 字符

#### Scenario: 鼓励性回复
- **WHEN** 用户表达喜好或成就
- **THEN** 系统在回复中包含鼓励性表达，如 "That's cool!" "Awesome!" "Great job!"

### Requirement: LLM 引擎可配置
系统 SHALL 支持通过配置文件切换 LLM 引擎，至少支持 OpenAI API 和 DeepSeek API。

#### Scenario: 使用 OpenAI API
- **WHEN** 配置文件中 LLM 引擎设置为 "openai"
- **THEN** 系统使用 OpenAI API 生成回复

#### Scenario: 使用 DeepSeek API
- **WHEN** 配置文件中 LLM 引擎设置为 "deepseek"
- **THEN** 系统使用 DeepSeek API 生成回复

## ADDED Requirements

### Requirement: 对话策略可配置
系统 SHALL 支持通过配置文件设置对话策略。v1.0.1 仅支持 `beginner` 策略（显式翻译模式），为后续版本预留策略扩展接口。

#### Scenario: 使用 beginner 策略
- **WHEN** 配置文件中 conversation.strategy 设置为 "beginner"
- **THEN** 系统使用显式翻译模式的 prompt 生成回复

#### Scenario: 未设置策略
- **WHEN** 配置文件中未设置 conversation.strategy
- **THEN** 系统默认使用 "beginner" 策略
