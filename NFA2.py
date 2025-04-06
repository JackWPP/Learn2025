import re
import graphviz
import io
from PIL import Image
import gradio as gr
from collections import defaultdict

class State:
    def __init__(self, id):
        self.id = id
        self.transitions = {}  # 字符到目标状态列表的映射
        self.is_end = False
        self.epsilon_transitions = []  # ε转移的目标状态列表

    def __repr__(self):
        return f"State({self.id})"

class NFA:
    def __init__(self):
        self.states = []
        self.start_state = None
        self.end_states = []
        self.alphabet = set()  # 输入符号集合

    def add_state(self, state):
        self.states.append(state)
        return state

    def set_start_state(self, state):
        self.start_state = state

    def add_end_state(self, state):
        state.is_end = True
        self.end_states.append(state)

    def add_transition(self, from_state, symbol, to_state):
        if symbol != 'ε':
            self.alphabet.add(symbol)
        if symbol in from_state.transitions:
            from_state.transitions[symbol].append(to_state)
        else:
            from_state.transitions[symbol] = [to_state]
        if symbol == 'ε':
            from_state.epsilon_transitions.append(to_state)

def regex_to_nfa(regex):
    """将正则表达式转换为NFA"""
    operators = {'|', '*', '(', ')'}
    alphabet = set(c for c in regex if c not in operators)
    alphabet.add('ε')  # 添加ε到字母表

    def parse_regex(regex):
        """为连接操作添加显式的.操作符"""
        result = []
        for i in range(len(regex)):
            result.append(regex[i])
            if i + 1 < len(regex) and regex[i] not in '(|' and regex[i + 1] not in ')|*':
                result.append('.')
        return ''.join(result)

    def create_basic_nfa(symbol):
        """创建基本NFA（单个符号）"""
        nfa = NFA()
        start = nfa.add_state(State(0))
        end = nfa.add_state(State(1))
        nfa.set_start_state(start)
        nfa.add_end_state(end)
        nfa.add_transition(start, symbol, end)
        return nfa

    def concat_nfa(nfa1, nfa2):
        """连接两个NFA"""
        nfa = NFA()
        
        # 复制nfa1的状态
        state_map = {}
        for state in nfa1.states:
            new_state = nfa.add_state(State(len(nfa.states)))
            state_map[state.id] = new_state
            if state is nfa1.start_state:
                nfa.set_start_state(new_state)
        
        # 从nfa1终态到nfa2起始态添加ε转移
        for end_state in nfa1.end_states:
            mapped_end_state = state_map[end_state.id]
            
            # 复制nfa2的状态
            nfa2_state_map = {}
            for state in nfa2.states:
                new_state = nfa.add_state(State(len(nfa.states)))
                nfa2_state_map[state.id] = new_state
                if state is nfa2.start_state:
                    nfa.add_transition(mapped_end_state, 'ε', new_state)
                if state in nfa2.end_states:
                    nfa.add_end_state(new_state)
            
            # 复制nfa2的转移
            for state in nfa2.states:
                mapped_state = nfa2_state_map[state.id]
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        mapped_target = nfa2_state_map[target.id]
                        nfa.add_transition(mapped_state, symbol, mapped_target)
        
        # 复制nfa1的转移
        for state in nfa1.states:
            mapped_state = state_map[state.id]
            for symbol, targets in state.transitions.items():
                for target in targets:
                    mapped_target = state_map[target.id]
                    nfa.add_transition(mapped_state, symbol, mapped_target)
        
        return nfa

    def union_nfa(nfa1, nfa2):
        """合并两个NFA"""
        nfa = NFA()
        start = nfa.add_state(State(0))
        nfa.set_start_state(start)
        end = nfa.add_state(State(1))
        nfa.add_end_state(end)
        
        # 复制nfa1的状态
        nfa1_state_map = {}
        for state in nfa1.states:
            new_state = nfa.add_state(State(len(nfa.states)))
            nfa1_state_map[state.id] = new_state
            if state is nfa1.start_state:
                nfa.add_transition(start, 'ε', new_state)
            if state in nfa1.end_states:
                nfa.add_transition(new_state, 'ε', end)
        
        # 复制nfa2的状态
        nfa2_state_map = {}
        for state in nfa2.states:
            new_state = nfa.add_state(State(len(nfa.states)))
            nfa2_state_map[state.id] = new_state
            if state is nfa2.start_state:
                nfa.add_transition(start, 'ε', new_state)
            if state in nfa2.end_states:
                nfa.add_transition(new_state, 'ε', end)
        
        # 复制nfa1的转移
        for state in nfa1.states:
            mapped_state = nfa1_state_map[state.id]
            for symbol, targets in state.transitions.items():
                for target in targets:
                    mapped_target = nfa1_state_map[target.id]
                    nfa.add_transition(mapped_state, symbol, mapped_target)
        
        # 复制nfa2的转移
        for state in nfa2.states:
            mapped_state = nfa2_state_map[state.id]
            for symbol, targets in state.transitions.items():
                for target in targets:
                    mapped_target = nfa2_state_map[target.id]
                    nfa.add_transition(mapped_state, symbol, mapped_target)
        
        return nfa

    def kleene_star_nfa(nfa1):
        """创建Kleene星NFA"""
        nfa = NFA()
        start = nfa.add_state(State(0))
        end = nfa.add_state(State(1))
        nfa.set_start_state(start)
        nfa.add_end_state(end)
        nfa.add_transition(start, 'ε', end)  # 允许跳过整个NFA
        
        # 复制nfa1的状态
        nfa1_state_map = {}
        for state in nfa1.states:
            new_state = nfa.add_state(State(len(nfa.states)))
            nfa1_state_map[state.id] = new_state
            if state is nfa1.start_state:
                nfa.add_transition(start, 'ε', new_state)
        
        # 复制nfa1的转移
        for state in nfa1.states:
            mapped_state = nfa1_state_map[state.id]
            for symbol, targets in state.transitions.items():
                for target in targets:
                    mapped_target = nfa1_state_map[target.id]
                    nfa.add_transition(mapped_state, symbol, mapped_target)
        
        # 从nfa1的结束状态到开始状态添加ε转移（循环）
        for end_state in nfa1.end_states:
            mapped_end_state = nfa1_state_map[end_state.id]
            for state in nfa1.states:
                if state is nfa1.start_state:
                    mapped_start_state = nfa1_state_map[state.id]
                    nfa.add_transition(mapped_end_state, 'ε', mapped_start_state)
            # 从nfa1的结束状态到新的结束状态添加ε转移
            nfa.add_transition(mapped_end_state, 'ε', end)
        
        return nfa

    def shunting_yard(regex):
        """Shunting Yard算法将中缀表达式转换为后缀表达式"""
        output_queue = []
        operator_stack = []
        precedence = {'|': 1, '.': 2, '*': 3}
        
        for c in regex:
            if c not in operators:
                output_queue.append(c)
            elif c == '(':
                operator_stack.append(c)
            elif c == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output_queue.append(operator_stack.pop())
                operator_stack.pop()  # 弹出'('
            else:
                while (operator_stack and operator_stack[-1] != '(' and
                       precedence.get(operator_stack[-1], 0) >= precedence.get(c, 0)):
                    output_queue.append(operator_stack.pop())
                operator_stack.append(c)
        
        while operator_stack:
            output_queue.append(operator_stack.pop())
        
        return output_queue

    def evaluate_postfix(postfix):
        """评估后缀表达式并构建NFA"""
        stack = []
        for c in postfix:
            if c not in operators:
                stack.append(create_basic_nfa(c))
            elif c == '*':
                nfa1 = stack.pop()
                stack.append(kleene_star_nfa(nfa1))
            elif c == '.':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(concat_nfa(nfa1, nfa2))
            elif c == '|':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(union_nfa(nfa1, nfa2))
        
        return stack.pop()

    # 处理正则表达式
    regex = parse_regex(regex)
    postfix = shunting_yard(regex)
    nfa = evaluate_postfix(postfix)
    return nfa

