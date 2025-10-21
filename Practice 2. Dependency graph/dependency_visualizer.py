#!/usr/bin/env python3
"""
Инструмент визуализации графа зависимостей для Maven пакетов.
"""

import argparse
import sys
import os
from pathlib import Path
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET


class TestRepository:
    """Класс для работы с тестовым репозиторием."""
    
    def __init__(self, repo_file):
        """
        Инициализация тестового репозитория.
        
        Args:
            repo_file: Путь к файлу репозитория
        """
        self.repo_file = repo_file
        self.dependencies = {}
        self._load_repository()
    
    def _load_repository(self):
        """Загрузить репозиторий из файла."""
        try:
            with open(self.repo_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Пропускаем пустые строки и комментарии
                    if not line or line.startswith('#'):
                        continue
                    
                    # Формат: PACKAGE:VERSION -> DEP1, DEP2, ...
                    if '->' in line:
                        parts = line.split('->')
                        package_info = parts[0].strip()
                        deps_str = parts[1].strip() if len(parts) > 1 else ""
                        
                        # Парсим имя пакета и версию
                        if ':' in package_info:
                            package, version = package_info.split(':', 1)
                            package = package.strip()
                            version = version.strip()
                        else:
                            package = package_info
                            version = "1.0"
                        
                        # Парсим зависимости
                        deps = []
                        if deps_str:
                            for dep in deps_str.split(','):
                                dep = dep.strip()
                                if dep:
                                    deps.append(dep)
                        
                        # Сохраняем в словарь
                        key = f"{package}:{version}"
                        self.dependencies[key] = deps
                        
        except Exception as e:
            raise ValueError(f"Ошибка при чтении тестового репозитория: {e}")
    
    def get_dependencies(self, package, version):
        """
        Получить зависимости для пакета.
        
        Args:
            package: Имя пакета
            version: Версия пакета
            
        Returns:
            Список зависимостей
        """
        key = f"{package}:{version}"
        return self.dependencies.get(key, [])


class MavenRepository:
    """Класс для работы с Maven репозиторием."""
    
    def __init__(self, repository_url):
        """
        Инициализация Maven репозитория.
        
        Args:
            repository_url: URL репозитория
        """
        self.repository_url = repository_url.rstrip('/')
    
    def _build_pom_url(self, group_id, artifact_id, version):
        """
        Построить URL к POM файлу.
        
        Args:
            group_id: Group ID пакета
            artifact_id: Artifact ID пакета
            version: Версия пакета
            
        Returns:
            URL к POM файлу
        """
        group_path = group_id.replace('.', '/')
        pom_url = f"{self.repository_url}/{group_path}/{artifact_id}/{version}/{artifact_id}-{version}.pom"
        return pom_url
    
    def _download_pom(self, url):
        """
        Скачать POM файл.
        
        Args:
            url: URL POM файла
            
        Returns:
            Содержимое POM файла
        """
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            raise ValueError(f"Не удалось загрузить POM файл (HTTP {e.code}): {url}")
        except urllib.error.URLError as e:
            raise ValueError(f"Ошибка соединения: {e.reason}")
        except Exception as e:
            raise ValueError(f"Ошибка при загрузке POM файла: {e}")
    
    def _parse_pom(self, pom_content):
        """
        Парсинг POM файла для извлечения зависимостей.
        
        Args:
            pom_content: Содержимое POM файла
            
        Returns:
            Список зависимостей в формате (groupId, artifactId, version)
        """
        try:
            root = ET.fromstring(pom_content)
            
            # Maven использует namespace
            namespace = {'m': 'http://maven.apache.org/POM/4.0.0'}
            
            # Ищем секцию dependencies
            dependencies = []
            deps_element = root.find('.//m:dependencies', namespace)
            
            if deps_element is not None:
                for dep in deps_element.findall('m:dependency', namespace):
                    group_id = dep.find('m:groupId', namespace)
                    artifact_id = dep.find('m:artifactId', namespace)
                    version = dep.find('m:version', namespace)
                    scope = dep.find('m:scope', namespace)
                    optional = dep.find('m:optional', namespace)
                    
                    # Пропускаем test и optional зависимости
                    if scope is not None and scope.text == 'test':
                        continue
                    if optional is not None and optional.text == 'true':
                        continue
                    
                    if group_id is not None and artifact_id is not None:
                        ver = version.text if version is not None else 'LATEST'
                        dependencies.append((group_id.text, artifact_id.text, ver))
            
            return dependencies
            
        except ET.ParseError as e:
            raise ValueError(f"Ошибка при парсинге POM файла: {e}")
    
    def get_dependencies(self, package, version):
        """
        Получить зависимости для Maven пакета.
        
        Args:
            package: Имя пакета в формате groupId:artifactId
            version: Версия пакета
            
        Returns:
            Список зависимостей в формате groupId:artifactId
        """
        # Парсим имя пакета
        if ':' not in package:
            raise ValueError(f"Неверный формат Maven пакета: {package}. Ожидается groupId:artifactId")
        
        group_id, artifact_id = package.split(':', 1)
        
        # Строим URL и скачиваем POM
        pom_url = self._build_pom_url(group_id, artifact_id, version)
        pom_content = self._download_pom(pom_url)
        
        # Парсим зависимости
        raw_deps = self._parse_pom(pom_content)
        
        # Преобразуем в формат groupId:artifactId
        dependencies = [f"{g}:{a}" for g, a, v in raw_deps]
        
        return dependencies


class DependencyVisualizer:
    """Основной класс для визуализации графа зависимостей."""
    
    def __init__(self, args):
        """
        Инициализация визуализатора.
        
        Args:
            args: Аргументы командной строки
        """
        self.package_name = args.package
        self.repository_url = args.repository
        self.test_mode = args.test_mode
        self.version = args.version
        self.output_file = args.output
        self.max_depth = args.max_depth
        
        # Инициализация репозитория
        if self.test_mode:
            self.repository = TestRepository(self.repository_url)
        else:
            self.repository = MavenRepository(self.repository_url)
        
    def display_config(self):
        """Вывести конфигурацию в формате ключ-значение."""
        print("=" * 60)
        print("Конфигурация визуализатора графа зависимостей")
        print("=" * 60)
        print(f"Имя пакета: {self.package_name}")
        print(f"Репозиторий/Путь: {self.repository_url}")
        print(f"Режим тестирования: {self.test_mode}")
        print(f"Версия пакета: {self.version}")
        print(f"Файл вывода: {self.output_file}")
        print(f"Максимальная глубина: {self.max_depth}")
        print("=" * 60)
    
    def get_direct_dependencies(self):
        """
        Получить прямые зависимости пакета.
        
        Returns:
            Список прямых зависимостей
        """
        try:
            dependencies = self.repository.get_dependencies(self.package_name, self.version)
            return dependencies
        except Exception as e:
            raise ValueError(f"Ошибка при получении зависимостей: {e}")
    
    def display_direct_dependencies(self):
        """Вывести прямые зависимости на экран (для этапа 2)."""
        print("\n" + "=" * 60)
        print(f"Прямые зависимости для {self.package_name}:{self.version}")
        print("=" * 60)
        
        try:
            dependencies = self.get_direct_dependencies()
            
            if dependencies:
                for i, dep in enumerate(dependencies, 1):
                    print(f"{i}. {dep}")
                print(f"\nВсего зависимостей: {len(dependencies)}")
            else:
                print("Зависимости отсутствуют")
                
        except Exception as e:
            print(f"Ошибка: {e}", file=sys.stderr)
            raise
        

def validate_package_name(package_name):
    """
    Проверить корректность имени пакета.
    
    Args:
        package_name: Имя пакета для проверки
        
    Raises:
        ValueError: Если имя пакета некорректно
    """
    if not package_name or not package_name.strip():
        raise ValueError("Имя пакета не может быть пустым")
    
    if len(package_name.strip()) < 1:
        raise ValueError("Имя пакета слишком короткое")
    
    return package_name.strip()


def validate_repository(repository_url, test_mode):
    """
    Проверить корректность URL репозитория или пути к файлу.
    
    Args:
        repository_url: URL или путь к репозиторию
        test_mode: Флаг режима тестирования
        
    Raises:
        ValueError: Если URL или путь некорректны
    """
    if not repository_url or not repository_url.strip():
        raise ValueError("URL репозитория или путь к файлу не может быть пустым")
    
    if test_mode:
        # В режиме тестирования проверяем существование файла
        path = Path(repository_url)
        if not path.exists():
            raise ValueError(f"Файл тестового репозитория не найден: {repository_url}")
        if not path.is_file():
            raise ValueError(f"Путь должен указывать на файл: {repository_url}")
    else:
        # Для реального репозитория проверяем формат URL
        if not (repository_url.startswith('http://') or repository_url.startswith('https://')):
            raise ValueError("URL репозитория должен начинаться с http:// или https://")
    
    return repository_url.strip()


def validate_version(version):
    """
    Проверить корректность версии пакета.
    
    Args:
        version: Версия пакета
        
    Raises:
        ValueError: Если версия некорректна
    """
    if not version or not version.strip():
        raise ValueError("Версия пакета не может быть пустой")
    
    # Базовая проверка формата версии (допускаем разные форматы)
    if len(version.strip()) < 1:
        raise ValueError("Версия пакета некорректна")
    
    return version.strip()


def validate_output_file(output_file):
    """
    Проверить корректность имени выходного файла.
    
    Args:
        output_file: Имя выходного файла
        
    Raises:
        ValueError: Если имя файла некорректно
    """
    if not output_file or not output_file.strip():
        raise ValueError("Имя выходного файла не может быть пустым")
    
    # Проверяем расширение файла
    if not output_file.endswith('.svg'):
        raise ValueError("Выходной файл должен иметь расширение .svg")
    
    # Проверяем, что путь к директории существует (если указан)
    output_path = Path(output_file)
    if output_path.parent != Path('.') and not output_path.parent.exists():
        raise ValueError(f"Директория для выходного файла не существует: {output_path.parent}")
    
    return output_file.strip()


def validate_max_depth(max_depth):
    """
    Проверить корректность максимальной глубины.
    
    Args:
        max_depth: Максимальная глубина анализа
        
    Raises:
        ValueError: Если глубина некорректна
    """
    if max_depth < 1:
        raise ValueError("Максимальная глубина должна быть не меньше 1")
    
    if max_depth > 100:
        raise ValueError("Максимальная глубина не может быть больше 100 (слишком большое значение)")
    
    return max_depth


def parse_arguments():
    """
    Парсинг аргументов командной строки.
    
    Returns:
        Распарсенные аргументы
    """
    parser = argparse.ArgumentParser(
        description='Визуализация графа зависимостей для Maven пакетов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Для реального репозитория Maven
  python dependency_visualizer.py -p org.springframework:spring-core -v 5.3.0 -r https://repo.maven.apache.org/maven2
  
  # Для тестового репозитория
  python dependency_visualizer.py -p A -v 1.0 -r test_repo.txt --test-mode
        """
    )
    
    parser.add_argument(
        '-p', '--package',
        required=True,
        help='Имя анализируемого пакета (формат: groupId:artifactId для Maven, или буква для тестового режима)'
    )
    
    parser.add_argument(
        '-r', '--repository',
        required=True,
        help='URL-адрес Maven репозитория или путь к файлу тестового репозитория'
    )
    
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Режим работы с тестовым репозиторием'
    )
    
    parser.add_argument(
        '-v', '--version',
        required=True,
        help='Версия пакета'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='dependency_graph.svg',
        help='Имя файла для сохранения графа (по умолчанию: dependency_graph.svg)'
    )
    
    parser.add_argument(
        '-d', '--max-depth',
        type=int,
        default=3,
        help='Максимальная глубина анализа зависимостей (по умолчанию: 3)'
    )
    
    return parser.parse_args()


def main():
    """Главная функция приложения."""
    try:
        # Парсинг аргументов командной строки
        args = parse_arguments()
        
        # Валидация всех параметров
        try:
            args.package = validate_package_name(args.package)
            args.repository = validate_repository(args.repository, args.test_mode)
            args.version = validate_version(args.version)
            args.output = validate_output_file(args.output)
            args.max_depth = validate_max_depth(args.max_depth)
        except ValueError as e:
            print(f"Ошибка валидации параметров: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Создание экземпляра визуализатора
        visualizer = DependencyVisualizer(args)
        
        # Вывод конфигурации
        visualizer.display_config()
        
        # Этап 2: Вывод прямых зависимостей
        visualizer.display_direct_dependencies()
        
        print("\n✓ Анализ завершен успешно")
        
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
