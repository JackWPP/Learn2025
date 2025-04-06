import random
import sys

class PetriNet:
    def __init__(self):
        self.places = {}  # 存储网络中的位置
        self.transitions = {}  # 存储转换规则
        self.tokens = {}  # 存储每个位置的标记数
        self.input_arcs = {}  # 转换的输入弧
        self.output_arcs = {}  # 转换的输出弧
        self.events = []  # 记录事件序列
        self.host_events = {}  # 按主机记录事件
    
    def add_place(self, place_id, tokens=0):
        """添加一个位置到Petri网"""
        self.places[place_id] = place_id
        self.tokens[place_id] = tokens
    
    def add_transition(self, transition_id, event_type=None, host=None):
        """添加一个转换到Petri网"""
        self.transitions[transition_id] = {
            "id": transition_id,
            "event_type": event_type,  # 'send' 或 'receive'
            "host": host
        }
        self.input_arcs[transition_id] = []
        self.output_arcs[transition_id] = []
    
    def add_arc(self, source, target):
        """添加一个弧到Petri网"""
        if source in self.places and target in self.transitions:
            # 从位置到转换的弧
            self.input_arcs[target].append(source)
        elif source in self.transitions and target in self.places:
            # 从转换到位置的弧
            self.output_arcs[source].append(target)
        else:
            raise ValueError(f"无效的弧: {source} -> {target}")
    
    def is_enabled(self, transition_id):
        """检查转换是否启用"""
        if transition_id not in self.transitions:
            return False
        
        # 检查所有输入位置是否有足够的标记
        for place in self.input_arcs[transition_id]:
            if self.tokens[place] <= 0:
                return False
        return True
    
    def fire_transition(self, transition_id, step):
        """触发一个转换"""
        if not self.is_enabled(transition_id):
            return False
        
        # 从输入位置移除标记
        for place in self.input_arcs[transition_id]:
            self.tokens[place] -= 1
        
        # 向输出位置添加标记
        for place in self.output_arcs[transition_id]:
            self.tokens[place] += 1
        
        # 记录事件
        trans_info = self.transitions[transition_id]
        if trans_info["event_type"] and trans_info["host"]:
            event = (step, trans_info["event_type"], trans_info["host"])
            self.events.append(event)
            
            # 按主机记录事件
            host = trans_info["host"]
            if host not in self.host_events:
                self.host_events[host] = []
            self.host_events[host].append((step, trans_info["event_type"]))
        
        return True
    
    def get_enabled_transitions(self):
        """获取所有启用的转换"""
        return [t for t in self.transitions if self.is_enabled(t)]
    
    def random_step(self, step):
        """随机选择一个启用的转换并触发它"""
        enabled = self.get_enabled_transitions()
        if not enabled:
            return None
        
        transition = random.choice(enabled)
        success = self.fire_transition(transition, step)
        return transition if success else None
    
    def check_condition(self):
        """检查是否有一个主机在接收两个数据包之间没有任何主机发送新数据包"""
        for host, events in self.host_events.items():
            # 获取该主机的接收事件
            receive_events = [(step, evt) for step, evt in events if evt == "receive"]
            
            if len(receive_events) < 2:
                continue
            
            for i in range(1, len(receive_events)):
                prev_step = receive_events[i-1][0]
                curr_step = receive_events[i][0]
                
                # 检查这两次接收之间是否有任何发送事件
                send_between = False
                for step, evt_type, _ in self.events:
                    if evt_type == "send" and prev_step < step < curr_step:
                        send_between = True
                        break
                
                if not send_between:
                    return True, host, prev_step, curr_step
        
        return False, None, None, None

def parse_input():
    """解析输入文件或标准输入"""
    petri_net = PetriNet()
    
    # 读取位置
    n_places = int(input())
    for _ in range(n_places):
        place_id, tokens = input().split()
        petri_net.add_place(place_id, int(tokens))
    
    # 读取转换
    n_transitions = int(input())
    for _ in range(n_transitions):
        parts = input().split()
        if len(parts) == 3:
            trans_id, event_type, host = parts
            petri_net.add_transition(trans_id, event_type, host)
        else:
            trans_id = parts[0]
            petri_net.add_transition(trans_id)
    
    # 读取弧
    n_arcs = int(input())
    for _ in range(n_arcs):
        source, target = input().split()
        petri_net.add_arc(source, target)
    
    return petri_net

def simulate(petri_net, max_steps=1000):
    """模拟Petri网的运行"""
    print("开始模拟...")
    
    step = 0
    while step < max_steps:
        transition = petri_net.random_step(step)
        if transition is None:
            print(f"在步骤 {step} 没有可启用的转换，模拟停止。")
            break
        
        # 检查条件
        condition_met, host, step1, step2 = petri_net.check_condition()
        if condition_met:
            print(f"\n发现满足条件的情况!")
            print(f"主机 {host} 在步骤 {step1} 和 {step2} 接收了数据包，")
            print(f"但在这两次接收之间没有任何主机发送新的数据包。")
            return True
        
        step += 1
    
    print(f"\n模拟完成 {step} 步，未发现符合条件的情况。")
    return False

def main():
    print("Petri网络模拟器")
    print("读取网络配置...")
    
    # 解析输入
    petri_net = parse_input()
    
    # 运行模拟
    simulate(petri_net)

if __name__ == "__main__":
    main()
