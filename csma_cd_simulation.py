import random

class Station:
    def __init__(self, station_id, initial_attempt_time):
        self.id = station_id               # 站点ID
        self.collision_count = 0          # 冲突次数计数器
        self.next_attempt_time = initial_attempt_time  # 下次尝试发送的时间
        self.success_time = None          # 成功发送的时间（未成功则为None）

def main():
    # 用户输入参数
    N = int(input("请输入站点数N: "))
    D = int(input("请输入初始帧剩余时隙数D: "))
    F = int(input("请输入每个帧传输所需时隙数F: "))

    # 初始化所有站点，设置初始尝试时间为D（初始帧传输结束的时间）
    stations = [Station(i, D) for i in range(N)]
    busy_until = D - 1  # 信道忙碌直到D-1时隙（初始帧传输期）
    current_time = 0     # 当前时间从0开始
    success_count = 0    # 成功发送的站点计数器

    # 主循环：模拟每个时隙的行为
    while success_count < N:
        # 如果当前信道忙碌，直接跳到信道空闲的时隙
        if current_time <= busy_until:
            current_time = busy_until + 1
            continue

        # 收集所有可以在此刻尝试发送的站点（未成功且计划时间<=当前时间）
        candidates = [s for s in stations if s.success_time is None and s.next_attempt_time <= current_time]

        if not candidates:
            current_time += 1  # 无站点尝试，时间递增
            continue

        if len(candidates) == 1:
            # 单个站点成功发送
            station = candidates[0]
            station.success_time = current_time
            busy_until = current_time + F - 1  # 信道占用到传输结束
            success_count += 1
            current_time = busy_until + 1      # 直接跳到信道空闲的下一时隙
        else:
            # 处理冲突：所有候选站点更新退避时间
            for station in candidates:
                station.collision_count += 1
                k = min(station.collision_count, 10)  # 冲突次数上限10
                r = random.randint(0, (2 ** k) - 1)   # 随机退避时隙
                station.next_attempt_time = current_time + 1 + r  # 下次尝试时间
            current_time += 1  # 时间递增，继续下一时隙

    # 按站点ID排序输出结果
    print("\n各站点成功发送的时间（时隙单位，每时隙51.2微秒）:")
    for station in sorted(stations, key=lambda x: x.id):
        print(f"站点 {station.id}: {station.success_time}")

if __name__ == "__main__":
    main()
