import os
from typing import List, Tuple, Optional


class TestRepository:
    """Класс для работы с тестовым репозиторием из txt-файла"""
    
    def __init__(self, file_path: str):
        
        self.file_path = file_path
        self.dependencies = self._load_dependencies()
    
    def _load_dependencies(self) -> dict:
        """Загрузка зависимостей из файла"""
        
        if not os.path.exists(self.file_path):
            raise ValueError(f"Файл тестового репозитория не найден: {self.file_path}")
        
        dependencies = {}
        
        with open(self.file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                
                # Пропускаем пустые строки и комментарии
                if not line or line.startswith('#'):
                    continue
                
                # Формат: PACKAGE -> DEP1, DEP2, DEP3
                if '->' in line:
                    package_part, deps_part = line.split('->', 1)
                    package = package_part.strip()
                    
                    if package not in dependencies:
                        dependencies[package] = []
                    
                    # Обрабатываем зависимости
                    for dep in deps_part.split(','):
                        dep = dep.strip()
                        if dep:
                            # Для тестового репозитория используем фиктивную версию
                            dependencies[package].append((dep, "1.0.0"))
                else:
                    print(f"Предупреждение: некорректный формат строки {line_num}: {line}")
        
        return dependencies
    
    def get_dependencies(self, package_name: str, version: Optional[str] = None) -> List[Tuple[str, str, str]]:
        """Получение зависимостей пакета"""
        
        if package_name not in self.dependencies:
            raise ValueError(f"Пакет {package_name} не найден в тестовом репозитории")
        
        # Преобразуем формат для совместимости с MavenClient
        result = []
        for dep_name, dep_version in self.dependencies[package_name]:
            # В тестовом репозитории имена пакетов используются как group_id:artifact_id
            result.append((dep_name, dep_name, dep_version))
        
        return result
