import tkinter as tk
from shell_core import ShellCore
from vfs import VFS
from gui import ShellGUI


def main():
    root = tk.Tk()

    vfs = VFS()
    shell_core = ShellCore(vfs)

    # Создаем GUI
    app = ShellGUI(root, shell_core, vfs)

    root.mainloop()


if __name__ == "__main__":
    main()