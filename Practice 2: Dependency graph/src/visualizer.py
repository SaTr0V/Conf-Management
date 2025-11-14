import subprocess
from typing import Dict, List


class GraphvizExporter:
    """Генератор DOT-файлов для Graphviz"""
    
    def __init__(self, dependencies: Dict[str, List[str]]):
        self.dependencies = dependencies

    def build_dot(self) -> str:
        """Формирует текст файла Graphviz"""
        
        lines = ["digraph dependencies {"]

        for pkg, deps in self.dependencies.items():
            for dep in deps:
                lines.append(f'    "{pkg}" -> "{dep}";')

        lines.append("}")
        return "\n".join(lines)

    def save_dot(self, filename: str):
        dot_text = self.build_dot()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(dot_text)

    def save_svg(self, dot_file: str, svg_file: str):
        """Конвертация DOT в SVG через Graphviz. Требует установленного dot в системе"""
        
        subprocess.run(["dot", "-Tsvg", dot_file, "-o", svg_file], check=True)
