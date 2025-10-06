import tkinter as tk
from shell_core import ShellCore
from vfs import VFS
from gui import ShellGUI
from config import Config
from script_runner import ScriptRunner


def main():
    # Парсим аргументы командной строки
    config = Config()
    config.parse_arguments()

    # Инициализируем VFS
    vfs = VFS()

    # Загружаем VFS из XML если указан путь
    if config.vfs_path:
        try:
            vfs.load_from_xml(config.vfs_path)
            print(f"VFS загружена из: {config.vfs_path}")
        except Exception as e:
            print(f"Ошибка загрузки VFS: {str(e)}")
            # Продолжаем с VFS по умолчанию

    # Инициализируем компоненты
    root = tk.Tk()
    shell_core = ShellCore(vfs, config)
    gui = ShellGUI(root, shell_core, vfs)

    # Если указан скрипт - выполняем его
    if config.script_path:
        script_runner = ScriptRunner(shell_core, gui)
        root.after(100, lambda: script_runner.run_script(config.script_path))

    root.mainloop()


if __name__ == "__main__":
    main()