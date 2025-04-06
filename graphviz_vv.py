import re
import graphviz
import io
from PIL import Image
import gradio as gr
from collections import defaultdict

class State:
    def __init__(self, id):
        self.id = id
        self.transitions = {}
        self.is_end = False
        self.epsilon_transitions = []  # 记录通过ε可到达的状态


class NFA:
    def __init__(self):
        self.states = []
        self.start_state = None
        self.end_states = []
        self.alphabet = set()

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


class DFA:
    def __init__(self):
        self.states = []
        self.start_state = None
        self.end_states = []
        self.alphabet = set()
        self.transitions = {}
        self.state_map = {}  # 用于映射DFA状态集合到状态ID

    def add_state(self, state_set):
        # 将NFA状态集合映射到DFA状态
        state_id = len(self.states)
        state = State(state_id)
        self.states.append(state)
        self.state_map[frozenset(state.id for state in state_set)] = state
        # 如果NFA状态集合中包含接受状态，则DFA状态也是接受状态
        if any(s.is_end for s in state_set):
            self.add_end_state(state)
        return state

    def set_start_state(self, state):
        self.start_state = state

    def add_end_state(self, state):
        state.is_end = True
        self.end_states.append(state)

    def add_transition(self, from_state, symbol, to_state):
        self.alphabet.add(symbol)
        self.transitions[(from_state.id, symbol)] = to_state.id


def epsilon_closure(nfa, states):
    # 计算状态集合的ε闭包
    closure = set(states)
    stack = list(states)
    while stack:
        state = stack.pop()
        for next_state in state.epsilon_transitions:
            if next_state not in closure:
                closure.add(next_state)
                stack.append(next_state)
    return closure


def move(nfa, states, symbol):
    # 计算状态集合通过某个符号的转移
    result = set()
    for state in states:
        if symbol in state.transitions:
            result.update(state.transitions[symbol])
    return result


def regex_to_nfa(regex):
    # 将正则表达式转换为NFA
    operators = {'|', '*', '(', ')', '.'}
    alphabet = set(c for c in regex if c not in operators)
    alphabet.add('ε')  # 添加ε到字母表

    def parse_regex(regex):
        # 为连接操作添加显式的.操作符
        result = []
        for i in range(len(regex)):
            result.append(regex[i])
            if i + 1 < len(regex) and regex[i] not in '(|' and regex[i + 1] not in ')|*':
                result.append('.')
        return ''.join(result)

    def create_basic_nfa(symbol):
        # 创建基本NFA（单个符号）
        nfa = NFA()
        start = nfa.add_state(State(0))
        end = nfa.add_state(State(1))
        nfa.set_start_state(start)
        nfa.add_end_state(end)
        nfa.add_transition(start, symbol, end)
        return nfa

    def concat_nfa(nfa1, nfa2):
        # 连接两个NFA
        nfa = NFA()
        state_map = {}
        
        # 复制nfa1的状态
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
        # 合并两个NFA
        nfa = NFA()
        start = nfa.add_state(State(0))
        nfa.set_start_state(start)
        end= nfa.add_state(State(1))
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
                #nfa.add_end_state(new_state)
        
        # 复制nfa2的状态
        nfa2_state_map = {}
        for state in nfa2.states:
            new_state = nfa.add_state(State(len(nfa.states)))
            nfa2_state_map[state.id] = new_state
            if state is nfa2.start_state:
                nfa.add_transition(start, 'ε', new_state)
            if state in nfa2.end_states:
                nfa.add_transition(new_state, 'ε', end)
                #nfa.add_end_state(new_state)
        
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
        # 创建Kleene星NFA
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

    # 使用Shunting Yard算法解析正则表达式
    def shunting_yard(regex):
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


def nfa_to_dfa(nfa):
    # 将NFA转换为DFA
    dfa = DFA()
    dfa.alphabet = nfa.alphabet.copy()
    
    # 计算起始状态的ε闭包
    start_states = epsilon_closure(nfa, {nfa.start_state})
    dfa_start = dfa.add_state(start_states)
    dfa.set_start_state(dfa_start)
    
    # 使用广度优先搜索构建DFA
    unmarked_states = [start_states]
    state_sets = {frozenset(s.id for s in start_states): dfa_start}
    
    while unmarked_states:
        current_states = unmarked_states.pop(0)
        current_dfa_state = state_sets[frozenset(s.id for s in current_states)]
        
        for symbol in dfa.alphabet:
            if symbol == 'ε':
                continue
            
            # 计算通过当前符号可达的状态集合
            next_states = epsilon_closure(nfa, move(nfa, current_states, symbol))
            if not next_states:
                continue
            
            next_states_key = frozenset(s.id for s in next_states)
            
            # 如果这个状态集合是新的，创建一个新的DFA状态
            if next_states_key not in state_sets:
                next_dfa_state = dfa.add_state(next_states)
                state_sets[next_states_key] = next_dfa_state
                unmarked_states.append(next_states)
            else:
                next_dfa_state = state_sets[next_states_key]
            
            # 添加转移
            dfa.add_transition(current_dfa_state, symbol, next_dfa_state)
    
    return dfa


