"""内容安全关键词分类（占位符，待填充）"""

CATEGORIES = {
    "violence": [
        # TODO: 暴力类关键词
        "kill",
        "killing",
        "killed",
        "murder",
        "dead",
        "death",
        "die",
        "hurt",
        "injure",
        "injury",
        "weapon",
        "gun",
        "knife",
        "shoot",
        "blood",
        "bloody",
        "fight",
        "attack",
        "hit",
        "beat",
        "torture",
        "destroy",
        "bomb",
        "explosion",
        "war",
    ],
    "pornography": [
        # TODO: 色情类关键词
        "sex",
        "sexual",
        "naked",
        "nude",
        "breast",
        "penis",
        "vagina",
        "orgasm",
        "porn",
        "xxx",
        "erotic",
        "strip",
        "underwear",
    ],
    "anti_social": [
        # TODO: 反社会类关键词
        "hate",
        "kill people",
        "destroy",
        "bomb",
        "terrorist",
        "terror",
        "attack people",
        "hurt people",
        "riot",
        "violence",
        "abuse",
    ],
    "cult": [
        # TODO: 邪教/迷信类关键词
        "cult",
        "邪教",
        "法轮功",
        "全能神",
        "呼喊派",
        "门徒会",
    ],
}

CONSOLE_MESSAGES = {
    "violence": "It sounds like something upset you. Let's talk about something fun instead!",
    "pornography": "That's not something we talk about. Tell me about something you like!",
    "anti_social": "Everyone deserves to be treated with kindness. What made you feel that way?",
    "cult": "Interesting! Let's talk about something else — what's your favorite hobby?",
}
