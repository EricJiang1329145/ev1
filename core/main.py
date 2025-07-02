import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI

from tknz.deepseek_tokenizer import get_tokenize
<<<<<<< HEAD:main.py
from utils import *
import os
from dotenv import load_dotenv
=======
from utils.utils import *
>>>>>>> 14b239cc39d1cfd8b5024da405b102effec17145:core/main.py


class ConfigManager:
    def __init__(self):
<<<<<<< HEAD:main.py
        load_dotenv()  # 加载.env文件
        self.CONFIG_DIR = os.getenv('ASSISTANT_CONFIG', '.assistant_config')
        self.tknz_path = os.path.join(os.path.dirname(__file__), 'tknz')
        self.HISTORY_FILE = os.path.join(self.CONFIG_DIR, 'conversation_history.json')
        self.model_settings_dir = os.getenv('MODEL_SETTINGS_DIR', 'modelSettings')
=======
        # 拼接配置文件夹的路径
        self.CONFIG_DIR = '../.assistant_config'
        # 拼接 tknz 的路径
        self.tknz_path = '../tknz'
        # 拼接对话历史文件的路径
        self.HISTORY_FILE = os.path.join(self.CONFIG_DIR, 'conversation_history.json')
        # 获取模型配置相关内容
        self.model_settings_dir = "../modelSettings"
>>>>>>> 14b239cc39d1cfd8b5024da405b102effec17145:core/main.py

config = ConfigManager()
def selected_file():
    files = search_files(config.model_settings_dir)
    selected_file = ask_user_choice(files)
    print(f"\033[31m你选择的文件是: \033[0m{selected_file}")
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
        OperationLogger.log_operation('对话保存', '成功')
    except Exception as e:
        OperationLogger.log_error('对话保存', e)


# 加载历史记录
def load_history():
    try:
        if os.path.exists(config.HISTORY_FILE):
            with open(config.HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['preset'], data['history']
    except Exception as e:
        print(f"\033[31m加载历史记录失败: \033[0m{str(e)}")
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
    # 初始化OpenAI客户端前添加验证
    if not api_key_s:
        print("\033[31m错误: API密钥未配置，请检查modelSettings文件或设置环境变量\033[0m")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key_s, base_url=urls)

    # 调用函数并传入文件名
    file_content = read_txt_file('../prompt.txt')

    # 提示词预设库
    preset_prompts = {"林汐然": file_content}
    # 尝试加载历史记录
    saved_preset, saved_context = load_history()

    if saved_preset and saved_context:
        print(f"\n\033[31m找到上次的对话记录（预设角色：\033[0m{saved_preset}）")
        choice = safe_input("\033[31m是否恢复上次对话？(\033[0my\033[31m/\033[0mn\033[31m):\033[0m ").lower()
        if choice == 'y':
            preset_name = saved_preset
            conversation_context = saved_context
            print("\033[31m对话已恢复，输入'退出'结束对话\033[0m")
            modify_json_system_content(config.HISTORY_FILE, file_content)

        else:
            saved_preset = None

    if not saved_preset:
        # 选择预设流程
        conversation_context = []
        print("\n\033[31m可用的角色预设：\033[0m")
        for i, (name) in enumerate(preset_prompts.items(), 1):
            print(f"{i}. {name}")

        selected = int(input("\033[31m请选择预设角色（输入编号）：\033[0m")) - 1
        preset_name = list(preset_prompts.keys())[selected]

    # 对话循环
    while True:
        user_input = safe_input("\n\033[36mYou：\033[0m").strip()

        if user_input.lower() in ["\\bye", "exit", "quit"]:
            # 原有退出逻辑保持不变
            save_choice = input("\033[31m是否保存当前对话？(y/n): \033[0m").lower()
            if save_choice == 'y':
                save_history(preset_name, conversation_context)
                print(f"\033[32m对话已保存到 {config.HISTORY_FILE}\033[30m")
            print("对话结束")
            break
        user_input = user_input + get_current_time_info()
        print(get_tokenize(user_input, config.tknz_path))
        conversation_context.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(model=use_model,
                messages=conversation_context,
                stream=use_stream,
                temperature=use_temperature)

            ai_response = preprocess_response(response.choices[0].message.content).lstrip()
            conversation_context.append({"role": "assistant", "content": ai_response})

            print(f"\n{preset_name}：", add_newline_after_punctuation(ai_response))
            print(get_tokenize(ai_response, config.tknz_path))
        except Exception as e:
            print("\033[31m发生错误：\033[0m", str(e))
            conversation_context = conversation_context[-4:]


