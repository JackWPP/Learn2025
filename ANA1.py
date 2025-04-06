def validate_regex(regex):
    """
    验证正则表达式的语法是否合法
    
    参数:
        regex: 待验证的正则表达式字符串
        
    返回:
        如果正则表达式合法，返回 -1
        如果不合法，返回错误位置的索引
    """
    if not regex:  # 空字符串视为合法
        return -1
        
    stack = []  # 用于括号匹配的栈
    
    for i, char in enumerate(regex):
        if char == '(':
            stack.append(('(', i))  # 记录左括号的类型和位置
        elif char == ')':
            if not stack or stack[-1][0] != '(':  # 没有匹配的左括号
                return i  # 返回错误位置
            stack.pop()  # 弹出匹配的左括号
        elif char == '[':
            stack.append(('[', i))  # 记录左中括号的类型和位置
        elif char == ']':
            if not stack or stack[-1][0] != '[':  # 没有匹配的左中括号
                return i  # 返回错误位置
            stack.pop()  # 弹出匹配的左中括号
        elif char == '*':
            # * 必须跟在字符或右括号后面
            if i == 0 or regex[i-1] in '(|':
                return i  # 返回错误位置
        # 此处正闭包与加号冲突 暂时保留 不处理 也就是 在该语法中 正闭包不合法 需要单独表示为a|a*
        #elif char == '+':
            # + 必须跟在字符或右括号后面
        #       if i == 0 or regex[i-1] in '(|':
              #  return i  # 返回错误位置
        elif char == '?':
            # ? 必须跟在字符或右括号后面
            if i == 0 or regex[i-1] in '(|':
                return i
        elif char == '.':
            # . 不能是表达式的第一个或最后一个字符
            if i == 0 or i == len(regex) - 1:
                return i
            # . 不能直接跟在左括号或另一个 . 后面
        elif char == '|':
            # | 不能是表达式的第一个或最后一个字符
            if i == 0 or i == len(regex) - 1:
                return i  # 返回错误位置
            # | 不能直接跟在左括号或另一个 | 后面
            if regex[i-1] in '|(': 
                return i  # 返回错误位置
            # | 后面不能直接是右括号或另一个 |
            if regex[i+1] in ')|':
                return i  # 返回错误位置
    
    # 检查未匹配的左括号
    if stack:
        return stack[0]  # 返回第一个未匹配的左括号位置
    
    # 通过所有检查，表达式合法
    return -1

def main():
    regex = input("请输入一个正则表达式: ")
    result = validate_regex(regex)
    if result == -1:
        print("正则表达式合法")
    else:
        print(f"不合法: 位置 {result}")

if __name__ == "__main__":
    main()