import json
import os
from openai import OpenAI
from utils import get_current_time_info, read_txt_file, add_newline_after_punctuation




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
use_stream=True
use_temperature=0.7
api_key_s = "sk-42576b8258364c2e8f350e511708e767"
urls="https://api.deepseek.com"
client = OpenAI(api_key=api_key_s, base_url=urls)




# 调用函数并传入文件名
file_content = read_txt_file('prompt.txt')

# 提示词预设库
preset_prompts = {
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

            print(f"\n{preset_name}：", add_newline_after_punctuation(ai_response))

        except Exception as e:
            print("发生错误：", str(e))
            conversation_context = conversation_context[-4:]


if __name__ == "__main__":
    main()