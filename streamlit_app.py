import streamlit as st

from core.problem_loader import list_problems
from core.config import get_type_display

st.set_page_config(page_title="LLM 刷题平台", page_icon="📚", layout="wide")


def init_session():
    defaults = {
        "page": "main_menu",  # 当前页面
        "category": None,  # 选中的类型
        "type_filter": None,  # 选中的题型过滤
        "all_filtered_problems": [],  # 过滤后的题目列表
        "current_index": 0,  # 当前题目索引
        "user_answer": "",  # 用户输入答案
        "show_hint": False,  # 是否显示提示
        "result": None,  # 本次答题结果
        "answered_map": {},
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def switch_page(page_name):
    st.session_state["page"] = page_name
    st.rerun()


def main_menu_page():
    """
    主菜单页面

    :return:
    """
    st.title("LLM 刷题平台")
    st.markdown("欢迎使用命令行刷题工具 web 版本")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("▶️ 开始刷题", use_container_width=True):
            switch_page("select_category")
    with col2:
        if st.button("📊 查看答题记录", use_container_width=True):
            st.info("答题记录功能开发中，敬请期待。")
    with col3:
        if st.button("❌ 退出", use_container_width=True):
            st.stop()   # 停止脚本（无菜单时显示空白）

def select_category_page():
    st.title("选择题目类别")
    all_problems = list_problems()
    if not all_problems:
        st.warning("暂无题目，请先添加题目")
        if st.button("🔙 返回主菜单"):
            switch_page("main_menu")
        return

    categories = sorted({p['category'] for p in all_problems})

    st.markdown("请选择你想练习的类别： ")

    cols = st.columns(2)

    for idx, cat in enumerate(categories):
        with cols[idx % 2]:
            if st.button(cat, key=f'cat_{idx}', use_container_width=True):
                st.session_state.category = cat
                switch_page("select_type")

    if st.button("🔙 返回主菜单"):
        switch_page("main_menu")

def select_type_page():
    st.title(f"选择题目类型 - {st.session_state.category}")

    category = st.session_state.category
    all_problems = list_problems(category = category)
    if not all_problems:
        st.warning(f"类别 {category} 下暂无题目。")
        if st.button("🔙 重新选择类别"):
            switch_page("select_category")
        return

    existing_types = sorted({p.get('type', "") for p in all_problems if p.get('type')})

    # selected_type = st.session_state.get("type_filter", None)

    st.markdown("请选择题型范围：")
    if st.button("全部题型", key="type_all", use_container_width=True):
        st.session_state.type_filter = None
        prepare_practice()
        switch_page("practice")

    for t in existing_types:
        type_cn = get_type_display(t)
        if st.button(type_cn, key=f"type_{t}", use_container_width=True):
            st.session_state.type_filter = t
            prepare_practice()
            switch_page("practice")

    if st.button("🔙 重新选择类别"):
        switch_page("select_category")

def prepare_practice():
    category = st.session_state.category
    type_filter = st.session_state.type_filter
    all_problems = list_problems(category=category)
    if type_filter is not None:
        filtered = [p for p in all_problems if p.get('type') == type_filter]
    else:
        filtered = all_problems

    filtered.sort(key=lambda p: p.get('id', ''))
    st.session_state.all_filtered_problems = filtered
    st.session_state.current_index = 0
    st.session_state.result = None
    st.session_state.show_hint = False

def go_back_to_type():
    """保留类别，清空刷题进度，返回题型选择页"""
    st.session_state.result = None
    st.session_state.show_hint = False
    st.session_state.all_filtered_problems = []
    st.session_state.current_index = 0
    st.session_state.answered_map = {}
    # 不清除 category，保留以便重新选题型
    st.session_state.type_filter = None
    st.session_state.page = "select_type"
    st.rerun()

# ====================== 刷题页面（选择题完整流程） ======================
def practice_page():
    category = st.session_state.category
    problems = st.session_state.all_filtered_problems
    total = len(problems)
    idx = st.session_state.current_index

    if total == 0:
        st.warning("没有可刷的题目。")
        if st.button("🔙 返回主菜单"):
            clear_practice_state()
            switch_page("main_menu")
        return

    # 当前题目
    problem = problems[idx]
    type_cn = get_type_display(problem.get('type'))

    # 侧边栏：进度与导航
    # with st.sidebar:
    #     st.subheader(f"📖 {category}")
    #     st.write(f"题型：{type_cn}")
    #     st.progress((idx + 1) / total, text=f"第 {idx + 1}/{total} 题")
    #     st.info(problem.get('knowledge_points', [])[0] if problem.get('knowledge_points') else "")

    with st.sidebar:
        st.subheader(f"📖 {category}")
        st.write(f"题型：{type_cn}")
        st.progress((idx + 1) / total, text=f"第 {idx + 1}/{total} 题")

        if problem.get('knowledge_points'):
            st.info(" | ".join(problem['knowledge_points']))

        st.markdown("---")
        st.caption("📋 题目导航")



        answered_map = st.session_state.answered_map
        # 构建 (索引, 显示标签) 对
        option_pairs = []
        for i, p in enumerate(problems):
            status_icon = get_status_icon(i, answered_map)
            short_title = (p['title'][:30] + '...') if len(p['title']) > 30 else p['title']
            option_pairs.append((i, f"{status_icon} {i + 1}. {short_title}"))

        selected_pair = st.selectbox(
            "选择题目",
            options=option_pairs,
            format_func=lambda pair: pair[1],  # pair[1] 是 str，明确无类型问题
            index=idx,
            key="nav_select"
        )

        selected_index = selected_pair[0]

        if st.button("📍 跳转到该题", use_container_width=True):
            go_to_question(selected_index)

        # 侧边栏底部：返回按钮
        st.sidebar.markdown("---")
        col_back1, col_back2 = st.sidebar.columns(2)
        with col_back1:
            if st.button("🔙 题型选择", use_container_width=True, key="sidebar_type"):
                go_back_to_type()
        with col_back2:
            if st.button("🏠 主菜单", use_container_width=True, key="sidebar_main"):
                clear_practice_state()
                switch_page("main_menu")

    # 主内容区
    st.title(f"{problem['title']}")
    st.caption(f"难度：{problem.get('difficulty', '未知')}")

    # 题目描述
    with st.expander("📄 题目描述", expanded=True):
        st.markdown(problem['description'])

    # 选项按钮（使用 radio 确保唯一选择）
    options = problem.get('options', [])
    option_letters = []
    if options:
        # 展示每个选项的代码（去除选项字母前缀）
        st.markdown("**选项：**")
        for opt in options:
            # 假设格式为 "A. <code>" 或 "A. \n<code>"
            if opt.startswith(("A. ", "B. ", "C. ", "D. ")):
                letter = opt[0]
                code_body = opt[3:].strip()
            else:
                letter = opt[0] if len(opt) > 1 else "?"
                code_body = opt[2:].strip() if len(opt) > 2 else opt
            option_letters.append(letter)
            st.caption(f"选项 {letter}")
            # 用 st.code 显示代码，保持高亮
            st.code(code_body, language="python")

        st.markdown("---")
        # 使用 radio 只选字母
        user_answer_key = f"user_answer_{idx}"
        selected_letter = st.radio(
            "选择你的答案：",
            options=option_letters,
            index=None,
            key=f"radio_{idx}",
            horizontal=True
        )
        if selected_letter:
            st.session_state[user_answer_key] = selected_letter
    else:
        st.warning("本题没有选项数据。")

    # Hint 按钮
    if problem.get('hint'):
        if st.button("💡 显示提示", key=f"hint_{idx}"):
            st.session_state.show_hint = True
    if st.session_state.show_hint:
        if problem.get('hint'):
            st.info(f"提示：{problem['hint']}")
        else:
            st.info("该题目没有提示。")

    # 提交按钮
    submit_disabled = st.session_state.get(f"user_answer_{idx}", "") == ""
    if st.button("✅ 提交答案", key=f"submit_{idx}", disabled=submit_disabled):
        handle_choice_submit(problem, st.session_state[f"user_answer_{idx}"])

    # 显示结果（若已提交）
    result = st.session_state.result
    if result:
        if result['is_correct']:
            st.success(f"✅ 正确！正确答案是 {result['correct_answer']}")
        else:
            st.error(f"❌ 错误！正确答案是 {result['correct_answer']}")
        with st.expander("📖 查看解析"):
            st.markdown(result['explanation'])

        # 下一题按钮
        col1, col2,col3 = st.columns(3)
        with col1:
            if st.button("➡️ 下一题", use_container_width=True):
                go_next_question()
        with col2:
            if st.button("🔙 题型选择", use_container_width=True, key="back_type_btn"):
                go_back_to_type()
        with col3:
            if st.button("🔙 返回主菜单", use_container_width=True):
                clear_practice_state()
                switch_page("main_menu")


def handle_choice_submit(problem, user_answer):
    """处理选择题提交：比对答案，存储结果"""
    correct = problem.get("correct_answer", "").strip().upper()
    user = user_answer.strip().upper()
    is_correct = (user == correct)

    st.session_state.result = {
        "is_correct": is_correct,
        "correct_answer": correct,
        "explanation": problem.get("explanation", "暂无解析。")
    }

    # 记录已答题状态
    st.session_state.answered_map[st.session_state.current_index] = (
        'correct' if is_correct else 'wrong'
    )

def go_next_question():
    """移动至下一题，循环"""
    st.session_state.current_index += 1
    if st.session_state.current_index >= len(st.session_state.all_filtered_problems):
        st.session_state.current_index = 0
    # 清除当前题目的提交状态
    st.session_state.result = None
    st.session_state.show_hint = False
    st.session_state.pop('nav_select', None)
    st.rerun()

def get_status_icon(idx, answered_map):
    """根据答题记录返回图标"""
    if idx not in answered_map:
        return "⬜"
    return "✅" if answered_map[idx] == 'correct' else "❌"

def go_to_question(idx):
    """跳转到指定题目（索引基于 filtered 列表）"""
    st.session_state.current_index = idx
    st.session_state.result = None
    st.session_state.show_hint = False
    st.session_state.pop('nav_select', None)
    st.rerun()


def clear_practice_state():
    """离开刷题时清理相关状态"""
    st.session_state.result = None
    st.session_state.show_hint = False
    st.session_state.all_filtered_problems = []
    st.session_state.current_index = 0
    st.session_state.answered_map = {}

def main():
    init_session()

    page = st.session_state.page
    if page == "main_menu":
        main_menu_page()
    elif page == "select_category":
        select_category_page()
    elif page == "select_type":
        select_type_page()
    elif page == "practice":
        practice_page()
    else:
        st.error("未知页面")
        main_menu_page()

if __name__ == "__main__":
    main()