#!/usr/bin/env python3
"""
Главный модуль CLI приложения для визуализации графа зависимостей.
Этап 1: Минимальный прототип с конфигурацией.
"""

import sys
import os

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import parse_arguments, print_config


def main():
    """
    Главная функция приложения.
    Парсит аргументы, валидирует конфигурацию и выводит параметры.
    """
    try:
        # Парсинг и валидация аргументов командной строки
        config = parse_arguments()
        
        # Вывод конфигурации (требование этапа 1)
        print_config(config)
        
        print("Конфигурация успешно загружена. Приложение готово к работе.")
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()