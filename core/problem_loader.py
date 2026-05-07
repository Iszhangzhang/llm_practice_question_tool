"""
Problem loader Modules
负责从problem/目录加载所有的Json文件，并提供查询功能
处理题目数据的读取、解析、查询
"""

# JSON处理库 （读取json文件）
import json

# Path类：python现代化路径处理工具（跨平台 比os.path更好用）
from pathlib import Path

# 导入类型注解工具：给函数返回值、参数加类型提示
from typing import List,Dict,Optional

# problems目录的路径（基于项目根目录）
# Path(__file_) 当前文件
# .parent上一级目录
PROBLEM_PATH = Path(__file__).parent.parent / "problems"

_cached_problems:Optional[List[Dict]] = None

def _get_problem_file() -> List[Path]:
    """
    获取problems目录下所有扩展名为.json的文件路径
    使用Path.glob匹配所有的*.json文件
    """
    # 调试：直接列出所有匹配的文件
    matched = list(PROBLEM_PATH.rglob("*.json"))
    return sorted(matched)

def load_all_problems()->List[Dict]:
    """
    加载全部题目的数据，存入列表并返回
    如果某个json文件格式有误，打印错误并跳过该文件
        1. 遍历所有json文件
        2. 读取并解析成python字典
        3. 存入列表返回
        4. 自带异常处理
    :return 列表，里面每一个元素都是一个题目字典
    """

    # 储存所有题目数据
    global _cached_problems

    # if _cached_problems is not None:
    #     return _cached_problems

    problems = []

    for file_path in _get_problem_file():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # 把文件内容转换成python 字典，列表
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(data, list):
                            problems.append(item)
                elif isinstance(data, dict):
                    problems.append(data)
                else:
                    print(f"Warning: Unknown format in {file_path}, skipped.")
        # 捕获 JSON格式错误（比如少写逗号、括号不匹配等）
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid Json in {file_path}, skipped. Error:{e}")
        # 捕获其他所有错误（权限不足，文件损坏等）
        except Exception as e:
            print(f"Warning: Failed to load {file_path}, skipped. Error:{e}")
            pass
    _cached_problems = problems

    return problems  # 返回所有题目

def list_problems(category:Optional[str] = None, problem_type: Optional[str] = None) -> List[Dict]:
    """
    返回问题列表的简要信息（id，title，difficulty） 用于cli展示
    实际实现中可复用    load_all_problems 但只取关键字段
    """
    problems  = load_all_problems()

    if category:
        problems = [p for p in problems if p.get("category") == category]
    if problem_type:
        problems = [p for p in problems if p.get("type") == problem_type]
    return problems

def get_problem_by_id(problem_id: int) ->Optional[Dict]:
    """
    根据题目id查询题目
    :param problem_id: 数字类型，题目id
    :return:
    """
    for problem in load_all_problems():
        if problem.get("id") == problem_id:
            return problem
    return None
