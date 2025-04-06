import graphviz
import io
from PIL import Image
import gradio as gr

class State:
    """表示自动机中的一个状态"""
    def __init__(self, id):
        self.id = id
        self.transitions = {}  # 存储状态转移: symbol -> [target_states]
        self.is_end = False    # 是否为接受状态
        self.epsilon_moves = []  # 存储ε转移可达的状态

class NFA:
    """非确定有限自动机"""
    def __init__(self):
        self.states = []       # 所有状态列表
        self.start_state = None  # 开始状态
        self.end_states = []   # 接受状态列表
        self.alphabet = set()  # 字母表(输入符号集)

    def create_state(self):
        """创建并添加新状态"""
        state = State(len(self.states))
        self.states.append(state)
        return state

    def set_start(self, state):
        """设置开始状态"""
        self.start_state = state

    def add_end(self, state):
        """添加接受状态"""
        state.is_end = True
        self.end_states.append(state)

    def add_transition(self, from_state, symbol, to_state):
        """添加状态转移"""
        if symbol != 'ε':
            self.alphabet.add(symbol)
            
        if symbol in from_state.transitions:
            from_state.transitions[symbol].append(to_state)
        else:
            from_state.transitions[symbol] = [to_state]
            
        if symbol == 'ε':
            from_state.epsilon_moves.append(to_state)
    
    def get_transition_table(self):
        """获取状态转移表"""
        table = []
        # 表头行
        header = ["状态ID", "是否接受状态"]
        symbols = sorted(list(self.alphabet))
        header.extend(symbols)
        header.append('ε')
        table.append(header)
        
        # 添加每个状态的转移信息
        for state in self.states:
            row = [f"q{state.id}", "是" if state.is_end else "否"]
            
            # 添加每个符号的转移
            for symbol in symbols:
                if symbol in state.transitions:
                    targets = state.transitions[symbol]
                    targets_str = ",".join([f"q{t.id}" for t in targets])
                    row.append(targets_str)
                else:
                    row.append("-")
            
            # 添加ε转移
            if 'ε' in state.transitions:
                targets = state.transitions['ε']
                targets_str = ",".join([f"q{t.id}" for t in targets])
                row.append(targets_str)
            else:
                row.append("-")
                
            table.append(row)
            
        return table

