import sys
import os

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import parse_arguments, print_config
from src.maven_repository import MavenRepository
from src.test_repository import TestRepository


def get_dependencies(config):
    """Получение зависимостей пакета в соответствии с режимом работы приложения"""
    
    if config.is_test_mode():
        # Работа с тестовым репозиторием
        test_repo = TestRepository(config.repo_url)
        dependencies = test_repo.get_dependencies(config.package_name, config.version)
    else:
        # Работа с реальным Maven-репозиторием
        maven_repo = MavenRepository(config.repo_url)
        dependencies = maven_repo.get_dependencies(config.package_name, config.version)
    
    return dependencies


def print_dependencies(package_name: str, dependencies: list) -> None:
    """Вывод прямых зависимостей пакета"""
    
    print(f"\nПрямые зависимости пакета {package_name}:")
    print("-" * 50)
    
    if not dependencies:
        print("Зависимости не найдены")
        return
    
    for i, (group_id, artifact_id, version) in enumerate(dependencies, 1):
        full_name = f"{group_id}:{artifact_id}"
        print(f"{i:2d}. {full_name:<40} {version}")
    
    print("-" * 50)
    print(f"Всего зависимостей: {len(dependencies)}")

def main():
    """Парсинг аргументов, валидиция конфигурации и вывод параметров"""
    
    try:
        config = parse_arguments()
        
        print_config(config)
        
        # Получение зависимостей
        print(f"\nПолучение зависимостей для пакета {config.package_name}...")
        dependencies = get_dependencies(config)
        
        # Вывод прямых зависимостей
        print_dependencies(config.package_name, dependencies)
        
        print("\nЗависимости успешно получены.")
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()