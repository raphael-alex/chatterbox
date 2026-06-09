"""用户画像收集与持久化"""

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass
class EnglishLevel:
    vocabulary: str = "beginner"        # "beginner" | "intermediate" | "advanced"
    grammar_accuracy: float = 0.0      # 0.0 - 1.0
    sentence_diversity: str = "basic"   # "basic" | "intermediate" | "advanced"
    last_assessed: str = ""             # ISO date

    def to_dict(self) -> dict:
        return {
            "vocabulary": self.vocabulary,
            "grammar_accuracy": self.grammar_accuracy,
            "sentence_diversity": self.sentence_diversity,
            "last_assessed": self.last_assessed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EnglishLevel":
        return cls(
            vocabulary=data.get("vocabulary", "beginner"),
            grammar_accuracy=float(data.get("grammar_accuracy", 0.0)),
            sentence_diversity=data.get("sentence_diversity", "basic"),
            last_assessed=data.get("last_assessed", ""),
        )


@dataclass
class UserProfile:
    name: str = ""
    age: int | None = None
    interests: list[str] = field(default_factory=list)
    created_at: str = ""
    last_chat: str = ""
    safety_events: list = field(default_factory=list)  # [{category, keyword, user_input, timestamp}, ...]
    english_level: EnglishLevel | None = None
    repetition_count: int = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "age": self.age,
            "interests": self.interests,
            "created_at": self.created_at,
            "last_chat": self.last_chat,
            "safety_events": self.safety_events,
            "english_level": self.english_level.to_dict() if self.english_level else None,
            "repetition_count": self.repetition_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        english_level = None
        if data.get("english_level"):
            english_level = EnglishLevel.from_dict(data["english_level"])
        return cls(
            name=data.get("name", ""),
            age=data.get("age"),
            interests=data.get("interests", []),
            created_at=data.get("created_at", ""),
            last_chat=data.get("last_chat", ""),
            safety_events=data.get("safety_events", []),
            english_level=english_level,
            repetition_count=data.get("repetition_count", 0),
        )

    @property
    def is_complete(self) -> bool:
        return bool(self.name)


PROFILES_DIR = Path.home() / ".chatterbox"
PROFILES_FILE = PROFILES_DIR / "profiles.json"


class ProfileStore:
    """本地 JSON 文件的用户画像存储"""

    def __init__(self, path: Path = PROFILES_FILE):
        self._path = path

    def get_default(self) -> UserProfile | None:
        """获取默认用户画像，不存在则返回 None"""
        data = self._load()
        if "default" not in data:
            return None
        return UserProfile.from_dict(data["default"])

    def save_default(self, profile: UserProfile):
        """保存默认用户画像"""
        data = self._load()
        data["default"] = profile.to_dict()
        self._save(data)

    def update_last_chat(self, profile: UserProfile):
        """更新最后聊天时间并保存"""
        profile.last_chat = date.today().isoformat()
        self.save_default(profile)

    def _load(self) -> dict:
        if not self._path.exists():
            return {}
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _save(self, data: dict):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