def print_welcome():
    print("欢迎使用本程序！")
    print("\033[31m这是红色文本\033[0m")
    print("\033[32m这是绿色文本\033[0m")
    print("\033[1;34m这是亮蓝色文本\033[0m")

def calculate_sum():
    total = sum(range(1, 11))
    print(f"1 到 10 的和是：{total}")


def exit_program():
    print("程序已退出。")
    sys.exit()


def configure_environment_vars():
    default_config = {
        'ASSISTANT_CONFIG': '.assistant_config',
        'MODEL_SETTINGS_DIR': 'modelSettings'
    }
    
    print("\n当前环境变量配置：")
    print(f"1. ASSISTANT_CONFIG: {os.getenv('ASSISTANT_CONFIG', default_config['ASSISTANT_CONFIG'])}")
    print(f"2. MODEL_SETTINGS_DIR: {os.getenv('MODEL_SETTINGS_DIR', default_config['MODEL_SETTINGS_DIR'])}")
    
    choice = safe_input("\033[31m请选择要修改的配置项（1-2）或输入'r'恢复默认: \033[0m")
    
    if choice.lower() == 'r':
        with open('.env', 'w') as f:
            f.write('')  # 清空配置文件
        print("\033[32m已恢复默认配置！\033[0m")
        return
    
    if choice == '1':
        new_path = input("请输入新的ASSISTANT_CONFIG路径（直接回车使用默认）: ").strip()
        value = new_path if new_path else default_config['ASSISTANT_CONFIG']
        os.environ['ASSISTANT_CONFIG'] = value
        update_env_file('ASSISTANT_CONFIG', value)
    elif choice == '2':
        new_dir = input("请输入新的MODEL_SETTINGS_DIR路径（直接回车使用默认）: ").strip()
        value = new_dir if new_dir else default_config['MODEL_SETTINGS_DIR']
        os.environ['MODEL_SETTINGS_DIR'] = value
        update_env_file('MODEL_SETTINGS_DIR', value)


def perform_operation():
    operations = {
        1: print_welcome,
        2: calculate_sum,
        3: main,
        4: exit_program,
        5: configure_environment_vars
    }
    try:
        for key, value in operations.items():
            print(f"{key}. {value.__name__.replace('_', ' ').title()}")
        
        choice = int(safe_input("\033[31m请输入操作对应的数字：\033[0m"))
        
        if choice in operations:
            operations[choice]()
        else:
            print("\033[31m输入无效，请重新选择\033[0m")
    except ExitToMain:
        print("\033[33m\n返回主菜单...\033[0m")
    except ValueError:
        print("\033[31m请输入有效数字\033[0m")
    perform_operation()


if __name__ == "__main__":
    init_config()
    
    print_welcome()
    perform_operation()


def update_env_file(key, value):
    env_lines = []
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_lines = f.readlines()
    
    # 移除旧配置
    env_lines = [line for line in env_lines if not line.startswith(f'{key}=')]
    
    # 添加新配置
    env_lines.append(f'{key}={value}\n')
    
    with open('.env', 'w') as f:
        f.writelines(env_lines)
    print("\033[32m配置已持久化保存！\033[0m")

// ... existing code ...
        OperationLogger.log_operation('环境变量更新', '成功')
    except Exception as e:
        OperationLogger.log_error('环境变量更新', e)


def perform_operation():
    operations = {
        1: print_welcome,
        2: calculate_sum,
        3: main,
        4: exit_program,
        5: configure_environment_vars
    }
    try:
        for key, value in operations.items():
            print(f"{key}. {value.__name__.replace('_', ' ').title()}")
        
        choice = int(safe_input("\033[31m请输入操作对应的数字：\033[0m"))
        
        if choice in operations:
            operations[choice]()
        else:
            print("\033[31m输入无效，请重新选择\033[0m")
    except ExitToMain:
        print("\033[33m\n返回主菜单...\033[0m")
    except ValueError:
        print("\033[31m请输入有效数字\033[0m")
    perform_operation()


if __name__ == "__main__":

    print_welcome()
    perform_operation()


def update_env_file(key, value):
    env_lines = []
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_lines = f.readlines()
    
    # 移除旧配置
    env_lines = [line for line in env_lines if not line.startswith(f'{key}=')]
    
    # 添加新配置
    env_lines.append(f'{key}={value}\n')
    
    with open('.env', 'w') as f:
        f.writelines(env_lines)
    print("\033[32m配置已持久化保存！\033[0m")
