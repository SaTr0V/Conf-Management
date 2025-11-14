from typing import List, Tuple, Dict, Set, Optional
from collections import deque
import sys
import os
from maven_repository import MavenRepository
from test_repository import TestRepository


def make_node_id(group: str, artifact: str, version: Optional[str]) -> str:
    v = version if version else "unknown"
    return f"{group}:{artifact}:{v}"


def split_package_name(pkg: str) -> Tuple[str, str]:
    """Разделить 'group:artifact' на две части
       Если формат простой ('A'), используем group=artifact=pkg"""
    if ':' not in pkg:
        return pkg, pkg
    group, artifact = pkg.split(':', 1)
    return group, artifact


class DependencyGraph:
    """Класс для построения и анализа графа зависимостей (версия в ключе)."""

    def __init__(self, repo_url: str, test_mode: bool = False):
        self.repo_url = repo_url
        self.test_mode = test_mode

        # graph: node_id -> list of node_id (dependency ids)
        self.graph: Dict[str, List[str]] = {}
        # meta: node_id -> (group, artifact, version)
        self.meta: Dict[str, Tuple[str, str, str]] = {}

        # visited set for BFS (node_id strings)
        self.visited: Set[str] = set()

        # cycles: list of lists of node_id in cycle order
        self.cycles: List[List[str]] = []
        self._cycles_set: Set[Tuple[str, ...]] = set()  # for uniqueness

        # repo client
        if test_mode:
            self.repo_client = TestRepository(repo_url)
        else:
            self.repo_client = MavenRepository(repo_url)

    def build_graph(self, root_package: str, version: Optional[str] = None, max_depth: Optional[int] = None) -> None:
        """
        Построение графа зависимостей с помощью BFS (итеративно).
        root_package: "group:artifact"
        version: версия root (или None)
        max_depth: ограничение глубины (1 — только прямые зависимости)
        """
        # Validate package format
        try:
            root_group, root_artifact = split_package_name(root_package)
        except ValueError:
            raise

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

            # Respect max depth
            if max_depth is not None and current_depth >= max_depth:
                # ensure node present in graph (leaf)
                self.graph.setdefault(current_id, [])
                continue

            # get group/artifact/version for current
            group, artifact, ver = self.meta.get(current_id, (None, None, None))
            if group is None:
                # parse from id
                parts = current_id.split(':')
                if len(parts) >= 2:
                    group, artifact = parts[0], parts[1]
                    ver = parts[2] if len(parts) > 2 else "unknown"
                    self.meta[current_id] = (group, artifact, ver)
                else:
                    # malformed id
                    group, artifact, ver = current_id, "", "unknown"
                    self.meta[current_id] = (group, artifact, ver)

            # Fetch dependencies using repo client (API expects group:artifact and version or None)
            pkg_for_client = f"{group}:{artifact}"
            try:
                deps = self.repo_client.get_dependencies(pkg_for_client, None if ver == "unknown" else ver)
            except Exception as e:
                # Can't fetch dependencies -> treat as leaf but keep meta
                print(f"Предупреждение: не удалось получить зависимости для {current_id}: {e}")
                self.graph.setdefault(current_id, [])
                continue

            # Ensure graph entry exists
            self.graph.setdefault(current_id, [])

            # Process dependencies
            for dep_group, dep_artifact, dep_version in deps:
                dep_id = make_node_id(dep_group, dep_artifact, dep_version)
                # save meta
                if dep_id not in self.meta:
                    self.meta[dep_id] = (dep_group, dep_artifact, dep_version if dep_version else "unknown")

                # add edge
                self.graph[current_id].append(dep_id)

                if dep_id in self.visited:
                    # Detected an edge to an already visited node -> possible cycle
                    # Try to reconstruct cycle path from current_id back to dep_id using parent map
                    cycle = self._reconstruct_cycle(parent, current_id, dep_id)
                    if cycle:
                        canon = tuple(cycle)
                        if canon not in self._cycles_set:
                            self._cycles_set.add(canon)
                            self.cycles.append(cycle)
                    # do not enqueue again
                    continue

                # Not visited -> enqueue
                self.visited.add(dep_id)
                parent[dep_id] = current_id
                depth_map[dep_id] = current_depth + 1
                queue.append(dep_id)

    def _reconstruct_cycle(self, parent: Dict[str, Optional[str]], from_node: str, to_node: str) -> Optional[List[str]]:
        """
        Попытаться восстановить цикл: найти путь от to_node до from_node через parent.
        Возвращает список node_id в цикле в корректном порядке: to_node -> ... -> from_node -> to_node
        Если путь не найден, возвращает None.
        """
        path = []
        cur = from_node
        while cur is not None:
            path.append(cur)
            if cur == to_node:
                # нашли путь from_node -> ... -> to_node (в обратном порядке)
                path.reverse()  # теперь from to_node ... from_node
                # we want cycle starting at to_node:
                # create sequence to_node -> ... -> from_node -> to_node
                cycle = path + [to_node]
                return cycle
            cur = parent.get(cur)
        return None

    def print_graph(self, root_package: str, root_version: Optional[str] = None) -> None:
        """Выводит граф зависимостей в читаемой форме (BFS по уровням)."""
        try:
            root_group, root_artifact = split_package_name(root_package)
        except ValueError:
            print("Некорректное имя корневого пакета для печати")
            return

        root_id = make_node_id(root_group, root_artifact, root_version)
        print(f"\nПолный граф зависимостей для {root_id}:")
        print("-" * 60)

        if not self.graph:
            print("Граф пуст")
            return

        # BFS для печати
        queue = deque([(root_id, 0)])
        printed: Set[str] = set([root_id])

        while queue:
            current_id, level = queue.popleft()
            indent = "  " * level
            # human-friendly name
            g, a, v = self.meta.get(current_id, (None, None, None))
            display = f"{g}:{a}:{v}" if g is not None else current_id
            print(f"{indent}└── {display}")

            # print children
            for child_id in self.graph.get(current_id, []):
                if child_id not in printed:
                    printed.add(child_id)
                    queue.append((child_id, level + 1))

        # cycles
        if self.cycles:
            print(f"\nОбнаружены циклические зависимости ({len(self.cycles)}):")
            for i, cycle in enumerate(self.cycles, 1):
                print(f"  Цикл {i}: {' -> '.join(cycle)}")

        # total unique nodes in graph
        nodes_set: Set[str] = set(self.graph.keys())
        for deps in self.graph.values():
            nodes_set.update(deps)

        print(f"\nВсего уникальных узлов в графе: {len(nodes_set)}")
