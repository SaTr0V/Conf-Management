import xml.etree.ElementTree as ET
import base64
import os


class VFSNode:
    """Узел виртуальной файловой системы (файл или директория)"""

    def __init__(self, name, node_type="dir", content=""):
        self.name = name
        self.type = node_type                               # "dir" или "file"
        self.content = content
        self.children = {} if node_type == "dir" else None  # дочерние узлы могут быть только у директорий
        self.parent = None


class VFS:
    """Виртуальная файловая система"""

    def __init__(self):
        self.root = VFSNode("", "dir")
        self.current_node = self.root
        self.name = "VFS"
        self._build_default_structure()  # структура vfs по умолчанию

    def _build_default_structure(self):
        """Создает минимальную структуру VFS по умолчанию"""

        # Создаем базовую структуру Unix-подобной системы
        home_dir = self._add_child(self.root, "home", "dir")
        self._add_child(home_dir, "user", "dir")
        self._add_child(self.root, "etc", "dir")
        self._add_child(self.root, "var", "dir")
        self._add_child(self.root, "tmp", "dir")

        # Устанавливаем текущую директорию в /home/user
        self.current_node = home_dir.children["user"]

    def _add_child(self, parent, name, node_type="dir", content=""):
        """Добавляет дочерний узел"""

        node = VFSNode(name, node_type, content)
        node.parent = parent
        if parent.children is not None:
            parent.children[name] = node
        return node

    def _resolve_path(self, path):
        """Разрешает путь к узлу VFS"""

        if path.startswith("/"):
            # Абсолютный путь
            current = self.root
            path_parts = path.split("/")[1:]  # убираем пустой первый элемент
        else:
            # Относительный путь
            current = self.current_node
            path_parts = path.split("/")

        for part in path_parts:
            if not part or part == ".":
                continue
            elif part == "..":
                if current.parent:
                    current = current.parent
            else:
                if (current.children and
                        part in current.children and
                        current.children[part].type == "dir"):
                    current = current.children[part]
                else:
                    # Проверяем, может это файл в текущей директории
                    if (current.children and part in current.children):
                        return current.children[part]
                    return None

        return current

    def load_from_xml(self, xml_path):
        """Загружает VFS из XML файла"""

        if not os.path.exists(xml_path):
            raise FileNotFoundError(f"XML файл не найден: {xml_path}")

        try:
            tree = ET.parse(xml_path)
            root_element = tree.getroot()

            # Очищаем текущую структуру
            self.root = VFSNode("", "dir")
            self.current_node = self.root

            # Рекурсивно строим VFS из XML
            self._build_from_xml_element(self.root, root_element)

            # Возвращаемся в корневую директорию
            self.current_node = self.root

        except ET.ParseError as e:
            raise ValueError(f"Ошибка парсинга XML: {str(e)}")

    def _build_from_xml_element(self, vfs_node, xml_element):
        """Рекурсивно строит VFS из XML элемента"""
        for child in xml_element:
            if child.tag == "directory":
                name = child.get("name", "unnamed")
                new_dir = self._add_child(vfs_node, name, "dir")
                self._build_from_xml_element(new_dir, child)

            elif child.tag == "file":
                name = child.get("name", "unnamed")
                content = child.text or ""
                if child.get("encoding") == "base64":
                    try:
                        content = base64.b64decode(content).decode('utf-8')
                    except:
                        content = f"Ошибка декодирования base64 для файла {name}"

                self._add_child(vfs_node, name, "file", content)

    def get_current_path(self):
        """Возвращает текущий путь в VFS"""

        path_parts = []
        node = self.current_node

        # Поднимаемся вверх по иерархии до корня
        while node and node.parent:
            path_parts.insert(0, node.name)
            node = node.parent

        return "/" + "/".join(path_parts) if path_parts else "/"

    def change_directory(self, path):
        """Изменяет текущую директорию. Алгоритм команды cd"""

        if not path:
            return False, "Путь не указан"

        target_node = self._resolve_path(path)
        if not target_node:
            return False, f"Директория не найдена: {path}"

        if target_node.type != "dir":
            return False, f"Не директория: {path}"

        self.current_node = target_node
        return True, f"Переход в {self.get_current_path()}"

    def list_directory(self, path=None):
        """Список содержимого директории. Алгоритм команды ls"""

        if path:
            target_node = self._resolve_path(path)
            if not target_node:
                return False, f"Директория не найдена: {path}"
        else:
            target_node = self.current_node

        if target_node.type != "dir":
            return False, f"Не директория: {path if path else self.get_current_path()}"

        if not target_node.children:
            return True, "Директория пуста"

        items = list(target_node.children.keys())
        return True, "\n".join(sorted(items))

    def get_file_content(self, path):
        """Получает содержимое файла по относительному или абсолютному пути"""

        if path.startswith("/"):  # абсолютный путь
            target_node = self._resolve_path(path)
        else:
            # Относительный путь - ищем в текущей директории
            if self.current_node.children and path in self.current_node.children:
                target_node = self.current_node.children[path]
            else:
                target_node = None

        return target_node

    def find_files(self, search_path, pattern):
        """Поиск файлов по шаблону"""

        start_node = self._resolve_path(search_path)
        if not start_node:
            return None

        if start_node.type != "dir":
            return None

        results = []
        self._find_recursive(start_node, pattern, search_path, results)
        return results

    def _find_recursive(self, node, pattern, current_path, results):
        """Рекурсивный поиск файлов"""

        if not node.children:
            return

        for name, child in node.children.items():
            child_path = f"{current_path}/{name}" if current_path != "/" else f"/{name}"

            # Проверяем соответствие шаблону
            if self._matches_pattern(name, pattern):
                results.append(child_path)

            # Рекурсивно ищем в поддиректориях
            if child.type == "dir":
                self._find_recursive(child, pattern, child_path, results)

    def _matches_pattern(self, filename, pattern):
        """Проверяет соответствие имени файла шаблону"""

        # Простая реализация подстановки * в начале/конце
        if pattern.startswith('*') and pattern.endswith('*'):
            # *text* - содержит текст
            search_text = pattern[1:-1]
            return search_text in filename

        elif pattern.startswith('*'):
            # *text - заканчивается на текст
            search_text = pattern[1:]
            return filename.endswith(search_text)

        elif pattern.endswith('*'):
            # text* - начинается с текста
            search_text = pattern[:-1]
            return filename.startswith(search_text)

        else:
            # полное совпадение
            return filename == pattern

    def create_directory(self, path):
        """Создает директорию"""

        if not path:
            return False, "Неверное имя директории"

        # Разделяем путь на родительскую директорию и имя новой директории
        if "/" in path:
            # Путь содержит поддиректории
            if path.endswith("/"):
                return False, "Неверное имя директории"

            parts = path.split("/")
            dirname = parts[-1]
            parent_path = "/".join(parts[:-1]) or "/"
        else:
            # Просто имя в текущей директории
            dirname = path
            parent_path = "."

        # Ищем родительскую директорию
        parent_dir = self._resolve_path(parent_path)
        if not parent_dir or parent_dir.type != "dir":
            return False, "Родительская директория не найдена"

        # Проверяем, существует ли уже узел с таким именем
        if parent_dir.children and dirname in parent_dir.children:
            existing_node = parent_dir.children[dirname]
            return (True, "Директория уже существует") if existing_node.type == "dir" else (
                False, f"{dirname}: файл с таким именем уже существует")

        # Создаем директорию
        self._add_child(parent_dir, dirname, "dir")
        return True, "Директория создана"

    def create_file(self, path):
        """Создает файл"""

        if not path:
            return False, "Неверное имя файла"

        # Разделяем путь на родительскую директорию и имя нового файла
        if "/" in path:
            # Путь содержит поддиректории
            if path.endswith("/"):
                return False, "Неверное имя файла"

            parts = path.split("/")
            filename = parts[-1]
            parent_path = "/".join(parts[:-1]) or "/"
        else:
            # Просто имя в текущей директории
            filename = path
            parent_path = "."

        # Ищем родительскую директорию
        parent_dir = self._resolve_path(parent_path)
        if not parent_dir or parent_dir.type != "dir":
            return False, "Родительская директория не найдена"

        # Проверяем, существует ли уже узел с таким именем
        if parent_dir.children and filename in parent_dir.children:
            existing_node = parent_dir.children[filename]
            return (True, "Файл уже существует") if existing_node.type == "file" else (
                False, f"{filename}: директория с таким именем уже существует")

        # Создаем файл
        self._add_child(parent_dir, filename, "file", "")
        return True, "Файл создан"