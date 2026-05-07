"""
全局配置模块
"""

TYPE_DISPLAY_MAP: dict[str, str] = {
    "choice": "选择题",
    "coding": "编码题",
    "short_answer": "简答题",
}
def get_type_display(type_key: str | None) -> str:
    """
    安全获取题型的中文显示名称。
    若传入 None 或空字符串，返回 '全部题型'；
    若传入未知类型，返回原值；
    否则返回中文映射。
    """
    if not type_key:
        return "全部题型"
    return TYPE_DISPLAY_MAP.get(type_key, type_key)