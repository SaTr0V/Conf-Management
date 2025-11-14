from typing import List, Tuple, Dict, Set, Optional
from collections import deque
import sys
import os
from maven_repository import MavenRepository
from test_repository import TestRepository
import graphviz


def make_node_id(group: str, artifact: str, version: Optional[str]) -> str:
    v = version if version else "unknown"
    return f"{group}:{artifact}:{v}"


def split_package_name(pkg: str) -> Tuple[str, str]:
    """Разделить 'group:artifact' на две части.
       Если формат простой ('A'), используем group=artifact=pkg"""
    if ':' not in pkg:
        return pkg, pkg
    group, artifact = pkg.split(':', 1)
    return group, artifact


class DependencyGraph:
    """Класс для построения и анализа графа зависимостей."""

    def __init__(self, repo_url: str, test_mode: bool = False):
        self.repo_url = repo_url
        self.test_mode = test_mode

        # graph: node_id -> list of node_id (dependency ids)
        self.graph: Dict[str, List[str]] = {}
        # meta: node_id -> (group, artifact, version)
        self.meta: Dict[str, Tuple[str, str, str]] = {}

        # Множество посещенных узлов для BFS
        self.visited: Set[str] = set()

        # Обработка циклических зависимостей
        self.cycles: List[List[str]] = []
        self._cycles_set: Set[Tuple[str, ...]] = set()

        # С каким репозиторием работаем
        if test_mode:
            self.repo_client = TestRepository(repo_url)
        else:
            self.repo_client = MavenRepository(repo_url)

        # Кэш обратного графа
        self._reverse_graph: Optional[Dict[str, List[str]]] = None

    def build_graph(self, root_package: str, version: Optional[str] = None, max_depth: Optional[int] = None) -> None:
        """Построение графа зависимостей с помощью BFS (итеративно)"""
        
        root_group, root_artifact = split_package_name(root_package)

        root_id = make_node_id(root_group, root_artifact, version)
        self.meta[root_id] = (root_group, root_artifact, version if version else "unknown")

        queue = deque()
        depth_map: Dict[str, int] = {}
        parent: Dict[str, Optional[str]] = {}  # для восстановления пути при цикле

        queue.append(root_id)
        depth_map[root_id] = 0
        parent[root_id] = None
        self.visited.add(root_id)

        while queue:
            current_id = queue.popleft()
            current_depth = depth_map[current_id]

            if max_depth is not None and current_depth >= max_depth:
                # Убедимся, что узел появился в графе
                self.graph.setdefault(current_id, [])
                continue

            # Получение group/artifact/version
            group, artifact, ver = self.meta.get(current_id, (None, None, None))
            if group is None:
                parts = current_id.split(':')
                if len(parts) >= 2:
                    group, artifact = parts[0], parts[1]
                    ver = parts[2] if len(parts) > 2 else "unknown"
                    self.meta[current_id] = (group, artifact, ver)
                else:
                    group, artifact, ver = current_id, "", "unknown"
                    self.meta[current_id] = (group, artifact, ver)

            # Получение зависимостей
            pkg_for_client = f"{group}:{artifact}"
            try:
                deps = self.repo_client.get_dependencies(pkg_for_client, None if ver == "unknown" else ver)
            except Exception as e:
                # Не удалось вытащить зависимости - считаем листом графа
                print(f"Предупреждение: не удалось получить зависимости для {current_id}: {e}")
                self.graph.setdefault(current_id, [])
                continue

            self.graph.setdefault(current_id, [])

            # Обрабатываем зависимости
            for dep_group, dep_artifact, dep_version in deps:
                dep_id = make_node_id(dep_group, dep_artifact, dep_version)
                if dep_id not in self.meta:
                    self.meta[dep_id] = (dep_group, dep_artifact, dep_version if dep_version else "unknown")

                # Добавляем ребро
                self.graph[current_id].append(dep_id)

                if dep_id in self.visited:
                    # Обработка циклических зависимостей
                    cycle = self._reconstruct_cycle(parent, current_id, dep_id)
                    if cycle:
                        canon = tuple(cycle)
                        if canon not in self._cycles_set:
                            self._cycles_set.add(canon)
                            self.cycles.append(cycle)
                    continue

                self.visited.add(dep_id)
                parent[dep_id] = current_id
                depth_map[dep_id] = current_depth + 1
                queue.append(dep_id)

        # Убираем кэш обратного графа
        self._reverse_graph = None

    def _reconstruct_cycle(self, parent: Dict[str, Optional[str]], from_node: str, to_node: str) -> Optional[List[str]]:
        """Попытаться восстановить цикл: найти путь от to_node до from_node через parent"""
        
        path = []
        cur = from_node
        while cur is not None:
            path.append(cur)
            if cur == to_node:
                path.reverse()
                cycle = path + [to_node]
                return cycle
            cur = parent.get(cur)
        return None
    
    def print_graph(self, root_package: str, version: Optional[str] = None) -> None:
        """Печатает полный граф зависимостей в виде дерева."""

        print(f"\nПолный граф зависимостей для {root_package}:{version if version else 'latest'}:")
        print("-" * 60)

        # Преобразуем group:artifact в node_id
        root_group, root_artifact = split_package_name(root_package)
        root_id = make_node_id(root_group, root_artifact, version)

        if root_id not in self.graph:
            # Попытка найти версию автоматически
            candidates = [n for n in self.graph.keys() if n.startswith(f"{root_group}:{root_artifact}:")]
            if not candidates:
                print("Граф пуст — возможно, не удалось получить зависимости.")
                return
            root_id = candidates[0]

        visited = set()

        def dfs(node: str, indent: str = ""):
            if node in visited:
                print(indent + f"↳ {node}  (повтор)")
                return
            visited.add(node)

            print(indent + f"{node}")

            for child in self.graph.get(node, []):
                dfs(child, indent + "   ")

        dfs(root_id)

        print("-" * 60)
        print(f"Всего узлов: {len(self.graph)}")

    def build_reverse_graph(self) -> Dict[str, List[str]]:
        """Построение обратного графа"""
        if self._reverse_graph is not None:
            return self._reverse_graph

        rev: Dict[str, List[str]] = {}
        for node in list(self.graph.keys()):
            rev.setdefault(node, [])
        for parent_node, children in self.graph.items():
            for child in children:
                rev.setdefault(child, []).append(parent_node)
        self._reverse_graph = rev
        return rev

    def get_reverse_dependencies(self, target_package: str, target_version: Optional[str] = None,
                                 max_depth: Optional[int] = None) -> List[str]:
        """Возвращает список node_id, которые зависят от target"""
        
        tg_group, tg_artifact = split_package_name(target_package)
        target_id = make_node_id(tg_group, tg_artifact, target_version)

        rev = self.build_reverse_graph()
        if target_id not in rev:
            # Целевой узел отсутствует в графе -> возможно его нет или использовалась иная версия
            # попробуем найти по префиксу group:artifact:*
            matches = [n for n in rev.keys() if n.startswith(f"{tg_group}:{tg_artifact}:")]
            if not matches:
                raise ValueError(f"Пакет {target_id} не найден в графе (нет узлов-зависимостей).")
            # Если есть несколько версий, выбираем те ключи
            # Для обратных зависимостей будем объединять результаты для всех совпадающих версий
            results_set: Set[str] = set()
            for m in matches:
                results_set.update(self._bfs_reverse_collect(m, rev, max_depth))
            return sorted(results_set)
        else:
            return self._bfs_reverse_collect(target_id, rev, max_depth)

    def _bfs_reverse_collect(self, start_id: str, rev_graph: Dict[str, List[str]], max_depth: Optional[int]) -> List[str]:
        """Внутренний BFS по обратному графу — вернуть все узлы, которые достижимы от start_id (вверх)"""
        
        q = deque([(start_id, 0)])
        visited: Set[str] = set([start_id])
        results: Set[str] = set()

        while q:
            node, depth = q.popleft()
            if max_depth is not None and depth >= max_depth:
                continue
            for parent in rev_graph.get(node, []):
                if parent not in visited:
                    visited.add(parent)
                    results.add(parent)
                    q.append((parent, depth + 1))
        return sorted(results)

    def print_reverse_dependencies(self, target_package: str, target_version: Optional[str] = None,
                                   max_depth: Optional[int] = None) -> None:
        """Печать обратных зависимостей"""
        try:
            rev_nodes = self.get_reverse_dependencies(target_package, target_version, max_depth)
        except ValueError as e:
            print(f"Критическая ошибка: {e}")
            return

        print(f"\nОбратные зависимости (кто зависит от {target_package}{':' + target_version if target_version else ''}):")
        print("-" * 60)
        if not rev_nodes:
            print("Обратные зависимости не найдены.")
            return

        for i, node_id in enumerate(rev_nodes, 1):
            g, a, v = self.meta.get(node_id, (None, None, None))
            display = f"{g}:{a}:{v}" if g is not None else node_id
            print(f"{i:2d}. {display}")
        print("-" * 60)
        print(f"Всего обратных зависимостей: {len(rev_nodes)}")

    def to_dot(self) -> str:
        """Сформировать текст Graphviz (DOT) для всего графа"""
        
        lines = ["digraph G {"]
        for parent, children in self.graph.items():
            parent_label = f'"{parent}"'
            for child in children:
                child_label = f'"{child}"'
                lines.append(f"    {parent_label} -> {child_label};")
        lines.append("}")
        return "\n".join(lines)

    def render_graph(self, output_file: str = "dependency_graph.svg") -> None:
        """Сохранить граф в SVG через Graphviz"""
        
        dot_str = self.to_dot()
        g = graphviz.Source(dot_str)
        g.format = 'svg'
        g.render(filename=output_file, cleanup=True)
        print(f"\nГраф зависимостей сохранён в {output_file}")