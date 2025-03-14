import json
import os
from openai import OpenAI
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
    return result


# 配置文件路径
# 获取当前脚本文件的绝对路径
current_script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录
current_directory = os.path.dirname(current_script_path)
# 拼接配置文件夹的路径
CONFIG_DIR = os.path.join(current_directory, '.assistant_config')
# 拼接对话历史文件的路径
HISTORY_FILE = os.path.join(CONFIG_DIR, 'conversation_history.json')

use_model="deepseek-reasoner"
use_stream=False
use_temperature=0.3
api_key_s = "sk-42576b8258364c2e8f350e511708e767"
urls="https://api.deepseek.com"
client = OpenAI(api_key=api_key_s, base_url=urls)

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


# 调用函数并传入文件名
file_content = read_txt_file('prompt.txt')

# 提示词预设库
preset_prompts = {

    "默认助手": "你是一个乐于助人的AI助手",
    "技术顾问": "你是一个资深技术专家，擅长用简洁易懂的方式解释复杂概念",
    "翻译家": "你是一个专业翻译，能够准确翻译中英文内容",
    "面试官": "你是一个技术面试官，会提出有挑战性的问题并给出改进建议",
    "林汐然": file_content
}


# 初始化配置目录
def init_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)


# 保存对话上下文
def save_history(preset_name, context):
    init_config()
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "preset": preset_name,
                "history": context
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存历史记录失败: {str(e)}")


# 加载历史记录
def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['preset'], data['history']
    except Exception as e:
        print(f"加载历史记录失败: {str(e)}")
    return None, None



# 主程序
def main():
    # 尝试加载历史记录
    saved_preset, saved_context = load_history()

    if saved_preset and saved_context:
        print(f"\n找到上次的对话记录（预设角色：{saved_preset}）")
        choice = input("是否恢复上次对话？(y/n): ").lower()
        if choice == 'y':
            preset_name = saved_preset
            conversation_context = saved_context
            print("对话已恢复，输入'退出'结束对话")
        else:
            saved_preset = None

    if not saved_preset:
        # 选择预设流程
        print("\n可用的角色预设：")
        for i, (name) in enumerate(preset_prompts.items(), 1):
            print(f"{i}. {name}")

        selected = int(input("请选择预设角色（输入编号）：")) - 1
        preset_name = list(preset_prompts.keys())[selected]

    # 对话循环
    while True:
        user_input = input("\nYou：").strip()

        if user_input.lower() in ["\\bye", "exit", "quit"]:
            save_choice = input("是否保存当前对话？(y/n): ").lower()
            if save_choice == 'y':
                save_history(preset_name, conversation_context)
                print(f"对话已保存到 {HISTORY_FILE}")
            print("对话结束")
            break
        user_input = user_input + get_current_time_info()
        conversation_context.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model=use_model,
                messages=conversation_context,
                stream=use_stream,
                temperature=use_temperature
            )

            ai_response = response.choices[0].message.content
            conversation_context.append({"role": "assistant", "content": ai_response})

            print(f"\n{preset_name}：", ai_response)

        except Exception as e:
            print("发生错误：", str(e))
            conversation_context = conversation_context[-4:]


if __name__ == "__main__":
    main()