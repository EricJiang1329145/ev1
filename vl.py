if input("1:").lower() in ["\\bye", "exit", "quit"]:
    save_choice = input("是否保存当前对话？(y/n): ").lower()
    if save_choice == 'y':
        print(f"对话已保存")
    print("对话结束")