def get_nfa_transition_table(nfa):
    """生成NFA状态转移表"""
    # 收集所有状态ID并按数字顺序排序
    state_ids = sorted([state.id for state in nfa.states])
    
    # 收集所有符号并按字母顺序排序
    symbols = sorted(nfa.alphabet)
    
    # 初始化转移表
    transition_table = []
    
    # 添加表头
    header = ["状态"] + symbols
    transition_table.append(header)
    
    # 为每个状态添加一行
    for state_id in state_ids:
        state = next(s for s in nfa.states if s.id == state_id)
        row = [f"q{state_id}"]
        
        for symbol in symbols:
            # 获取通过该符号可达的状态
            targets = []
            if symbol in state.transitions:
                targets.extend([f"q{t.id}" for t in state.transitions[symbol]])
            
            # 如果是ε转移，也包含在ε列中
            if symbol == 'ε':
                targets.extend([f"q{t.id}" for t in state.epsilon_transitions])
            
            # 格式化输出
            if targets:
                row.append(", ".join(sorted(targets)))
            else:
                row.append("-")
        
        transition_table.append(row)
    
    return transition_table

def visualize_nfa(nfa):
    """可视化NFA"""
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='LR', size='8,5')
    
    # 添加隐藏的起始节点
    dot.node('start', style='invisible')
    
    # 添加状态
    for state in nfa.states:
        if state in nfa.end_states:
            # 接受状态用双圈表示
            dot.node(str(state.id), shape='doublecircle', style='filled', fillcolor='lightgreen')
        else:
            # 普通状态用单圈表示
            dot.node(str(state.id), shape='circle', style='filled', fillcolor='lightblue')
    
    # 添加起始箭头
    if nfa.start_state:
        dot.edge('start', str(nfa.start_state.id), label='')
    
    # 添加转移
    for state in nfa.states:
        for symbol, targets in state.transitions.items():
            for target in targets:
                dot.edge(str(state.id), str(target.id), label=symbol)
    
    # 添加ε转移
    for state in nfa.states:
        for target in state.epsilon_transitions:
            dot.edge(str(state.id), str(target.id), label='ε')
    
    # 渲染为PNG并转换为PIL Image
    png_data = dot.pipe()
    buf = io.BytesIO(png_data)
    img = Image.open(buf)
    return img

