# Dependency Graph Visualizer

*Инструмент для визуализации графа зависимостей пакетов Maven, а также тестовых пакетов.*

## Текущий статус: Этап 2 - Сбор данных

## Функциональность
- конфигурация через параметры командной строки;
- валидация входных параметров;
- вывод настроек в формате ключ-значение;
- получение прямых зависимостей из Maven репозитория;
- поддержка формата Maven метаданных.

## Использование
```bash
python src/cli.py --package <имя_пакета> --repo <url_репозитория> [опции]
```

**Допускается использование сокращений для параметров, они указаны в таблице «Доступные параметры»**

Продемонстрируем работу приложения на примере Maven-репозитория (https://repo.maven.apache.org/maven2).

Структура этого репозитория:
https://repo.maven.apache.org/maven2/GROUP_ID/ARTIFACT_ID/VERSION/

Рассмотрим на примере для **commons-lang3 версии 3.0**:
- GROUP_ID: `org.apache.commons`.
- ARTIFACT_ID: `commons-lang3`.
- VERSION: `3.0`.

Таким образом, запуск будет осуществлен со следующими параметрами:
```bash
python src/cli.py --package org.apache.commons:commons-lang3 --repo https://repo.maven.apache.org/maven2/ --version 3.0
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
python src/cli.py -p TEST_PACKAGE -r tests/test_repo.txt -t
```
**Примечание: все тестовые репозитории находятся в директории tests; для корректной работы программы при использовании тестовых репозиториев необходим тестовый режим (`--test-mode / -t`).**

### С дополнительными параметрами
```bash
python src/cli.py -p com.example:lib -r /path/to/repo -v 1.0.0 -o graph.svg -d 3
```

## Тестирование

**Тест 1: получение зависимостей реального пакета**
```bash
python src/cli.py -p app.futured.donut:donut -r https://repo.maven.apache.org/maven2/ -v 2.1.0
```

**Вывод**
```bash
Текущая конфигурация:
------------------------------
package_name: app.futured.donut:donut
repo_url: https://repo.maven.apache.org/maven2/
test_mode: False
version: 2.1.0
output_file: dependency_graph.svg
max_depth: unlimited
------------------------------

Получение зависимостей для пакета app.futured.donut:donut...

Прямые зависимости пакета app.futured.donut:donut:
--------------------------------------------------
 1. org.jetbrains.kotlin:kotlin-stdlib-jdk7  1.3.72
 2. androidx.core:core-ktx                   1.1.0
--------------------------------------------------
Всего зависимостей: 2

Зависимости успешно получены.
```
\
**Тест 2: обработка ошибок (нет переданного пакета)**
```bash
python src/cli.py --package "" --repo https://repo.maven.apache.org/maven2/
```

**Вывод**
```bash
Ошибка валидации конфигурации: Имя пакета обязательно для указания
```

\
**Тест 3: обработка ошибок (несуществующий пакет)**
```bash
python src/cli.py -p non.existent:package -r https://repo.maven.apache.org/maven2/ -v 1.0
```

**Вывод**
```bash
Текущая конфигурация:
------------------------------
package_name: non.existent:package
repo_url: https://repo.maven.apache.org/maven2/
test_mode: False
version: 1.0
output_file: dependency_graph.svg
max_depth: unlimited
------------------------------

Получение зависимостей для пакета non.existent:package...
Критическая ошибка: POM-файл для non.existent:package:1.0 не найден
```

**Тест 4: тестовый репозиторий**
```bash
python src/cli.py -p A -r tests/test_repo.txt -t
```

\
**Вывод**
```bash
Текущая конфигурация:
------------------------------
package_name: A
repo_url: tests/test_repo.txt
test_mode: True
version: latest
output_file: dependency_graph.svg
max_depth: unlimited
------------------------------

Получение зависимостей для пакета A...

Прямые зависимости пакета A:
--------------------------------------------------
 1. B:B                                      1.0.0
 2. C:C                                      1.0.0
--------------------------------------------------
Всего зависимостей: 2

Зависимости успешно получены.
```