"""
Модуль для работы с конфигурацией приложения.
Обрабатывает параметры командной строки и валидацию.
"""

import argparse
import sys
from typing import Optional, Dict, Any


class Config:
    """Класс для хранения и валидации конфигурации приложения."""
    
    def __init__(self):
        self.package_name: Optional[str] = None
        self.repo_url: Optional[str] = None
        self.test_mode: bool = False
        self.version: Optional[str] = None
        self.output_file: str = "dependency_graph.svg"
        self.max_depth: Optional[int] = None
    
    def validate(self) -> None:
        """
        Валидация параметров конфигурации.
        
        Raises:
            ValueError: Если параметры невалидны
        """
        if not self.package_name:
            raise ValueError("Имя пакета обязательно для указания")
        
        if not self.repo_url:
            raise ValueError("URL репозитория или путь к файлу обязателен")
        
        if self.version and not self._is_valid_version(self.version):
            raise ValueError(f"Некорректный формат версии: {self.version}")
        
        if self.max_depth is not None:
            if not isinstance(self.max_depth, int) or self.max_depth < 1:
                raise ValueError("Максимальная глубина должна быть положительным целым числом")
        
        if self.output_file and not self._is_valid_filename(self.output_file):
            raise ValueError(f"Некорректное имя файла: {self.output_file}")
    
    def _is_valid_version(self, version: str) -> bool:
        """Проверяет корректность формата версии."""
        # Базовая проверка - версия не должна быть пустой и содержать только допустимые символы
        if not version or not isinstance(version, str):
            return False
        
        # Допустимы цифры, точки, дефисы для snapshot версий
        import re
        pattern = r'^[a-zA-Z0-9._-]+$'
        return bool(re.match(pattern, version))
    
    def _is_valid_filename(self, filename: str) -> bool:
        """Проверяет корректность имени файла."""
        if not filename or not isinstance(filename, str):
            return False
        
        # Запрещенные символы в именах файлов
        forbidden_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        return not any(char in filename for char in forbidden_chars)
    
    def to_dict(self) -> Dict[str, Any]:
        """Возвращает конфигурацию в виде словаря для вывода."""
        return {
            'package_name': self.package_name,
            'repo_url': self.repo_url,
            'test_mode': self.test_mode,
            'version': self.version if self.version else 'latest',
            'output_file': self.output_file,
            'max_depth': self.max_depth if self.max_depth else 'unlimited'
        }


def parse_arguments() -> Config:
    """
    Парсит аргументы командной строки и возвращает объект Config.
    
    Returns:
        Config: Объект с настройками конфигурации
        
    Raises:
        SystemExit: При ошибке парсинга аргументов
    """
    parser = argparse.ArgumentParser(
        description='Инструмент визуализации графа зависимостей для Maven пакетов',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Обязательные параметры
    parser.add_argument(
        '--package', '-p',
        type=str,
        required=True,
        help='Имя анализируемого пакета (например: com.example:my-package)'
    )
    
    parser.add_argument(
        '--repo', '-r',
        type=str,
        required=True,
        help='URL репозитория Maven или путь к файлу тестового репозитория'
    )
    
    # Опциональные параметры
    parser.add_argument(
        '--test-mode', '-t',
        action='store_true',
        help='Режим работы с тестовым репозиторием'
    )
    
    parser.add_argument(
        '--version', '-v',
        type=str,
        default=None,
        help='Версия пакета (по умолчанию используется latest)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='dependency_graph.svg',
        help='Имя сгенерированного файла с изображением графа (по умолчанию: dependency_graph.svg)'
    )
    
    parser.add_argument(
        '--max-depth', '-d',
        type=int,
        default=None,
        help='Максимальная глубина анализа зависимостей'
    )
    
    try:
        args = parser.parse_args()
        
        config = Config()
        config.package_name = args.package
        config.repo_url = args.repo
        config.test_mode = args.test_mode
        config.version = args.version
        config.output_file = args.output
        config.max_depth = args.max_depth
        
        # Валидация конфигурации
        config.validate()
        
        return config
        
    except argparse.ArgumentError as e:
        print(f"Ошибка в аргументах командной строки: {e}")
        parser.print_help()
        sys.exit(1)
    except ValueError as e:
        print(f"Ошибка валидации конфигурации: {e}")
        sys.exit(1)


def print_config(config: Config) -> None:
    """Выводит конфигурацию в формате ключ-значение."""
    print("Текущая конфигурация:")
    print("-" * 30)
    
    config_dict = config.to_dict()
    for key, value in config_dict.items():
        print(f"{key}: {value}")
    
    print("-" * 30)