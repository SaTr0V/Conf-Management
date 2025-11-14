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
        """Получение зависимостей пакета
           Поддерживается поиск как по 'A' так и по 'A:A' (совместимость с форматом group:artifact)"""
        
        # Если ключ есть прямо — используем
        if package_name in self.dependencies:
            key = package_name
        else:
            # Попробуем разбить group:artifact и искать по простой форме (A)
            if ':' in package_name:
                left = package_name.split(':', 1)[0]
                if left in self.dependencies:
                    key = left
                else:
                    # Также попробуем artifact (в случае form A:A)
                    right = package_name.split(':', 1)[1]
                    key = right if right in self.dependencies else None
            else:
                key = None

        if not key or key not in self.dependencies:
            raise ValueError(f"Пакет {package_name} не найден в тестовом репозитории")
        
        # Преобразуем формат для совместимости с MavenClient (group, artifact, version)
        result = []
        for dep_name, dep_version in self.dependencies[key]:
            # В тестовом репозитории имена пакетов используются как простые токены — используем их как group и artifact
            result.append((dep_name, dep_name, dep_version))
        
        return result
