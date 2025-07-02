import datetime
import os
import json
import re
import logging
from logging.config import fileConfig


def replace_consecutive_newlines(input_string):
    pattern = r'\n{2,}'
    return re.sub(pattern, '\n', input_string)


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

def extract_content_after_think(input_str):
    # 查找 </think> 的位置
    index = input_str.find("</think>")
    if index != -1:
        # 如果找到 </think>，则返回其后的部分
        return input_str[index + len("</think>"):]
    else:
        # 如果未找到 </think>，则返回原始字符串
        return input_str
# 定义一个函数，用于预处理响应
def preprocess_response(response):
    return replace_consecutive_newlines(extract_content_after_think(response)).lstrip()
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
    punctuation = '，。！？；：、.,…）'
    result = ""
    consecutive_punctuation = ""
    for char in text:
        if char in punctuation:
            consecutive_punctuation += char
        else:
            if consecutive_punctuation:
                result += consecutive_punctuation + '\n'
                consecutive_punctuation = ""
            result += char
    # 处理字符串结尾的连续标点符号
    if consecutive_punctuation:
        result += consecutive_punctuation + '\n'
    return result

def read_specific_line(file_path, line_number):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for i, line in enumerate(file, start=1):
                if i == line_number:
                    print(f"成功读取 {file_path} 第 {line_number} 行内容")
                    return line.strip()
            return None
    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 未找到。")
    except Exception as e:
        print(f"错误: 发生未知错误 - {e}")
    return None

def search_files(directory):
    """
    搜索指定目录下所有可读取的文件
    :param directory: 要搜索的目录
    :return: 可读取文件的列表
    """
    file_list = []
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        file_list.append(file_path)
                except Exception:
                    continue
    return file_list

def modify_json_system_content(file_path, new_content):
    try:
        if not os.path.exists(file_path):
            print("错误: 文件未找到。")
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for entry in data.get("history", []):
            if entry.get("role") == "system":
                entry["content"] = new_content
                break

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print("JSON 文件已成功更新。")
    except json.JSONDecodeError:
        print("错误: 无法解析 JSON 文件。")
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")

def ask_user_choice(files):
    try:
        for i, file in enumerate(files, 1):
            print(f"{i}. {file}")
        choice = int(safe_input("请输入要使用的文件编号: "))
        return files[choice-1]
    except ExitToMain:
        print("\033[33m返回主菜单...\033[0m")
        raise
    except (ValueError, IndexError):
        print("\033[31m输入无效，请重新选择\033[0m")
        return ask_user_choice(files)

class ExitToMain(Exception):
    pass

def safe_input(prompt):
    try:
        user_input = input(prompt)
        if user_input.strip().lower() in ('\exit', '\quit'):
            raise ExitToMain
        return user_input
    except EOFError:
        raise ExitToMain


# 日志配置路径
LOG_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config/logging_config.ini')

def init_logging():
    try:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        fileConfig(LOG_CONFIG_PATH)
        logger = logging.getLogger(__name__)
        logger.info('日志系统初始化成功')
    except Exception as e:
        logging.basicConfig(level=logging.INFO)
        logging.error(f'日志配置加载失败，使用基础配置: {str(e)}')

class OperationLogger:
    @staticmethod
    def log_operation(operation: str, status: str):
        logging.info(f'[{operation}] 操作状态: {status}')

    @staticmethod
    def log_error(operation: str, error: Exception):
        logging.error(f'[{operation}] 发生错误', exc_info=error)
