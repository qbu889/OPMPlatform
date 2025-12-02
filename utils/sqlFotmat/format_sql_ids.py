def format_sql_ids():
    print("请输入需要格式化的ID（每行一个，输入空行结束）：")
    ids = []
    while True:
        line = input().strip()
        if not line:
            break
        ids.append(line)

    if not ids:
        print("未输入任何ID！")
        return

    formatted = [f"'{id_}'" for id_ in ids]
    if len(formatted) == 1:
        result = formatted[0]
    else:
        result = ',\n'.join(formatted)

    print("\n格式化结果：")
    print(result)
    # 尝试复制到剪贴板（需pyperclip库，可执行 pip install pyperclip）
    try:
        import pyperclip
        pyperclip.copy(result)
        print("\n内容已复制到剪贴板！")
    except ImportError:
        print("\n提示：安装pyperclip库（pip install pyperclip）可自动复制到剪贴板")


if __name__ == "__main__":
    format_sql_ids()