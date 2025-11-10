# Dependency Graph Visualizer

*Инструмент для визуализации графа зависимостей пакетов Maven.*

## Текущий статус: Этап 1 - Минимальный прототип

## Функциональность
- Конфигурация через параметры командной строки
- Валидация входных параметров
- Вывод настроек в формате ключ-значение

## Использование
```bash
python src/cli.py --package <имя_пакета> --repo <url_репозитория> [опции]
```

## Доступные параметры
 Параметр | Описание |
|:----------:|:----------:|
| `--package / -p`    | `Имя анализируемого пакета (обязательный)`  |
| `--repo / -r`    | `URL репозитория или путь к файлу тестового репозитория (обязательный)`   |
| `--test-mode / -t`   | `Режим работы с тестовым репозиторием`   |
| `--version / -v` | `Версия пакета` |
| `--output / -o` | `Имя сгенерированного файла с изображением графа ()` |
| `--max-depth / -d` | `Максимальная глубина анализа зависимостей` |

## Примеры запуска

### Базовый запуск
```bash
python src/cli.py -p com.example:my-package -r https://repo.maven.apache.org/maven2/
```

### С тестовым режимом
```bash
python src/cli.py -p TEST_PACKAGE -r test_repo.txt -t
```

### С дополнительными параметрами
```bash
python src/cli.py -p com.example:lib -r /path/to/repo -v 1.0.0 -o graph.svg -d 3
```

## Тестирование

**Тест 1: запуск с корректными параметрами**
```bash
python src/cli.py --package com.example:my-app --repo https://repo.maven.apache.org/maven2/ --version 1.0.0 --output graph.svg --max-depth 3
```

**Вывод**
```bash
Текущая конфигурация:
------------------------------
package_name: com.example:my-app
repo_url: https://repo.maven.apache.org/maven2/
test_mode: False
version: 1.0.0
output_file: graph.svg
max_depth: 3
------------------------------
Конфигурация успешно загружена. Приложение готово к работе.
```
\
**Тест 2: обработка ошибок**
```bash
python src/cli.py --package "" --repo https://repo.maven.apache.org/maven2/
```

**Вывод**
```bash
Ошибка валидации конфигурации: Имя пакета обязательно для указания
```