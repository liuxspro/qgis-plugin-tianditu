import re
from dataclasses import dataclass

KEY_LENGTH = 32
_KEY_PATTERN = re.compile(r"^[A-Za-z0-9]+$")


@dataclass(frozen=True)
class KeyCheckResult:
    is_valid: bool
    message: str = ""


def check_key_format(key: str) -> KeyCheckResult:
    """检查天地图 key 的格式

    Args:
        key: 天地图 key

    Returns:
        KeyCheckResult: 校验结果，不合法时 message 为具体原因
    """
    if not key:
        return KeyCheckResult(False, "请输入 Key")
    if len(key) != KEY_LENGTH:
        return KeyCheckResult(
            False, f"Key 长度应为 {KEY_LENGTH} 位，当前 {len(key)} 位"
        )
    if not _KEY_PATTERN.match(key):
        return KeyCheckResult(False, "Key 只能包含字母和数字")
    return KeyCheckResult(True)


def mask_key(key: str) -> str:
    """隐藏 key 的后半部分，用于界面展示"""
    return f"{key[:8]}****{key[-4:]}" if len(key) > 12 else f"{key[:8]}****"