def minimize_dfa(dfa):
    # 最小化DFA
    # 1. 区分接受状态和非接受状态
    accepting = set(state.id for state in dfa.end_states)
    non_accepting = set(state.id for state in dfa.states if state.id not in accepting)
    
    # 初始化分区
    partitions = []
    if accepting:
        partitions.append(accepting)
    if non_accepting:
        partitions.append(non_accepting)
    
    # 2. 细化分区直到不能再细化
    while True:
        new_partitions = []
        for partition in partitions:
            # 对于每个分区，检查其中的状态是否有不同的行为
            subgroups = defaultdict(set)
            for state_id in partition:
                # 计算状态的特征（对于每个输入符号，转移到哪个分区）
                characteristics = []
                for symbol in sorted(dfa.alphabet):
                    if symbol == 'ε':
                        continue
                    
                    transition_key = (state_id, symbol)
                    if transition_key in dfa.transitions:
                        target_state = dfa.transitions[transition_key]
                        # 找出目标状态所在的分区
                        target_partition = next((i for i, p in enumerate(partitions) if target_state in p), None)
                        characteristics.append((symbol, target_partition))
                    else:
                        characteristics.append((symbol, None))
                
                # 使用特征来分组状态
                subgroups[tuple(characteristics)].add(state_id)
            
            # 如果分区被细化，添加新的子分区
            if len(subgroups) > 1:
                new_partitions.extend(subgroups.values())
            else:
                new_partitions.append(partition)
        
        # 如果分区没有变化，结束迭代
        if len(new_partitions) == len(partitions) and all(
            any(new_p == old_p for new_p in new_partitions)
            for old_p in partitions
        ):
            break
        
        partitions = new_partitions
    
    # 3. 构建最小化DFA
    min_dfa = DFA()
    min_dfa.alphabet = dfa.alphabet.copy()
    
    # 创建新的状态
    partition_to_state = {}
    for i, partition in enumerate(partitions):
        state = State(i)
        min_dfa.states.append(state)
        partition_to_state[frozenset(partition)] = state
        
        # 检查是否包含起始状态
        if any(dfa.start_state.id == state_id for state_id in partition):
            min_dfa.set_start_state(state)
        
        # 检查是否包含接受状态
        if any(state_id in accepting for state_id in partition):
            min_dfa.add_end_state(state)
    
    # 添加转移
    for partition, state in partition_to_state.items():
        # 选择分区中的一个代表状态
        representative = next(iter(partition))
        
        for symbol in min_dfa.alphabet:
            if symbol == 'ε':
                continue
            
            transition_key = (representative, symbol)
            if transition_key in dfa.transitions:
                target = dfa.transitions[transition_key]
                # 找出目标状态所在的分区
                target_partition = next(
                    p for p in partitions if target in p
                )
                target_state = partition_to_state[frozenset(target_partition)]
                min_dfa.add_transition(state, symbol, target_state)
    
    return min_dfa

def match_regex(regex, input_string):
    # 构建并最小化DFA
    nfa = regex_to_nfa(regex)
    dfa = nfa_to_dfa(nfa)
    min_dfa = minimize_dfa(dfa)
    
    # 使用最小化DFA来匹配输入字符串
    current_state = min_dfa.start_state
    for c in input_string:
        transition_key = (current_state.id, c)
        if transition_key not in min_dfa.transitions:
            return False
        current_state_id = min_dfa.transitions[transition_key]
        current_state = next(state for state in min_dfa.states if state.id == current_state_id)
    
    # 如果最终状态是接受状态，则匹配成功
    return current_state in min_dfa.end_states

