import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Tuple
import re


class MavenRepository:
    """Класс для работы с Maven-репозиторием"""
    
    def __init__(self, repo_url: str):
        
        self.repo_url = repo_url.rstrip('/')
    
    def get_dependencies(self, package_name: str, version: Optional[str] = None) -> List[Tuple[str, str, str]]:
        """Получение прямых зависимостей пакета"""
        
        if ':' not in package_name:
            raise ValueError(f"Некорректный формат имени пакета: {package_name}. Ожидается group:artifact")
        
        group_id, artifact_id = package_name.split(':', 1)
        
        # Если версия не указана, получаем последнюю версию
        if version is None:
            version = self._get_latest_version(group_id, artifact_id)
        
        # Получаем POM-файл и извлекаем зависимости
        return self._parse_pom_dependencies(group_id, artifact_id, version)
    
    def _get_latest_version(self, group_id: str, artifact_id: str) -> str:
        """Получение последней версии пакета из maven-metadata.xml"""
        
        # Получаем URL для maven-metadata.xml
        group_path = group_id.replace('.', '/')
        metadata_url = f"{self.repo_url}/{group_path}/{artifact_id}/maven-metadata.xml"
        
        try:
            with urllib.request.urlopen(metadata_url) as response:
                content = response.read().decode('utf-8')
                root = ET.fromstring(content)  # используем xml.etree
                
                # Ищем версию в теге <latest> или берем последнюю из <versions>
                latest_elem = root.find('.//latest')
                if latest_elem is not None and latest_elem.text:
                    return latest_elem.text
                
                # Если нет latest, берем последнюю версию из списка
                versions = root.findall('.//version')
                if versions:
                    return versions[-1].text
                
                raise ValueError(f"Не найдены версии для пакета {group_id}:{artifact_id}")
                
        except urllib.error.HTTPError as e:
            if e.code == 404:  # такой пакет не найден
                raise ValueError(f"Пакет {group_id}:{artifact_id} не найден в репозитории")
            else:
                raise ConnectionError(f"Ошибка HTTP {e.code} при доступе к {metadata_url}")
        except urllib.error.URLError as e:
            raise ConnectionError(f"Ошибка сети: {e.reason}")
        except ET.ParseError as e:
            raise ValueError(f"Ошибка парсинга metadata: {e}")
    
    def _parse_pom_dependencies(self, group_id: str, artifact_id: str, version: str) -> List[Tuple[str, str, str]]:
        """Парсинг POM-файла и извлечение зависимостей"""
        
        # Строим URL для POM-файла
        group_path = group_id.replace('.', '/')
        pom_url = f"{self.repo_url}/{group_path}/{artifact_id}/{version}/{artifact_id}-{version}.pom"
        
        try:
            with urllib.request.urlopen(pom_url) as response:
                content = response.read().decode('utf-8')
                return self._extract_dependencies_from_pom(content)
                
        except urllib.error.HTTPError as e:
            if e.code == 404:  # такой POM-файл не найден
                raise ValueError(f"POM-файл для {group_id}:{artifact_id}:{version} не найден")
            else:
                raise ConnectionError(f"Ошибка HTTP {e.code} при доступе к {pom_url}")
        except urllib.error.URLError as e:
            raise ConnectionError(f"Ошибка сети: {e.reason}")
    
    def _extract_dependencies_from_pom(self, pom_content: str) -> List[Tuple[str, str, str]]:
        """Извлечение зависимостей из содержимого POM-файла"""
        
        dependencies = []
        
        try:
            root = ET.fromstring(pom_content)
            
            # Определяем namespace POM (namespace обычно выглядит как http://maven.apache.org/POM/4.0.0)
            namespace_match = re.match(r'\{.*\}', root.tag)
            namespace = namespace_match.group(0)[1:-1] if namespace_match else ''
            ns = {'pom': namespace} if namespace else {}
            
            # Ищем секцию dependencies
            dependencies_elem = root.find('.//pom:dependencies', ns) if namespace else root.find('.//dependencies')
            
            if dependencies_elem is not None:
                for dep_elem in dependencies_elem.findall('pom:dependency', ns) if namespace else dependencies_elem.findall('dependency'):
                    group_id_elem = dep_elem.find('pom:groupId', ns) if namespace else dep_elem.find('groupId')
                    artifact_id_elem = dep_elem.find('pom:artifactId', ns) if namespace else dep_elem.find('artifactId')
                    version_elem = dep_elem.find('pom:version', ns) if namespace else dep_elem.find('version')
                    
                    if (group_id_elem is not None and group_id_elem.text and
                        artifact_id_elem is not None and artifact_id_elem.text):
                        
                        group_id = group_id_elem.text.strip()
                        artifact_id = artifact_id_elem.text.strip()
                        version = version_elem.text.strip() if version_elem is not None and version_elem.text else "unknown"
                        
                        dependencies.append((group_id, artifact_id, version))
            
            return dependencies
            
        except ET.ParseError as e:
            # Если XML-парсинг не удался, пытаемся извлечь зависимости с помощью регулярных выражений
            dependencies = []
        
            # Ищем блок dependencies
            deps_match = re.search(r'<dependencies>(.*?)</dependencies>', pom_content, re.DOTALL)
            if not deps_match:
                return dependencies
            
            deps_content = deps_match.group(1)
            
            # Ищем отдельные зависимости dependency
            dep_pattern = r'<dependency>(.*?)</dependency>'
            for dep_match in re.finditer(dep_pattern, deps_content, re.DOTALL):
                dep_content = dep_match.group(1)
                
                group_match = re.search(r'<groupId>(.*?)</groupId>', dep_content)
                artifact_match = re.search(r'<artifactId>(.*?)</artifactId>', dep_content)
                version_match = re.search(r'<version>(.*?)</version>', dep_content)
                
                if group_match and artifact_match:
                    group_id = group_match.group(1).strip()
                    artifact_id = artifact_match.group(1).strip()
                    version = version_match.group(1).strip() if version_match else "unknown"
                    
                    dependencies.append((group_id, artifact_id, version))
            
            return dependencies
