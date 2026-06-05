## Requirements

### Requirement: 翻译与回复生成
系统 SHALL 将用户的中文或英文输入翻译为英文，并生成自然、适合儿童的英语对话回复。当用户输入中文时，LLM SHALL 返回 `[翻译内容] 回复内容` 格式，方括号内为中文的英文翻译，方括号后为回复。当用户输入英文时，LLM SHALL 检查语法错误并在回复中自然融入正确表达。回复中自然融入翻译内容，不使用机械的 "You just said..." 模式。

#### Scenario: 用户说中文
- **WHEN** 用户输入 "我喜欢恐龙"
- **THEN** LLM 返回格式如 "[I like dinosaurs!] Oh, you like dinosaurs! Which one is your favorite?"

#### Scenario: 用户说英文（语法正确）
- **WHEN** 用户输入 "I like cats"
- **THEN** LLM 返回英文回复延续对话，如 "Cats are so cute! Do you have a cat at home?"

#### Scenario: 用户说英文（语法错误）
- **WHEN** 用户输入 "I goed to school"
- **THEN** LLM 返回融入纠正的回复，如 "Oh, you went to school! What did you do there?"

#### Scenario: 用户中英混合
- **WHEN** 用户输入 "我喜欢 dinosaur"
- **THEN** LLM 返回格式如 "[I like dinosaurs!] Dinosaurs are awesome! Which dinosaur do you like best?"

### Requirement: 回复风格适合儿童
系统 SHALL 使用简单词汇和简短句子（1-2 句）生成回复，语气鼓励、友好、适合儿童理解。

#### Scenario: 简单词汇回复
- **WHEN** 用户输入任何内容
- **THEN** 系统使用基础英语词汇生成回复，避免复杂句式和生僻词汇

#### Scenario: 鼓励性回复
- **WHEN** 用户表达喜好或成就
- **THEN** 系统在回复中包含鼓励性表达，如 "That's cool!" "Awesome!" "Great!"

### Requirement: 对话上下文保持
系统 SHALL 在单次会话内保持对话上下文，支持多轮对话。`_try_extract_profile_from_history` 函数 SHALL 接受可选的 `llm` 参数，当正则匹配无法提取 name 或 age 时，使用 LLM 兜底提取。LLM 提取调用 SHALL 使用独立 prompt，结果 SHALL NOT 写入对话历史。

#### Scenario: 多轮对话
- **WHEN** 用户说 "我喜欢恐龙" 后系统回复 "Oh, you like dinosaurs! Which one is your favorite?"，用户再说 "霸王龙"
- **THEN** 系统基于上下文理解 "霸王龙" 是对上一轮问题的回答，生成如 "T-Rex is so cool! It's the king of dinosaurs!" 的回复

#### Scenario: 会话重置
- **WHEN** 程序重新启动
- **THEN** 对话上下文清空，开始全新会话

#### Scenario: LLM 提取不影响对话历史
- **WHEN** LLM 兜底提取被触发并成功返回画像信息
- **THEN** LLM 提取的请求和响应 SHALL NOT 出现在 `conversation.messages` 中

### Requirement: 画像提取函数支持 LLM 参数
`_try_extract_profile_from_history` 函数 SHALL 接受可选的 `llm` 参数（默认 `None`）。当 `llm` 不为 `None` 且正则匹配后仍缺少 name 或 age 时，SHALL 调用 LLM 进行兜底提取。

#### Scenario: 传入 llm 参数
- **WHEN** `_try_extract_profile_from_history(conversation, profile_store, llm=llm)` 被调用且 profile 缺少 name
- **THEN** 系统在正则扫描后调用 LLM 兜底提取

#### Scenario: 不传入 llm 参数
- **WHEN** `_try_extract_profile_from_history(conversation, profile_store)` 被调用（llm=None）
- **THEN** 系统仅执行正则扫描，行为与修改前完全一致

### Requirement: LLM 引擎可配置
系统 SHALL 支持通过配置文件切换 LLM 引擎，至少支持 OpenAI API 和 DeepSeek API。

#### Scenario: 使用 OpenAI API
- **WHEN** 配置文件中 LLM 引擎设置为 "openai"
- **THEN** 系统使用 OpenAI API 生成回复

#### Scenario: 使用 DeepSeek API
- **WHEN** 配置文件中 LLM 引擎设置为 "deepseek"
- **THEN** 系统使用 DeepSeek API 生成回复
