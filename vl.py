import json
import os
import datetime
import logging
from openai import OpenAI
from configparser import ConfigParser

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChatAssistant:
    def __init__(self):
        # 加载配置文件
        self.config = self.load_config()
        # 初始化配置目录
        self.init_config()
        # 加载提示词预设库
        self.preset_prompts = self.load_preset_prompts()
        # 加载对话历史记录
        self.preset_name, self.conversation_context = self.load_history()

    def load_config(self):
        try:
            config = ConfigParser()
            config.read('config.ini')
            return {
                'use_model': config.get('API', 'use_model'),
                'use_stream': config.getboolean('API', 'use_stream'),
                'use_temperature': config.getfloat('API', 'use_temperature'),
                'api_key': config.get('API', 'api_key'),
                'base_url': config.get('API', 'base_url')
            }
        except Exception as e:
            logging.error(f"加载配置文件失败: {e}")
            return {}

    def init_config(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        self.CONFIG_DIR = os.path.join(current_directory, '.assistant_config')
        self.HISTORY_FILE = os.path.join(self.CONFIG_DIR, 'conversation_history.json')
        if not os.path.exists(self.CONFIG_DIR):
            os.makedirs(self.CONFIG_DIR)

    def load_preset_prompts(self):
        file_content = self.read_txt_file('prompt.txt')
        return {
            "林汐然": file_content
        }

    def read_txt_file(self, file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logging.warning(f"文件 {file_name} 未找到。")
            return None
        except Exception as e:
            logging.error(f"读取文件时出现错误: {e}")
            return None

    def add_newline_after_punctuation(self, text):
        punctuation = '，。！？；：、……）'
        result = ""
        for char in text:
            result += char
            if char in punctuation:
                result += '\n'
        return result

    def save_history(self):
        try:
            with open(self.HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "preset": self.preset_name,
                    "history": self.conversation_context
                }, f, ensure_ascii=False, indent=2)
            logging.info(f"对话已保存到 {self.HISTORY_FILE}")
        except Exception as e:
            logging.error(f"保存历史记录失败: {e}")

    def load_history(self):
        try:
            if os.path.exists(self.HISTORY_FILE):
                with open(self.HISTORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data['preset'], data['history']
        except Exception as e:
            logging.error(f"加载历史记录失败: {e}")
        return None, []

    def select_preset(self):
        if self.preset_name and self.conversation_context:
            print(f"\n找到上次的对话记录（预设角色：{self.preset_name}）")
            choice = input("是否恢复上次对话？(y/n): ").lower()
            if choice == 'y':
                print("对话已恢复，输入'退出'结束对话")
                return
        print("\n可用的角色预设：")
        for i, (name, _) in enumerate(self.preset_prompts.items(), 1):
            print(f"{i}. {name}")
        while True:
            try:
                selected = int(input("请选择预设角色（输入编号）：")) - 1
                if 0 <= selected < len(self.preset_prompts):
                    self.preset_name = list(self.preset_prompts.keys())[selected]
                    self.conversation_context = [{"role": "system", "content": self.preset_prompts[self.preset_name]}]
                    break
                else:
                    print("输入的编号无效，请重新输入。")
            except ValueError:
                print("输入无效，请输入一个数字。")

    def get_current_time_info(self):
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
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
        return f"{formatted_time} {weekday}"

    def run(self):
        client = OpenAI(api_key=self.config.get('api_key'), base_url=self.config.get('base_url'))
        self.select_preset()
        while True:
            user_input = input("\nYou：").strip()
            if user_input.lower() in ["\\bye", "exit", "quit"]:
                save_choice = input("是否保存当前对话？(y/n): ").lower()
                if save_choice == 'y':
                    self.save_history()
                print("对话结束")
                break
            user_input = user_input + self.get_current_time_info()
            self.conversation_context.append({"role": "user", "content": user_input})
            try:
                response = client.chat.completions.create(
                    model=self.config.get('use_model'),
                    messages=self.conversation_context,
                    stream=self.config.get('use_stream'),
                    temperature=self.config.get('use_temperature')
                )
                ai_response = response.choices[0].message.content
                self.conversation_context.append({"role": "assistant", "content": ai_response})
                print(f"\n{self.preset_name}：", self.add_newline_after_punctuation(ai_response))
            except Exception as e:
                logging.error(f"发生错误：{e}")
                self.conversation_context = self.conversation_context[-4:]

if __name__ == "__main__":
    chat_assistant = ChatAssistant()
    chat_assistant.run()