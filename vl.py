import os
from utils import read_specific_line

# 配置文件路径
# 获取当前脚本文件的绝对路径
current_script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录
current_directory = os.path.dirname(current_script_path)
msd = current_directory+"/modelSettings/model.txt"
class modelSettings:
    def __init__(self, model, api_key_s, urls):
        self.model = model
        self.api_key_s = api_key_s
        self.urls = urls

    def introduce(self):
        print(self.model,self.api_key_s,self.urls)

useModelSettings = modelSettings(read_specific_line(msd,1),read_specific_line(msd,2),read_specific_line(msd,3))
useModelSettings.introduce()
use_model=useModelSettings.model
api_key_s = useModelSettings.api_key_s
urls=useModelSettings.urls