def process_regex_ui(regex):
    """处理正则表达式并返回结果"""
    try:
        nfa = regex_to_nfa(regex)
        
        # 生成NFA状态转移表
        transition_table = get_nfa_transition_table(nfa)
        
        # 生成可视化
        nfa_image = visualize_nfa(nfa)
        
        # 格式化状态转移表为字符串
        table_str = "NFA状态转移表:\n"
        max_col_widths = [max(len(str(row[i])) for row in transition_table) for i in range(len(transition_table[0]))]
        
        # 添加表头分隔线
        separator = "+" + "+".join(["-" * (w + 2) for w in max_col_widths]) + "+"
        table_str += separator + "\n"
        
        # 添加表头
        header = "| " + " | ".join([str(transition_table[0][i]).ljust(max_col_widths[i]) 
                                   for i in range(len(transition_table[0]))]) + " |"
        table_str += header + "\n"
        table_str += separator + "\n"
        
        # 添加数据行
        for row in transition_table[1:]:
            row_str = "| " + " | ".join([str(row[i]).ljust(max_col_widths[i]) 
                                        for i in range(len(row))]) + " |"
            table_str += row_str + "\n"
        
        table_str += separator
        
        return nfa_image, table_str
    except Exception as e:
        return None, f"错误: {str(e)}"

# 创建Gradio界面
with gr.Blocks(title="正则表达式到NFA转换工具") as iface:
    gr.Markdown("# 正则表达式到NFA转换工具")
    gr.Markdown("将正则表达式转换为NFA并可视化，同时显示状态转移表。")
    
    with gr.Row():
        regex_input = gr.Textbox(label="正则表达式", placeholder="输入正则表达式，如: a(b|c)*")
    
    process_btn = gr.Button("转换")
    
    with gr.Row():
        nfa_graph = gr.Image(label="NFA可视化")
        nfa_table = gr.Textbox(label="NFA状态转移表", lines=15)
    
    gr.Markdown("""
    ## 使用说明
    1. 在输入框中输入正则表达式
    2. 点击"转换"按钮
    3. 查看右侧的NFA状态转移表和可视化图形
    
    ## 支持的运算符
    - `|` - 选择 (a|b 匹配 a 或 b)
    - `*` - 克莱尼星号 (a* 匹配零个或多个 a)
    - `()` - 分组 ((ab)* 匹配零个或多个 ab)
    - 连接操作自动处理 (ab 匹配 a 后跟 b)
    
    ## 示例
    - `a(b|c)*` - 匹配 a 后跟零个或多个 b 或 c
    - `(ab)*c` - 匹配零个或多个 ab 后跟 c
    - `a|b*` - 匹配 a 或零个或多个 b
    """)

    process_btn.click(
        process_regex_ui,
        inputs=[regex_input],
        outputs=[nfa_graph, nfa_table]
    )

# 启动应用
if __name__ == "__main__":
    iface.launch()
