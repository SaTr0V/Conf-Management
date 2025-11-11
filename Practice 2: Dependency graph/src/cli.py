import sys
import os

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import parse_arguments, print_config


def main():
    """Парсинг аргументов, валидиция конфигурации и вывод параметров"""
    
    try:
        config = parse_arguments()
        
        print_config(config)
        
        print("Конфигурация успешно загружена. Приложение готово к работе.")
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()