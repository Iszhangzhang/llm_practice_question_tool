"""
LLM LeetCode CLI 入
LLM LeetCode CLI - Entry point
A command-line tool for practicing LLM application development

这是一个 命令行工具 的入口文件
作用：帮助练习 LLM 应用开发

架构：命令行解析层 -》业务逻辑层-》数据加载层
"""

# 导入命令行参数解析库 argparse
import argparse
from core.problem_loader import list_problems
from core.interaction import start
from core.config import get_type_display

# defaultdict 增强字典 访问不存在的key时不会报错,而是自动创建默认值
from collections import defaultdict

def handle_list(args)->None:
    """
    处理 '--list' 参数的核心逻辑
    功能：根据筛选条件获取题目 按类别，按题型分类 格式化打印
    """
    problems = list_problems(category=args.category, problem_type=args.type)

    if not problems:
        print("没有找到符合条件的题目")
        return

    grouped = defaultdict(list)
    for p in  problems:
        category = p.get("category", "未分类")
        grouped[category].append(p)

    for cat, probs in grouped.items():
        print(f"\n [{cat}] 共{len(probs)} 道题")
        type_order = defaultdict(list)
        for pb in probs:
            problem_type = pb.get("type", "unknown")
            type_order[problem_type].append(pb)

        for t, tprobs in type_order.items():
            type_cn = get_type_display(t)
            print(f"{type_cn} ({len(tprobs)}道)：")
            for prob in tprobs:
                print(f"[{prob['id']}] {prob['title']} (难度：{prob.get('difficulty','')})")


def main():
    """
    解析命令行参数，根据参数执行具体功能
        1. 定义命令行参数(用户可以输入什么指令)
        2. 解析用户输入的命令
        3. 根据指令调用对应的功能
        4. 对题目数据进行分组、美化展示
    """

    # -----------------------1、命令行解析器----------------------
    # 创建命令行解析器
    # 创建 ArgumentParser 对象，用于接受命令行输入
    parser = argparse.ArgumentParser(
        description="命令行刷题工具-专注技术能力训练"
    )

    # 定义命令行参数
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有题目"
    )

    parser.add_argument(
        "--category",
        type=str,
        help="按类别筛选"
    )

    parser.add_argument(
        "--type",
        type=str,
        choices=["choice", "coding", "short_answer"],
        help="按题型筛选"
    )

    # ---------------------2. 解析命令行参数
    # 解析命令行输入的参数
    args = parser.parse_args()

    # 根据参数执行逻辑
    if args.list:
        handle_list(args)
    else:
        start()

if __name__ == "__main__":
    main()