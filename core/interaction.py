"""
交互控制器 - 主菜单、刷题流程调度
【整体功能】刷题工具的“大脑/调度中心”
【核心职责】：
    1. 显示主菜单
    2. 让用户选择题目类型
    3. 让用户选择具体题目
    4. 根据题型自动分发但对应的做题逻辑（选择/编码/简答）
    5. 控制整个交互流程： 菜单-》选题-》做题-》返回菜单

【架构分层】：
    UI层：打印标题、分割线、等待回车
    数据线：加载题目、按条件查询题目
    业务处理层：处理选择题/编码题/简答题逻辑
    控制层：本文件，负责流程调度

"""

# 导入题目加载工具：列出所有题目、根据ID获取单题
from core.problem_loader import list_problems
from core.config import get_type_display

# 导入三种题型的处理器：处理选择、编码、简答题
from core.handlers import choice, coding, short_answer
from core.ui import print_title, print_separator, wait_enter, select_index


def display_main_menu() -> None:
    """
    展示程序主菜单
    无返回值，纯输出函数
    """
    print_title("刷题工具")
    print("1. 开始刷题")
    print("2. 查看答题记录")
    print("3. 退出")
    print_separator()


def select_category() -> str | None:
    """
    列出所有类别供用户选择，返回类别名或None
        1. 获取所有题目
        2. 无题目时直接返回
        3. 提取所有不重复的分类（集合自动去重），并排序
        4. 展示分类列表
        5. 获取用户输入并处理
        6. 尝试将输入转为数字，处理合法选择
        7. 输入无效，递归重新调用
    """
    # 1.获取所有题目
    all_problems = list_problems()

    # 2.无题目时直接返回
    if not all_problems:
        print("暂无题目，请先添加题目")
        return None

    # 3.提取所有不重复的分类（集合自动去重），并排序
    categories = sorted({p['category'] for p in all_problems})

    # 4.展示分类列表
    print_title("类型类别")

    for idx, cat in enumerate(categories, 1):
        print(f"{idx}. {cat}")
    print("0. 返回主菜单")

    # 5.获取用户输入并处理
    choice = input("请输入序号： ".strip())
    if choice == '0':
        return None

    # 6.尝试将输入转为数字，处理合法选择
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(categories):
            return categories[idx]
    except ValueError:
        pass

    # 7.输入无效，递归重新调用
    print("输入无效，请重试")
    return select_category()

def handle_problem(problem: dict) -> None:
    """
    根据题目类型分发到对应的处理器
    """
    try:
        ptype = problem.get('type')
        if ptype == 'choice':
            choice.run(problem)
        elif ptype == 'coding':
            coding.run(problem)
        elif ptype == 'short_answer':
            short_answer.run(problem)
        else:
            print_title(f"未知题型： {ptype}")
            wait_enter()
    except Exception as e:
        print(f"做题时出错：{e}")
        wait_enter()

def practice_loop() -> None:
    """
    刷题主循环: 选类别 -》 选题 -》 做题
        1. 外层循环，选择分类
        2. 内层循环，返回题目并做题
    """

    category = select_category()
    if category is None:
        return

    all_problems = list_problems(category=category)
    if not all_problems:
        print(f"类别 {category} 下暂无题目")
        wait_enter()
        return

    all_problems.sort(key=lambda p:p.get('id',''))
    existing_types = sorted({p.get('type',"") for p in all_problems if p.get('type')})


    filter_options = [get_type_display(None)]
    filter_mapping = [None]
    for t in existing_types:
        filter_options.append(get_type_display(t))
        filter_mapping.append(t)
    print_title(f"{category} - 选择题目类型")
    filter_idx = select_index(filter_options, "请选择类型", "返回上一级")
    if filter_idx is None:
        return
    selected_type = filter_mapping[filter_idx]

    if selected_type is not None:
        filtered_problems = [p for p in all_problems if p.get('type') == selected_type]
    else:
        filtered_problems = all_problems
    type_display = get_type_display(selected_type)

    if not filtered_problems:
        print(f"该类别下暂无 {type_display} 题目。")
        wait_enter()
        return
    total = len(filtered_problems)

    problem_options = []
    for p in filtered_problems:
        type_cn = get_type_display(p.get('type'))
        problem_options.append(f"[{type_cn}] {p['title']} ({p.get('difficulty', '')})")

    print_title(f"{category} - 题目列表（共 {total} 题）")
    start_idx = select_index(problem_options, "请选择起始题号", "返回主菜单")

    if start_idx is None:
        return

    current_index = start_idx
    print(f"\n当前模式：{category} - {type_display}，从第 {start_idx + 1} 题开始。")
    print("答题时输入 0 可退出。")
    while True:
        problem = filtered_problems[current_index]
        type_cn = get_type_display(problem.get('type'))
        print(f"\n--- 第{current_index + 1}/{total} 题 ---")
        print(f"[{type_cn}] {problem['title']} ({problem.get('difficulty', '')})")

        user_input = input("按回车开始答题， 输入0退出")
        if user_input == '0':
            break

        handle_problem(problem)
        current_index += 1
        if current_index >= total:
            current_index = 0
            print("\n 已经刷完一轮，重新从第一题开始。")
            cont = input("按回车键继续，输入0退出： ").strip()
            if cont == '0':
                break

def start() -> None:
    """
    启动交互式程序
        1. 死循环，一直显示菜单，直到用户选择退出

    """
    while True:
        display_main_menu()
        choice = input("请输入操作序号：").strip()
        if choice == '1':
            practice_loop()
        elif choice == '2':
            print("答题记录功能开发中，敬请期待")
            wait_enter()
        elif choice == '3':
            print("感谢使用，再见")
            break
        else:
            print("输入无效，请重新选择(1/2/3)")

