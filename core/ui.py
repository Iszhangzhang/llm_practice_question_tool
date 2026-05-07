"""
用户界面模块
"""

def print_separator():
    """打印分割线"""
    print("-" * 40)

def print_title(title:str):
    print(f"\n===== {title} =====")

def wait_enter():
    input("\n 按回车键继续...")

def select_index(options:list,
                 prompt:str = "请选择题号", zero_text:str = "返回",
                 max_per_page:int = 0) -> int|None:
    total = len(options)
    if total == 0:
        print("没有可选项。")
        return None

    for idx, opt in enumerate(options, 1):
        print(f"{idx}.{opt}")
    print(f"0. {zero_text}")

    while True:
        choice = input(f"{prompt}: ").strip()

        if choice == "0":
            return None
        try:
            idx = int(choice)- 1
            if 0 <= idx < total:
                return idx
            print(f"序号超出范围（1-{total}），请重新输入。")
        except ValueError:
            print("输入无效，请输入数字序号")
