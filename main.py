import json
import os
import sys

from openai import OpenAI

from tknz.deepseek_tokenizer import get_tokenize
from utils import add_newline_after_punctuation, extract_content_after_think, read_specific_line
from utils import get_current_time_info, read_txt_file
from utils import modify_json_system_content
from utils import search_files, ask_user_choice


class ConfigManager:
    def __init__(self):
        # 拼接配置文件夹的路径
        self.CONFIG_DIR = '.assistant_config'
        # 拼接 tknz 的路径
        self.tknz_path = 'tknz'
        # 拼接对话历史文件的路径
        self.HISTORY_FILE = os.path.join(self.CONFIG_DIR, 'conversation_history.json')
        # 获取模型配置相关内容
        self.model_settings_dir = "modelSettings"

config = ConfigManager()
def selected_file():
    files = search_files(config.model_settings_dir)
    selected_file = ask_user_choice(files)
    print(f"你选择的文件是: {selected_file}")
    return selected_file


class ModelSettings:
    def __init__(self, model, api_key, url):
        self.model = model
        self.apiKey = api_key
        self.url = url

    def introduce(self):
        print(self.model, self.apiKey, self.url)



# 初始化配置目录
def init_config():
    if not os.path.exists(config.CONFIG_DIR):
        os.makedirs(config.CONFIG_DIR)


# 保存对话上下文
def save_history(preset_name, context):
    init_config()
    try:
        with open(config.HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump({"preset": preset_name, "history": context}, f, ensure_ascii=False, indent=2)  # type: ignore
    except Exception as e:
        print(f"保存历史记录失败: {str(e)}")


# 加载历史记录
def load_history():
    try:
        if os.path.exists(config.HISTORY_FILE):
            with open(config.HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['preset'], data['history']
    except Exception as e:
        print(f"加载历史记录失败: {str(e)}")
    return None, None


# 主程序
def main():
    msd = selected_file()
    ums = ModelSettings(read_specific_line(msd, 1), read_specific_line(msd, 2), read_specific_line(msd, 3))
    ums.introduce()
    use_model = ums.model
    api_key_s = ums.apiKey
    urls = ums.url

    use_stream = False
    use_temperature = 0.9
    client = OpenAI(api_key=api_key_s, base_url=urls)

    # 调用函数并传入文件名
    file_content = read_txt_file('prompt.txt')

    # 提示词预设库
    preset_prompts = {"林汐然": file_content}
    # 尝试加载历史记录
    saved_preset, saved_context = load_history()

    if saved_preset and saved_context:
        print(f"\n找到上次的对话记录（预设角色：{saved_preset}）")
        choice = input("是否恢复上次对话？(y/n): ").lower()
        if choice == 'y':
            preset_name = saved_preset
            conversation_context = saved_context
            print("对话已恢复，输入'退出'结束对话")
            modify_json_system_content(config.HISTORY_FILE, file_content)

        else:
            saved_preset = None

    if not saved_preset:
        # 选择预设流程
        conversation_context = []
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
                print(f"对话已保存到 {config.HISTORY_FILE}")
            print("对话结束")
            break
        user_input = user_input + get_current_time_info()
        print(get_tokenize(user_input, config.tknz_path))
        conversation_context.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(model=use_model, messages=conversation_context, stream=use_stream,
                temperature=use_temperature)

            ai_response = extract_content_after_think(response.choices[0].message.content).lstrip()
            conversation_context.append({"role": "assistant", "content": ai_response})

            print(f"\n{preset_name}：", add_newline_after_punctuation(ai_response))
            print(get_tokenize(ai_response, config.tknz_path))
        except Exception as e:
            print("发生错误：", str(e))
            conversation_context = conversation_context[-4:]


def print_welcome():
    print("欢迎使用本程序！")


def calculate_sum():
    total = sum(range(1, 11))
    print(f"1 到 10 的和是：{total}")


def exit_program():
    print("程序已退出。")
    sys.exit()


def perform_operation():
    operations = {
        1: print_welcome,
        2: calculate_sum,
        3 : main,
        4: exit_program
    }
    for key, value in operations.items():
        print(f"{key}. {value.__name__}")
    try:
        choice = int(input("请输入操作对应的数字："))
        if choice in operations:
            result = operations[choice]()
            if result is not None:
                return
        else:
            print("输入的数字无效，请输入 1 - 3 之间的数字。")
    except ValueError:
        print("输入无效，请输入一个有效的整数。")
    perform_operation()


if __name__ == "__main__":

    print_welcome()
    perform_operation()
