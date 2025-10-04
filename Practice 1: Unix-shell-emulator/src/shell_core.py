import os
import re


class ShellCore:
    """Ядро оболочки - содержит всю логику командной строки"""

    # Конструктор
    def __init__(self, vfs):
        self.vfs = vfs              # сохраняет ссылку на vfs для доступа к файловой системе
        self.commands = {           # список команд
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'exit': self.cmd_exit
        }

    def _expand_env_vars(self, text):
        """Раскрытие переменных окружения в формате $VAR или ${VAR}"""

        def replace_var(match):
            var_name = match.group(1) or match.group(2)  # группа 1 - $HOME, группа 2 - ${HOME}; берем что-то одно
            return os.getenv(var_name, '')

        # Регуляное выражение для обработки $VAR или ${VAR}
        pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*)|\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
        return re.sub(
            pattern,        # шаблон, вхождение которого нужно заменить
            replace_var,    # функция, производящая замену
            text            # строка, для которой производится замена
        )

    def parse_command(self, input_line):
        """Парсер команд"""

        if not input_line.strip():
            return "", []

        # Раскрываем переменные окружения
        expanded_input = self._expand_env_vars(input_line)

        # Разбиваем на команду и аргументы
        parts = expanded_input.split()
        command = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        return command, args

    def execute(self, command, args):
        """Выполнение команды"""

        if command in self.commands:
            try:
                return self.commands[command](args)
            except Exception as e:
                return f"Ошибка выполнения команды {command}: {str(e)}"
        elif command:
            return f"Команда не найдена: {command}"
        else:
            return ""


    """Область разработки команд"""

    def cmd_ls(self, args):
        """Заглушка для команды ls"""

        return f"ls: аргументы {args}. Команда в разработке"

    def cmd_cd(self, args):
        """Заглушка для команды cd"""

        target = args[0] if args else "~"
        return f"cd: переход в {target}. Команда в разработке"

    def cmd_exit(self, args):
        """Команда exit - завершает программу"""

        return "EXIT"