# 使用Graphviz的可视化函数
def visualize_nfa(nfa):
    # Create a Graphviz digraph
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='LR', size='8,5')
    
    # Add a hidden start node
    dot.node('start', style='invisible')
    
    # Add states
    for state in nfa.states:
        if state in nfa.end_states:
            # Double circle for accept states
            dot.node(str(state.id), shape='doublecircle', style='filled', fillcolor='lightgreen')
        else:
            # Single circle for normal states
            dot.node(str(state.id), shape='circle', style='filled', fillcolor='lightblue')
    
    # Add start arrow
    if nfa.start_state:
        dot.edge('start', str(nfa.start_state.id), label='')
    
    # Add transitions
    for state in nfa.states:
        for symbol, targets in state.transitions.items():
            for target in targets:
                dot.edge(str(state.id), str(target.id), label=symbol)
    
    # Render to PNG and convert to PIL Image
    png_data = dot.pipe()
    buf = io.BytesIO(png_data)
    img = Image.open(buf)
    return img

def visualize_dfa(dfa, title="DFA"):
    # Create a Graphviz digraph
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='LR', size='8,5')
    
    # Add a hidden start node
    dot.node('start', style='invisible')
    
    # Add states
    for state in dfa.states:
        if state in dfa.end_states:
            # Double circle for accept states
            dot.node(str(state.id), shape='doublecircle', style='filled', fillcolor='lightgreen')
        else:
            # Single circle for normal states
            dot.node(str(state.id), shape='circle', style='filled', fillcolor='lightblue')
    
    # Add start arrow
    if dfa.start_state:
        dot.edge('start', str(dfa.start_state.id), label='')
    
    # Create a dictionary to collect multiple transitions between the same states
    transitions = {}
    for (from_state, symbol), to_state in dfa.transitions.items():
        key = (from_state, to_state)
        if key in transitions:
            transitions[key].append(symbol)
        else:
            transitions[key] = [symbol]
    
    # Add transitions
    for (from_state, to_state), symbols in transitions.items():
        # Sort and join symbols for better readability
        label = ','.join(sorted(symbols))
        dot.edge(str(from_state), str(to_state), label=label)
    
    # Render to PNG and convert to PIL Image
    png_data = dot.pipe()
    buf = io.BytesIO(png_data)
    img = Image.open(buf)
    return img

# 处理正则表达式的函数
def process_regex(regex, test_string):
    try:
        # 处理正则表达式
        nfa = regex_to_nfa(regex)
        dfa = nfa_to_dfa(nfa)
        min_dfa = minimize_dfa(dfa)
        
        # 生成可视化
        nfa_viz = visualize_nfa(nfa)
        dfa_viz = visualize_dfa(dfa)
        min_dfa_viz = visualize_dfa(min_dfa, "最小化 DFA")
        
        # 检查测试字符串是否匹配
        match_result = match_regex(regex, test_string)
        match_text = f"字符串 '{test_string}' {'匹配' if match_result else '不匹配'} 正则表达式 '{regex}'"
        
        return (
            nfa_viz, 
            dfa_viz, 
            min_dfa_viz,
            match_text
        )
    except Exception as e:
        return None, None, None, f"错误: {str(e)}"

# 定义Gradio界面
with gr.Blocks(title="正则表达式可视化工具") as iface:
    gr.Markdown("# 正则表达式可视化工具")
    gr.Markdown("可视化正则表达式的NFA、DFA和最小化DFA，并测试字符串是否匹配。")
    
    with gr.Row():
        regex_input = gr.Textbox(label="正则表达式", placeholder="输入正则表达式...")
        test_string = gr.Textbox(label="测试字符串", placeholder="输入要测试的字符串...")
    
    process_btn = gr.Button("处理")
    
    match_result = gr.Textbox(label="匹配结果")
    
    with gr.Tab("NFA 自动机"):
        nfa_graph = gr.Image(label="NFA 图")
    
    with gr.Tab("DFA 自动机"):
        dfa_graph = gr.Image(label="DFA 图")
    
    with gr.Tab("最小化 DFA 自动机"):
        min_dfa_graph = gr.Image(label="最小化 DFA 图")
    
    process_btn.click(
        process_regex, 
        inputs=[regex_input, test_string], 
        outputs=[nfa_graph, dfa_graph, min_dfa_graph, match_result]
    )
    
    gr.Markdown("""
    ## 使用指南
    1. 在第一个输入框中输入正则表达式。
    2. 在第二个输入框中输入要测试的字符串。
    3. 点击"处理"按钮以可视化NFA、DFA和最小化DFA。
    4. 查看下方的匹配结果。
    
    ## 支持的运算符
    - `|` (选择): a|b 匹配 a 或 b
    - `*` (克莱尼星号): a* 匹配零个或多个 a
    - `()` (分组): (ab)* 匹配零个或多个 ab
    """)

# 启动应用
if __name__ == "__main__":
    iface.launch()