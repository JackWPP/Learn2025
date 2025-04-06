import tkinter as tk
from tkinter import filedialog, messagebox
import random

# 定义转换类，每个转换包含事件类型（"send"或"receive"）和主机标识
class Transition:
    def __init__(self, event_type, host):
        self.event_type = event_type.strip().lower()  # "send" 或 "receive"
        self.host = host.strip()
    
    def __repr__(self):
        return f"{self.event_type}({self.host})"

# 定义 Petri 网模拟器类
class PetriNetSimulator:
    def __init__(self):
        self.transitions = []          # 所有转换规则列表
        self.current_state = []        # 日志：依次记录触发的转换
        self.last_receive = {}         # 记录每个主机是否刚刚发生过“receive”事件（未被其他主机的send打断）
        self.violation_callback = None # 如果设置了回调函数，违规时会调用此函数显示提示
    
    def load_transitions(self, filename):
        """
        从指定文件加载转换规则。文件中每行格式为： event_type,host
        例如：
            send,host1
            receive,host1
            send,host2
            receive,host2
        """
        with open(filename, "r") as f:
            lines = f.readlines()
        self.transitions = []
        for line in lines:
            line = line.strip()
            if line:
                parts = line.split(',')
                if len(parts) == 2:
                    t = Transition(parts[0], parts[1])
                    self.transitions.append(t)
        # 初始化所有出现过的主机的 last_receive 标志
        hosts = {t.host for t in self.transitions}
        self.last_receive = {host: False for host in hosts}
        self.current_state = []

    def load_default_transitions(self):
        """
        如果没有转换文件，则可以加载内置的默认转换规则。
        """
        self.transitions = [
            Transition("send", "host1"),
            Transition("receive", "host1"),
            Transition("send", "host2"),
            Transition("receive", "host2"),
            Transition("send", "host3"),
            Transition("receive", "host3")
        ]
        hosts = {t.host for t in self.transitions}
        self.last_receive = {host: False for host in hosts}
        self.current_state = []

    def reset(self):
        """重置模拟器状态，清空日志并重置各主机状态"""
        self.current_state = []
        for host in self.last_receive:
            self.last_receive[host] = False

    def step(self):
        """
        模拟一步：从所有转换中随机选择一个触发，并更新状态及检测违规。
        返回触发的转换，如果没有可用转换则返回 None。
        """
        if not self.transitions:
            return None
        transition = random.choice(self.transitions)
        self.current_state.append(transition)
        self.update_condition(transition)
        return transition

    def update_condition(self, transition):
        """
        根据触发的转换更新状态：
          - 如果是 send 事件，则对于除当前主机以外的所有主机，重置 last_receive 标志（即打断连续接收链）。
          - 如果是 receive 事件，则检测该主机是否已经存在连续接收（标志为 True）。
        """
        if transition.event_type == "send":
            # 只有其他主机的 send 才会打断其连续接收记录
            for host in self.last_receive:
                if host != transition.host:
                    self.last_receive[host] = False
        elif transition.event_type == "receive":
            # 如果该主机此前已记录有一次接收而未被其他主机 send 打断，则触发违规提示
            if self.last_receive.get(transition.host, False):
                self.alert_violation(transition.host)
            else:
                self.last_receive[transition.host] = True

    def alert_violation(self, host):
        """调用违规提示回调函数显示违规信息"""
        msg = (f"违规警告：主机 {host} 连续接收了两个数据包，且在两次接收之间没有其他主机发送数据包！\n")
        if self.violation_callback:
            self.violation_callback(msg)
        else:
            print(msg)

# 定义图形用户界面类
class PetriNetGUI:
    def __init__(self, root):
        self.root = root
        root.title("Petri 网模拟器")
        
        # 创建模拟器实例，并将违规提示回调设置为在日志中显示信息
        self.simulator = PetriNetSimulator()
        self.simulator.violation_callback = self.show_alert
        
        # 日志显示区域
        self.log_text = tk.Text(root, height=20, width=80)
        self.log_text.pack(padx=10, pady=5)
        
        # 按钮区域
        btn_frame = tk.Frame(root)
        btn_frame.pack(padx=10, pady=5)
        
        self.load_button = tk.Button(btn_frame, text="加载转换规则", command=self.load_transitions)
        self.load_button.pack(side=tk.LEFT, padx=5)
        
        self.default_button = tk.Button(btn_frame, text="加载默认转换", command=self.load_default)
        self.default_button.pack(side=tk.LEFT, padx=5)
        
        self.start_button = tk.Button(btn_frame, text="开始模拟", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(btn_frame, text="重置", command=self.reset_simulation)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # 显示说明信息
        instructions = (
            "【程序说明】\n"
            "1. 点击“加载转换规则”按钮，从文件中加载转换规则，文件中每行的格式为：\n"
            "   event_type,host  （例如：send,host1 或 receive,host1）\n"
            "2. 或点击“加载默认转换”按钮，使用内置默认规则。\n"
            "3. 点击“开始模拟”后，程序将从初始状态开始，随机选择并触发转换；\n"
            "   模拟过程中会检测是否有主机在连续接收两个数据包（中间没有其他主机发送数据包），\n"
            "   若检测到则在日志中显示违规警告。\n"
            "4. 点击“重置”按钮可清空日志和内部状态，重新开始模拟。"
        )
        self.instruction_label = tk.Label(root, text=instructions, justify=tk.LEFT)
        self.instruction_label.pack(padx=10, pady=5)
    
    def load_transitions(self):
        """通过文件对话框加载转换规则文件"""
        filename = filedialog.askopenfilename(title="选择转换规则文件")
        if filename:
            try:
                self.simulator.load_transitions(filename)
                self.log_text.insert(tk.END, f"成功加载 {len(self.simulator.transitions)} 条转换规则，来自文件：{filename}\n")
            except Exception as e:
                messagebox.showerror("错误", str(e))
    
    def load_default(self):
        """加载内置默认转换规则"""
        self.simulator.load_default_transitions()
        self.log_text.insert(tk.END, f"已加载默认转换规则，共 {len(self.simulator.transitions)} 条\n")
    
    def start_simulation(self):
        """开始模拟，演示 20 个步骤或直到没有转换可触发"""
        self.simulator.reset()
        self.log_text.insert(tk.END, "开始模拟...\n")
        # 模拟 20 步
        for i in range(20):
            transition = self.simulator.step()
            if transition is None:
                self.log_text.insert(tk.END, "无可用转换，模拟终止。\n")
                break
            self.log_text.insert(tk.END, f"步骤 {i+1}: 触发转换 {transition}\n")
            # 为了让日志显示效果更直观，可调用 update 更新界面
            self.root.update()
        self.log_text.insert(tk.END, "模拟结束。\n\n")
    
    def reset_simulation(self):
        """重置模拟器状态和日志显示"""
        self.simulator.reset()
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, "已重置模拟器状态。\n")
    
    def show_alert(self, msg):
        """当检测到违规时，将信息写入日志并弹出提示框"""
        self.log_text.insert(tk.END, msg)
        messagebox.showwarning("违规警告", msg)

if __name__ == "__main__":
    root = tk.Tk()
    gui = PetriNetGUI(root)
    root.mainloop()