def regex_to_nfa(regex):
    """将正则表达式转换为NFA"""
    # 定义操作符优先级
    precedence = {'|': 1, '.': 2, '*': 3}
    operators = {'|', '.', '*', '(', ')'}
    
    def add_concat_operator(regex):
        """在需要的位置添加连接操作符('.')"""
        output = []
        for i in range(len(regex)):
            output.append(regex[i])
            if i+1 < len(regex) and regex[i] not in '(|' and regex[i+1] not in ')|*':
                output.append('.')
        return ''.join(output)
    
    def to_postfix(regex):
        """使用调度场算法(Shunting Yard)将中缀表达式转换为后缀表达式"""
        output = []
        operator_stack = []
        
        for token in regex:
            if token not in operators:  # 普通字符
                output.append(token)
            elif token == '(':  # 左括号
                operator_stack.append(token)
            elif token == ')':  # 右括号
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                operator_stack.pop()  # 弹出左括号
            else:  # 其他操作符
                while (operator_stack and operator_stack[-1] != '(' and 
                       precedence.get(operator_stack[-1], 0) >= precedence.get(token, 0)):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
        
        # 将剩余操作符添加到输出
        while operator_stack:
            output.append(operator_stack.pop())
            
        return output
    
    def basic_nfa(symbol):
        """为单个符号创建基本NFA"""
        nfa = NFA()
        start = nfa.create_state()
        end = nfa.create_state()
        
        nfa.set_start(start)
        nfa.add_end(end)
        nfa.add_transition(start, symbol, end)
        
        return nfa
    
    def concat_nfa(nfa1, nfa2):
        """连接两个NFA"""
        result = NFA()
        
        # 创建新的起始状态
        start = result.create_state()
        result.set_start(start)
        
        # 添加ε转移到nfa1的起始状态
        nfa1_start_copy = result.create_state()
        result.add_transition(start, 'ε', nfa1_start_copy)
        
        # 复制nfa1的所有状态和转移
        state_map_nfa1 = {nfa1.start_state.id: nfa1_start_copy}
        for state in nfa1.states:
            if state.id not in state_map_nfa1:
                new_state = result.create_state()
                state_map_nfa1[state.id] = new_state
                
            for symbol, targets in state.transitions.items():
                for target in targets:
                    if target.id not in state_map_nfa1:
                        new_target = result.create_state()
                        state_map_nfa1[target.id] = new_target
                    result.add_transition(state_map_nfa1[state.id], symbol, state_map_nfa1[target.id])
        
        # 复制nfa2的所有状态和转移
        nfa2_start_copy = result.create_state()
        state_map_nfa2 = {nfa2.start_state.id: nfa2_start_copy}
        
        # 从nfa1的所有结束状态添加ε转移到nfa2的起始状态
        for end_state in nfa1.end_states:
            result.add_transition(state_map_nfa1[end_state.id], 'ε', nfa2_start_copy)
            
        for state in nfa2.states:
            if state.id not in state_map_nfa2:
                new_state = result.create_state()
                state_map_nfa2[state.id] = new_state
                
            for symbol, targets in state.transitions.items():
                for target in targets:
                    if target.id not in state_map_nfa2:
                        new_target = result.create_state()
                        state_map_nfa2[target.id] = new_target
                    result.add_transition(state_map_nfa2[state.id], symbol, state_map_nfa2[target.id])
        
        # 将nfa2的结束状态添加为result的结束状态
        for end_state in nfa2.end_states:
            result.add_end(state_map_nfa2[end_state.id])
            
        return result
    
    def union_nfa(nfa1, nfa2):
        """合并两个NFA (对应 | 操作)"""
        result = NFA()
        
        # 创建新的起始和结束状态
        start = result.create_state()
        end = result.create_state()
        result.set_start(start)
        result.add_end(end)
        
        # 复制nfa1
        nfa1_start_copy = result.create_state()
        result.add_transition(start, 'ε', nfa1_start_copy)
        
        state_map_nfa1 = {nfa1.start_state.id: nfa1_start_copy}
        for state in nfa1.states:
            if state.id not in state_map_nfa1:
                new_state = result.create_state()
                state_map_nfa1[state.id] = new_state
                
            for symbol, targets in state.transitions.items():
                for target in targets:
                    if target.id not in state_map_nfa1:
                        new_target = result.create_state()
                        state_map_nfa1[target.id] = new_target
                    result.add_transition(state_map_nfa1[state.id], symbol, state_map_nfa1[target.id])
        
        # 复制nfa2
        nfa2_start_copy = result.create_state()
        result.add_transition(start, 'ε', nfa2_start_copy)
        
        state_map_nfa2 = {nfa2.start_state.id: nfa2_start_copy}
        for state in nfa2.states:
            if state.id not in state_map_nfa2:
                new_state = result.create_state()
                state_map_nfa2[state.id] = new_state
                
            for symbol, targets in state.transitions.items():
                for target in targets:
                    if target.id not in state_map_nfa2:
                        new_target = result.create_state()
                        state_map_nfa2[target.id] = new_target
                    result.add_transition(state_map_nfa2[state.id], symbol, state_map_nfa2[target.id])
        
        # 从nfa1和nfa2的结束状态添加ε转移到新的结束状态
        for end_state in nfa1.end_states:
            result.add_transition(state_map_nfa1[end_state.id], 'ε', end)
        for end_state in nfa2.end_states:
            result.add_transition(state_map_nfa2[end_state.id], 'ε', end)
            
        return result
    
    def kleene_star_nfa(nfa):
        """克莱尼星操作 (对应 * 操作)"""
        result = NFA()
        
        # 创建新的起始和结束状态
        start = result.create_state()
        end = result.create_state()
        result.set_start(start)
        result.add_end(end)
        
        # 添加ε转移以跳过nfa (允许空字符串)
        result.add_transition(start, 'ε', end)
        
        # 复制原始nfa
        nfa_start_copy = result.create_state()
        result.add_transition(start, 'ε', nfa_start_copy)
        
        state_map = {nfa.start_state.id: nfa_start_copy}
        for state in nfa.states:
            if state.id not in state_map:
                new_state = result.create_state()
                state_map[state.id] = new_state
                
            for symbol, targets in state.transitions.items():
                for target in targets:
                    if target.id not in state_map:
                        new_target = result.create_state()
                        state_map[target.id] = new_target
                    result.add_transition(state_map[state.id], symbol, state_map[target.id])
        
        # 从nfa的结束状态添加ε转移到新的结束状态
        for end_state in nfa.end_states:
            result.add_transition(state_map[end_state.id], 'ε', end)
            # 添加回环 - 从结束状态到起始状态的ε转移
            result.add_transition(state_map[end_state.id], 'ε', nfa_start_copy)
            
        return result
    
    def build_nfa(postfix):
        """根据后缀表达式构建NFA"""
        stack = []
        
        for token in postfix:
            if token == '*':
                if not stack:
                    raise ValueError("无效的表达式: * 操作符没有操作数")
                nfa = stack.pop()
                stack.append(kleene_star_nfa(nfa))
            elif token == '.':
                if len(stack) < 2:
                    raise ValueError("无效的表达式: . 操作符需要两个操作数")
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(concat_nfa(nfa1, nfa2))
            elif token == '|':
                if len(stack) < 2:
                    raise ValueError("无效的表达式: | 操作符需要两个操作数")
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(union_nfa(nfa1, nfa2))
            else:
                stack.append(basic_nfa(token))
        
        if len(stack) != 1:
            raise ValueError("无效的表达式")
            
        return stack[0]
    
    # 处理正则表达式并构建NFA
    regex_with_concat = add_concat_operator(regex)
    postfix = to_postfix(regex_with_concat)
    return build_nfa(postfix)

