import datetime
def get_current_time_info():
    # 获取当前时间
    current_time = datetime.datetime.now()
    # 格式化日期和时间
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    # 获取星期信息
    weekday_mapping = {
        0: "星期一",
        1: "星期二",
        2: "星期三",
        3: "星期四",
        4: "星期五",
        5: "星期六",
        6: "星期日"
    }
    weekday = weekday_mapping[current_time.weekday()]
    # 组合输出信息
    result = f"{formatted_time} {weekday}"
    return "["+result+"]"


def read_txt_file(file_name):
    try:
        # 使用with语句打开文件
        with open(file_name, 'r', encoding='utf-8') as file:
            # 读取整个文件内容到变量中
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"文件 {file_name} 未找到。\n")
        return None
    except Exception as e:
        print(f"读取文件时出现错误: {e}\n")
        return None

def add_newline_after_punctuation(text):
    # 定义需要添加换行符的标点符号
    punctuation = '，。！？；：、……）'
    result = ""
    for char in text:
        result += char
        if char in punctuation:
            result += '\n'
    return result