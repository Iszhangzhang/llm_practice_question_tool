"""
选择题处理模块
"""

from core.ui import wait_enter, print_separator, print_title


def run(problem:dict)-> None:
    """
    执行一道选择题的完整流程
        1. 展示题目和描述选项
        2. 可选的提示
        3. 接收用户答案
        4. 判定对错并显示解析
    :param problem:
    :return:
    """
    print_separator()
    print(f"题目：{problem['title']}")
    print(f"难度：{problem.get('difficulty', '')}")
    print(f"描述：{problem['description']}")
    print()
    print("选项： ")

    for opt in problem.get("options", []):
        print(f"{opt}")

    print_separator()
    print("（输入 hint 查看提示，输入选项字母作答）")

    # if problem.get("hint"):
    #     show_hint = input("是否需要提示？ （y/n 默认n）: ").strip().lower()
    #     if show_hint == 'y':
    #         print(f"提示：{problem['hint']}")
    #
    # user_answer = input("请输入你的答案（选项字母）： ").strip().upper()

    correct = problem.get("correct_answer", "").strip().upper()

    while True:
        user_answer = input("请输入你的答案（选项字母）： ").strip().upper()
        if user_answer.lower() == "hint":
            hint = problem.get("hint")
            if hint:
                print(f"提示： {hint}")
            else:
                print("该题目没有提示")
            continue
        if user_answer == correct:
            print("\n✅ 正确！")
        else:
            print(f"\n❌ 错误！正确答案是 {correct}。")

        explanation = problem.get("explanation")
        if explanation:
            print(f"解析：{explanation}")

        break

    wait_enter()