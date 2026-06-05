import os
import yaml
from pathlib import Path


DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.yaml"
USER_CONFIG_PATH = Path("config.yaml")


def load_config() -> dict:
    """加载配置，优先级：环境变量 > 用户 config.yaml > 默认 config.yaml"""
    config_path = USER_CONFIG_PATH if USER_CONFIG_PATH.exists() else DEFAULT_CONFIG_PATH
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 环境变量替换 ${VAR_NAME}
    config = _resolve_env_vars(config)

    # 校验必填项
    _validate(config)

    return config


def _resolve_env_vars(obj):
    """递归替换 ${VAR_NAME} 为环境变量值"""
    if isinstance(obj, str):
        if obj.startswith("${") and obj.endswith("}"):
            env_name = obj[2:-1]
            return os.environ.get(env_name, "")
        return obj
    if isinstance(obj, dict):
        return {k: _resolve_env_vars(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_resolve_env_vars(item) for item in obj]
    return obj


def _validate(config: dict):
    """校验必填配置项"""
    errors = []

    asr_engine = config.get("asr", {}).get("engine")
    if asr_engine == "whisper-api":
        api_key = config.get("asr", {}).get("whisper_api", {}).get("api_key")
        if not api_key:
            errors.append("asr.whisper_api.api_key 未设置 (请设置 OPENAI_API_KEY 环境变量)")

    llm_engine = config.get("llm", {}).get("engine")
    if llm_engine == "openai":
        api_key = config.get("llm", {}).get("openai", {}).get("api_key")
        if not api_key:
            errors.append("llm.openai.api_key 未设置 (请设置 OPENAI_API_KEY 环境变量)")
    elif llm_engine == "deepseek":
        api_key = config.get("llm", {}).get("deepseek", {}).get("api_key")
        if not api_key:
            errors.append("llm.deepseek.api_key 未设置 (请设置 DEEPSEEK_API_KEY 环境变量)")

    if errors:
        raise ValueError("配置校验失败:\n" + "\n".join(f"  - {e}" for e in errors))
