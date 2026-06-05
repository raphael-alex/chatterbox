import re


# Emoji Unicode 范围的正则表达式
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"  # enclosed characters
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA00-\U0001FA6F"  # chess symbols
    "\U0001FA70-\U0001FAFF"  # symbols extended-A
    "\U00002600-\U000026FF"  # misc symbols
    "\U0000FE00-\U0000FE0F"  # variation selectors
    "\U0000200D"             # zero width joiner
    "\U00002B50"             # star
    "\U0000203C-\U00003299"  # other misc
    "]+",
    flags=re.UNICODE,
)


def clean_for_tts(text: str) -> str:
    """过滤 emoji 和非语音字符，返回适合 TTS 朗读的文本。

    - 移除 emoji
    - 移除方括号标记（保留方括号内的文字内容）
    - 移除 <SAVE_PROFILE:...> 标记
    - 合并多余空格
    - 去除首尾空白
    """
    text = _EMOJI_PATTERN.sub("", text)
    text = text.replace("[", "").replace("]", "")
    text = re.sub(r"<SAVE_PROFILE:.+?>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
