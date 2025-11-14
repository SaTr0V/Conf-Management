import sys
import os
from config import parse_arguments, print_config
from maven_repository import MavenRepository
from test_repository import TestRepository
from dependency_graph import DependencyGraph


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


def build_dependency_graph(config):
    """Построение полного графа зависимостей"""
    
    print(f"\nПостроение полного графа зависимостей...")
    print(f"Максимальная глубина: {config.max_depth if config.max_depth else 'неограничена'}")
    
    graph = DependencyGraph(config.repo_url, config.test_mode)
    graph.build_graph(config.package_name, config.version, config.max_depth)
    
    return graph


def main():
    """Парсинг аргументов, валидиция конфигурации и вывод построение графа зависимостей"""
    
    try:
        config = parse_arguments()
        
        print_config(config)
        
        # Получение зависимостей
        print(f"\nПолучение зависимостей для пакета {config.package_name}...")
        dependencies = get_dependencies(config)
        
        # Вывод прямых зависимостей
        print_dependencies(config.package_name, dependencies)
        
        print("\nЗависимости успешно получены.")
        
        # Построение полного графа зависимостей
        graph = build_dependency_graph(config)
        
        # Вывод полного графа
        graph.print_graph(config.package_name, config.version)
        
        print("\nГраф зависимостей успешно построен.")
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()