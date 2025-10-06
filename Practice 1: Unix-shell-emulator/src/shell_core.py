import os
import re


class ShellCore:
    """Ядро оболочки - содержит всю логику командной строки"""

    # Конструктор
    def __init__(self, vfs, config):
        self.vfs = vfs              # сохраняет ссылку на vfs для доступа к файловой системе
        self.config = config
        self.commands = {           # список команд
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'exit': self.cmd_exit,
            'conf-dump': self.cmd_conf_dump,
            'echo': self.cmd_echo,
            'tac': self.cmd_tac,
            'find': self.cmd_find,
            'wc': self.cmd_wc
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
        """Команда ls - список файлов и директорий"""

        path = args[0] if args else None

        success, result = self.vfs.list_directory(path)
        if success:
            return result
        else:
            return f"ls: {result}"

    def cmd_cd(self, args):
        """Команда cd - смена директории"""

        target = args[0] if args else "/"

        success, result = self.vfs.change_directory(target)
        if success:
            return result
        else:
            return f"cd: {result}"

    def cmd_exit(self, args):
        """Команда exit - завершает программу"""

        return "EXIT"

    def cmd_conf_dump(self, args):
        """Команда conf-dump - выводит текущую конфигурацию эмулятора"""

        config_dict = self.config.get_config_dict()

        result = "КОНФИГУРАЦИЯ ЭМУЛЯТОРА\n"
        for key, value in config_dict.items():
            result += f"{key}: {value}\n"
        result += "-----------------------------"

        return result

    def cmd_echo(self, args):
        """Команда echo - вывод текста в консоль"""

        if not args:
            return ""

        text = " ".join(args)

        # Раскрываем переменные окружения
        expanded_text = self._expand_env_vars(text)
        return expanded_text

    def cmd_tac(self, args):
        """Команда tac - вывод содержимого файла в обратном порядке строк"""

        if not args:
            return "tac: отсутствует аргумент - имя файла"

        filename = args[0]
        file_node = self.vfs.get_file_content(filename)

        if file_node is None:
            return f"tac: {filename}: файл не найден"

        if file_node.type != "file":
            return f"tac: {filename}: не является файлом"

        content = file_node.content
        if not content:
            return ""  # пустой файл

        # Разбиваем на строки и выводим в обратном порядке
        lines = content.split('\n')
        reversed_lines = reversed(lines)
        return '\n'.join(reversed_lines)

    def cmd_find(self, args):
        """Команда find - поиск файлов и директорий по имени"""

        if not args:
            return "find: отсутствуют аргументы. Использование: find <путь> -name <шаблон>"

        # Базовая реализация: find <путь> -name <шаблон>
        if len(args) < 3 or args[1] != "-name":
            return "find: поддерживается только форма: find <путь> -name <шаблон>"

        search_path = args[0]
        pattern = args[2]

        results = self.vfs.find_files(search_path, pattern)
        if results is None:
            return f"find: {search_path}: директория не найдена"

        if not results:
            return ""  # ничего не найдено

        return '\n'.join(results)

    def cmd_wc(self, args):
        """Команда wc - подсчет строк, слов и символов в файле"""

        if not args:
            return "wc: отсутствует аргумент - имя файла"

        filename = args[0]
        file_node = self.vfs.get_file_content(filename)

        if file_node is None:
            return f"wc: {filename}: файл не найден"

        if file_node.type != "file":
            return f"wc: {filename}: не является файлом"

        content = file_node.content
        if content is None:
            content = ""  # пустой файл

        # Подсчет статистики
        lines = content.split('\n')
        line_count = len(lines) if content else 0
        word_count = len(content.split()) if content else 0
        char_count = len(content) if content else 0

        return f"  {line_count}  {word_count}  {char_count} {filename}"