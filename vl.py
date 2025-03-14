def add_newline_after_punctuation(text):
    # 定义需要添加换行符的标点符号
    punctuation = '，。！？；：、……）'
    result = ""
    for char in text:
        result += char
        if char in punctuation:
            result += '\n'
    return result
