import random
import time
from collections import defaultdict
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext

class PetriNetSimulator:
    def __init__(self):
        self.places = {}  # 存储位置及其标记数
        self.transitions = {}  # 存储转换及其输入输出规则
        self.history = []  # 存储状态历史
        self.conditions_met = True  # 跟踪条件是否满足
        self.last_received_host = None  # 记录最后接收数据包的主机
        self.last_received_time = 0  # 记录最后接收数据包的时间
        self.packet_sent_since_last_receive = False  # 记录自上次接收后是否有数据包发送
        
    def load_initial_state(self, state_str):
        """加载初始状态"""
        self.places.clear()
        parts = state_str.split(',')
        for part in parts:
            place, tokens = part.split(':')
            self.places[place.strip()] = int(tokens.strip())
        self.history.append(self.get_current_state())
    
    def add_transition(self, name, inputs, outputs):
        """添加转换规则"""
        input_dict = {}
        output_dict = {}
        
        # 处理输入
        if inputs:
            for inp in inputs.split(','):
                place, tokens = inp.split(':')
                input_dict[place.strip()] = int(tokens.strip())
        
        # 处理输出
        if outputs:
            for out in outputs.split(','):
                place, tokens = out.split(':')
                output_dict[place.strip()] = int(tokens.strip())
        
        self.transitions[name] = {'inputs': input_dict, 'outputs': output_dict}
    
    def get_current_state(self):
        """获取当前状态"""
        return dict(self.places)
    
    def is_transition_enabled(self, transition_name):
        """检查转换是否可以触发"""
        transition = self.transitions[transition_name]
        
        # 检查所有输入位置是否有足够的标记
        for place, tokens in transition['inputs'].items():
            if self.places.get(place, 0) < tokens:
                return False
        
        return True
    
    def fire_transition(self, transition_name):
        """触发转换"""
        if not self.is_transition_enabled(transition_name):
            return False
        
        transition = self.transitions[transition_name]
        
        # 消耗输入标记
        for place, tokens in transition['inputs'].items():
            self.places[place] -= tokens
        
        # 产生输出标记
        for place, tokens in transition['outputs'].items():
            self.places[place] += tokens
        
        # 记录状态变化
        self.history.append(self.get_current_state())
        
        # 检查条件
        self.check_conditions(transition_name)
        
        return True
    
    def check_conditions(self, transition_name):
        """检查特定条件"""
        # 检查是否是接收数据包的转换
        if "receive" in transition_name.lower():
            current_host = transition_name.split('_')[-1]
            current_time = len(self.history)
            
            if self.last_received_host == current_host:
                # 检查在两次接收之间是否有数据包发送
                if not self.packet_sent_since_last_receive:
                    self.conditions_met = False
            
            self.last_received_host = current_host
            self.last_received_time = current_time
            self.packet_sent_since_last_receive = False
        
        # 检查是否是发送数据包的转换
        elif "send" in transition_name.lower():
            self.packet_sent_since_last_receive = True
    
    def get_enabled_transitions(self):
        """获取所有可触发的转换"""
        return [t for t in self.transitions if self.is_transition_enabled(t)]
    
    def simulate_step(self):
        """模拟一步"""
        enabled = self.get_enabled_transitions()
        if not enabled:
            return False
        
        # 随机选择一个可触发的转换
        transition = random.choice(enabled)
        self.fire_transition(transition)
        return True
    
    def simulate(self, steps=100):
        """模拟多步"""
        for _ in range(steps):
            if not self.simulate_step():
                break
        return self.conditions_met

class PetriNetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Petri网模拟器")
        self.simulator = PetriNetSimulator()
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入区域
        input_frame = tk.LabelFrame(main_frame, text="输入", padx=5, pady=5)
        input_frame.pack(fill=tk.X, pady=5)
        
        # 初始状态
        tk.Label(input_frame, text="初始状态 (格式: place1:tokens,place2:tokens):").pack(anchor=tk.W)
        self.initial_state_entry = tk.Entry(input_frame, width=50)
        self.initial_state_entry.pack(fill=tk.X, pady=2)
        self.initial_state_entry.insert(0, "HostA:1, HostB:1, Network:0, Packet:0")
        
        # 添加转换按钮
        tk.Button(input_frame, text="添加转换规则", command=self.add_transition).pack(pady=5)
        
        # 转换规则列表
        self.transitions_listbox = tk.Listbox(input_frame, height=5)
        self.transitions_listbox.pack(fill=tk.X, pady=2)
        
        # 模拟控制
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(control_frame, text="单步模拟", command=self.single_step).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="模拟10步", command=lambda: self.multi_step(10)).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="模拟100步", command=lambda: self.multi_step(100)).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="重置", command=self.reset).pack(side=tk.RIGHT, padx=2)
        
        # 输出区域
        output_frame = tk.LabelFrame(main_frame, text="输出", padx=5, pady=5)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # 状态显示
        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(status_frame, text="当前状态:").pack(side=tk.LEFT)
        self.current_state_label = tk.Label(status_frame, text="未初始化", relief=tk.SUNKEN)
        self.current_state_label.pack(fill=tk.X, expand=True, padx=5)
        
        tk.Label(status_frame, text="条件状态:").pack(side=tk.LEFT)
        self.condition_label = tk.Label(status_frame, text="未检查", relief=tk.SUNKEN)
        self.condition_label.pack(fill=tk.X, expand=True, padx=5)
        
        # 添加一些示例转换规则
        self.add_example_transitions()
    
    def add_example_transitions(self):
        """添加示例转换规则"""
        example_transitions = [
            ("Send_A", "HostA:1,Packet:0", "Network:1,Packet:1"),
            ("Send_B", "HostB:1,Packet:0", "Network:1,Packet:1"),
            ("Receive_A", "Network:1,Packet:1", "HostA:1,Packet:0"),
            ("Receive_B", "Network:1,Packet:1", "HostB:1,Packet:0"),
        ]
        
        for name, inputs, outputs in example_transitions:
            self.simulator.add_transition(name, inputs, outputs)
            self.transitions_listbox.insert(tk.END, f"{name}: {inputs} -> {outputs}")
    
    def add_transition(self):
        """添加新的转换规则"""
        name = simpledialog.askstring("添加转换", "输入转换名称:")
        if not name:
            return
        
        inputs = simpledialog.askstring("添加转换", "输入转换输入 (格式: place1:tokens,place2:tokens):")
        outputs = simpledialog.askstring("添加转换", "输入转换输出 (格式: place1:tokens,place2:tokens):")
        
        if inputs is None or outputs is None:
            return
        
        self.simulator.add_transition(name, inputs, outputs)
        self.transitions_listbox.insert(tk.END, f"{name}: {inputs} -> {outputs}")
        self.log_message(f"添加转换: {name}")
    
    def reset(self):
        """重置模拟器"""
        initial_state = self.initial_state_entry.get()
        try:
            self.simulator = PetriNetSimulator()
            self.simulator.load_initial_state(initial_state)
            
            # 重新添加转换规则
            for i in range(self.transitions_listbox.size()):
                item = self.transitions_listbox.get(i)
                name, rest = item.split(":", 1)
                inputs, outputs = rest.split("->")
                self.simulator.add_transition(name.strip(), inputs.strip(), outputs.strip())
            
            self.log_message("模拟器已重置")
            self.update_display()
        except Exception as e:
            messagebox.showerror("错误", f"初始化失败: {str(e)}")
    
    def single_step(self):
        """执行单步模拟"""
        if not hasattr(self.simulator, 'places') or not self.simulator.places:
            self.reset()
        
        enabled = self.simulator.get_enabled_transitions()
        if not enabled:
            self.log_message("没有可触发的转换")
            return
        
        transition = random.choice(enabled)
        self.simulator.fire_transition(transition)
        self.log_message(f"触发转换: {transition}")
        self.update_display()
    
    def multi_step(self, steps):
        """执行多步模拟"""
        if not hasattr(self.simulator, 'places') or not self.simulator.places:
            self.reset()
        
        for _ in range(steps):
            if not self.simulator.simulate_step():
                break
        
        self.log_message(f"完成 {steps} 步模拟")
        self.update_display()
    
    def update_display(self):
        """更新显示"""
        # 更新当前状态
        state = self.simulator.get_current_state()
        self.current_state_label.config(text=str(state))
        
        # 更新条件状态
        if self.simulator.conditions_met:
            self.condition_label.config(text="条件满足", bg="lightgreen")
        else:
            self.condition_label.config(text="条件不满足", bg="lightcoral")
    
    def log_message(self, message):
        """记录消息到输出区域"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.update()

def main():
    root = tk.Tk()
    app = PetriNetGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
