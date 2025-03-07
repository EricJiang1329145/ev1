import requests

url = "http://localhost:11434/api/generate"
headers = {"Content-Type": "application/json"}

data = {
    "model": "deepseek-r1:14b",  # 替换为你下载的模型名称
    "prompt": "为什么天空是蓝色的？",
    "stream": False  # 是否使用流式响应
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print(response.json()["response"])
else:
    print("请求失败，状态码:", response.status_code)