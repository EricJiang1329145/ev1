import os
from utils import search_files, ask_user_choice
current_script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录
current_directory = os.path.dirname(current_script_path)
# 拼接配置文件夹的路径
CONFIG_DIR = os.path.join(current_directory, '.assistant_config')
# 拼接对话历史文件的路径
HISTORY_FILE = os.path.join(CONFIG_DIR, 'conversation_history.json')