def visualize_nfa(nfa):
    """使用Graphviz可视化NFA"""
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='LR', size='8,5')
    
    # 添加一个隐藏的起始节点
    dot.node('start', style='invisible')
    
    # 添加所有状态
    for state in nfa.states:
        if state in nfa.end_states:
            # 接受状态用双圆圈
            dot.node(f'q{state.id}', shape='doublecircle', style='filled', fillcolor='lightgreen')
        else:
            # 普通状态用单圆圈
            dot.node(f'q{state.id}', shape='circle', style='filled', fillcolor='lightblue')
    
    # 添加起始箭头
    if nfa.start_state:
        dot.edge('start', f'q{nfa.start_state.id}', label='')
    
    # 添加所有转移
    for state in nfa.states:
        for symbol, targets in state.transitions.items():
            for target in targets:
                dot.edge(f'q{state.id}', f'q{target.id}', label=symbol)
    
    # 渲染为PNG并转换为PIL图像
    png_data = dot.pipe()
    buf = io.BytesIO(png_data)
    img = Image.open(buf)
    return img

def render_transition_table(table):
    """将状态转移表格式化为HTML"""
    html = "<table border='1' cellpadding='5'>"
    
    # 添加表头
    html += "<tr>"
    for header in table[0]:
        html += f"<th>{header}</th>"
    html += "</tr>"
    
    # 添加数据行
    for row in table[1:]:
        html += "<tr>"
        for i, cell in enumerate(row):
            cell_style = ""
            # 如果是接受状态，添加绿色背景
            if i == 1 and cell == "是":
                cell_style = " style='background-color: lightgreen;'"
            html += f"<td{cell_style}>{cell}</td>"
        html += "</tr>"
    
    html += "</table>"
    return html

def process_regex(regex):
    """处理正则表达式并返回结果"""
    try:
        # 将正则表达式转换为NFA
        nfa = regex_to_nfa(regex)
        
        # 获取状态转移表
        transition_table = nfa.get_transition_table()
        table_html = render_transition_table(transition_table)
        
        # 可视化NFA
        nfa_image = visualize_nfa(nfa)
        
        return nfa_image, table_html
    except Exception as e:
        return None, f"<p style='color: red'>错误: {str(e)}</p>"

# 定义Gradio界面
with gr.Blocks(title="正则表达式到NFA转换工具") as iface:
    gr.Markdown("# 正则表达式到NFA转换工具")
    gr.Markdown("输入正则表达式，查看对应的NFA及其状态转移表。")
    
    regex_input = gr.Textbox(label="正则表达式", placeholder="输入正则表达式，例如: a(b|c)*")
    process_btn = gr.Button("转换为NFA")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### NFA 可视化")
            nfa_graph = gr.Image(label="NFA 图")
        
        with gr.Column():
            gr.Markdown("### NFA 状态转移表")
            transition_table = gr.HTML()
    
    process_btn.click(
        process_regex, 
        inputs=[regex_input], 
        outputs=[nfa_graph, transition_table]
    )
    
    gr.Markdown("""
    ## 使用指南
    1. 在输入框中输入正则表达式
    2. 点击"转换为NFA"按钮
    3. 查看生成的NFA图和状态转移表
    
    ## 支持的运算符
    - `|` (或): a|b 匹配 a 或 b
    - `*` (克莱尼星号): a* 匹配零个或多个 a
    - `()` (分组): (ab)* 匹配零个或多个 ab
    
    ## 示例
    - `a` - 匹配字符 'a'
    - `ab` - 匹配字符串 "ab"
    - `a|b` - 匹配字符 'a' 或 'b'
    - `a*` - 匹配零个或多个 'a'
    - `(a|b)*` - 匹配由 'a' 和 'b' 组成的任意字符串
    - `a(b|c)*` - 匹配 'a' 后跟零个或多个 'b' 或 'c'
    """)

# 启动应用
if __name__ == "__main__":
    iface.launch()
