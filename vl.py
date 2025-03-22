import json
import os

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
