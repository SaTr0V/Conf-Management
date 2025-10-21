#!/usr/bin/env python3
"""
Инструмент визуализации графа зависимостей для Maven пакетов.
"""

import argparse
import sys
import os
from pathlib import Path


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
        
        # Вывод конфигурации (для этапа 1)
        visualizer.display_config()
        
        print("\n✓ Все параметры успешно валидированы")
        
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()


