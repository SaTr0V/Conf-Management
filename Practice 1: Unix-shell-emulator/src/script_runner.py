import os


class ScriptRunner:
    """Класс для выполнения скриптов"""

    def __init__(self, shell_core, gui):
        self.shell = shell_core
        self.gui = gui

    def run_script(self, script_path):
        """Выполнение скрипта"""

        if not script_path or not os.path.exists(script_path):
            error_msg = f"Ошибка: файл скрипта не найден - {script_path}\n"
            self.gui.print_output(error_msg)
            return

        try:
            with open(script_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Выводим информацию о запуске скрипта
            self.gui.print_output(f"Выполнение скрипта: {script_path}\n")
            self.gui.print_output("------------------------------\n")

            # Выполняем каждую строку скрипта
            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Пропускаем пустые строки и комментарии
                if not line or line.startswith('#'):
                    continue

                # Выводим команду (имитируем ввод пользователя)
                current_path = self.shell.vfs.get_current_path()
                vfs_name = self.shell.vfs.name
                self.gui.print_output(f"{vfs_name}:{current_path}$ {line}\n")

                # Выполняем команду
                command, args = self.shell.parse_command(line)
                result = self.shell.execute(command, args)

                # Выводим результат
                if result and result != "EXIT":
                    self.gui.print_output(f"{result}\n")

                # Если команда exit - прерываем выполнение скрипта
                if result == "EXIT":
                    self.gui.print_output("Завершение работы по команде exit\n")
                    break

            self.gui.print_output(f"Скрипт завершен\n\n")

        except Exception as e:
            error_msg = f"Ошибка выполнения скрипта: {str(e)}\n"
            self.gui.print_output(error_msg)