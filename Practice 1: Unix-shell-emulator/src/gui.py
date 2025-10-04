import tkinter as tk
from tkinter import scrolledtext, Entry, Frame


class ShellGUI:
    """Графический интерфейс"""

    # Конструктор
    def __init__(self, root, shell_core, vfs):
        self.root = root            # окно приложения
        self.shell = shell_core     # ядро для выполнения команд
        self.vfs = vfs              # файловая система для отображения пути

        self.setup_gui()            # настройка графического интерфейса
        self.print_welcome()        # приветственное сообщение

    def setup_gui(self):
        """Настройка графического интерфейса"""

        self.root.title(self.vfs.name)  # название окна
        self.root.geometry("800x600")   # размер окна

        # Основной фрейм - область для группировки элементов
        main_frame = Frame(self.root)

        # pack() - размещает элемент в окне
        main_frame.pack(
            fill=tk.BOTH,               # fill=tk.BOTH - растягивает по ширине и высоте
            expand=True,                # expnd=True - занимает все доступное пространство
            padx=10,                    # отступ по горизонтали 10 пикселей
            pady=10                     # отступ по вертикали 10 пикселей
        )

        # Область вывода - текстовое поле с прокруткой
        self.output_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,               # перенос по словам
            width=80,                   # ширина
            height=25,                  # высота
            font=("Courier New", 14)    # шрифт
        )
        self.output_area.pack(fill=tk.BOTH, expand=True)

        # Блокировка текстового поля, пользователь не сможет редактировать вывод команд
        self.output_area.config(state=tk.DISABLED)

        # Фрейм для ввода команд
        input_frame = Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))

        # Приглашение оболочки командной строки
        self.prompt_label = tk.Label(
            input_frame,
            text=f"{self.vfs.name}:{self.vfs.get_current_path()}$ ",
            font=("Courier New", 14, "bold")
        )

        # Расположение приглашения
        self.prompt_label.pack(side=tk.LEFT)

        # Поле ввода команды
        self.command_entry = Entry(
            input_frame,
            font=("Courier New", 14),
            bg="black",                 # цвет фона
            fg="white",                 # цвет текста
            insertbackground="white"    # цвет мигающего курсора
        )

        # Расположение поля ввода
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Реагирование на клавишу Enter
        self.command_entry.bind("<Return>", self.execute_command)

        # Фокус на поля ввода, автоматически ставящий на него курсор
        self.command_entry.focus()

    def print_output(self, text):
        """Вывод текста в область вывода"""

        self.output_area.config(state=tk.NORMAL)    # разблокируем текстовое поле
        self.output_area.insert(tk.END, text)       # вставляем текст в конец
        self.output_area.see(tk.END)                # прокручиваем до конца, чтобы видеть последний вывод
        self.output_area.config(state=tk.DISABLED)  # блокируем текстовое поле

    def print_welcome(self):
        """Приветственная команда. Вывод основной информации об эмуляторе"""

        welcome_msg = f"""
Добро пожаловать в эмулятор командной строки {self.vfs.name}!
Доступные команды: ls, cd, exit
Для выхода введите 'exit'

"""
        self.print_output(welcome_msg)

    def update_prompt(self):
        """
        Обновление приглашения оболочки командной строки
        Метод будет вызван после выполнения каждой команды, так как директория может измениться
        """

        self.prompt_label.config(
            text=f"{self.vfs.name}:{self.vfs.get_current_path()}$ "
        )

    def execute_command(self, event=None):  # параметр event=None для обработки нажатия Enter
        """Выполнение введенной команды"""

        # Получаем текст из поля ввода
        command_text = self.command_entry.get().strip()

        # Очищаем поле ввода
        self.command_entry.delete(0, tk.END)

        # Выводим команду пользователя
        self.print_output(f"{self.vfs.name}:{self.vfs.get_current_path()}$ {command_text}\n")

        # Парсим и выполняем команду
        command, args = self.shell.parse_command(command_text)
        result = self.shell.execute(command, args)

        # Обрабатываем результат
        if result == "EXIT":
            self.root.quit()
        elif result:
            self.print_output(f"{result}\n")

        self.update_prompt()