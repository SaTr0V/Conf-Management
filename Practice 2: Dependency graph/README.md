# Dependency Graph Visualizer

*Инструмент для визуализации графа зависимостей пакетов Maven, а также тестовых пакетов.*

## Текущий статус: Этап 4 - Дополнительные операции

## Функциональность
- конфигурация через параметры командной строки;
- валидация входных параметров;
- вывод настроек в формате ключ-значение;
- получение прямых зависимостей из Maven-репозитория;
- вывод обратных зависимостей пакета;
- построение полного графа зависимостей с помощью BFS;
- обработка циклических зависимостей;
- поддержка тестовых репозиториев в txt-файлах;
- поддержка максимальной глубины анализа.

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
| `--package / -p` `имя_пакета`    | `Имя анализируемого пакета (обязательный)`  |
| `--repo / -r` `ссылка_на_репозиторий`    | `URL репозитория или путь к файлу тестового репозитория (обязательный)`   |
| `--test-mode / -t`   | `Режим работы с тестовым репозиторием`   |
| `--version / -v` `номер_версии` | `Версия пакета` |
| `--output / -o` `название_файла` | `Имя сгенерированного файла с изображением графа ()` |
| `--max-depth / -d` `количество_уровней` | `Максимальная глубина анализа зависимостей` |
| `--reverse / -R` `имя_пакета` | `Вывод графа обратных зависимостей` |

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
python src/cli.py -p app.futured.donut:donut -r https://repo.maven.apache.org/maven2 -v 2.1.0 -R org.jetbrains.kotlin:kotlin-stdlib
```

**Вывод**
```bash
Текущая конфигурация:
------------------------------
package_name: app.futured.donut:donut
repo_url: https://repo.maven.apache.org/maven2
test_mode: False
version: 2.1.0
output_file: dependency_graph.svg
max_depth: unlimited
reverse_package: org.jetbrains.kotlin:kotlin-stdlib
------------------------------

Получение зависимостей для пакета app.futured.donut:donut...

Прямые зависимости пакета app.futured.donut:donut:
--------------------------------------------------
 1. org.jetbrains.kotlin:kotlin-stdlib-jdk7  1.3.72
 2. androidx.core:core-ktx                   1.1.0
--------------------------------------------------
Всего зависимостей: 2

Зависимости успешно получены.

Построение полного графа зависимостей...
Максимальная глубина: неограничена
Предупреждение: не удалось получить зависимости для androidx.core:core-ktx:1.1.0: POM-файл для androidx.core:core-ktx:1.1.0 не найден

Полный граф зависимостей для app.futured.donut:donut:2.1.0:
------------------------------------------------------------
app.futured.donut:donut:2.1.0
   org.jetbrains.kotlin:kotlin-stdlib-jdk7:1.3.72
      org.jetbrains.kotlin:kotlin-stdlib:1.3.72
         org.jetbrains.kotlin:kotlin-stdlib-common:1.3.72
            org.jetbrains.kotlin:kotlin-test-common:1.3.72
               ↳ org.jetbrains.kotlin:kotlin-stdlib-common:1.3.72  (повтор)
               org.jetbrains.kotlin:kotlin-test-annotations-common:1.3.72
                  ↳ org.jetbrains.kotlin:kotlin-stdlib-common:1.3.72  (повтор)
                  ↳ org.jetbrains.kotlin:kotlin-test-common:1.3.72  (повтор)
            ↳ org.jetbrains.kotlin:kotlin-test-annotations-common:1.3.72  (повтор)
         org.jetbrains:annotations:13.0
         org.jetbrains.kotlin:kotlin-test-junit:1.3.72
            ↳ org.jetbrains.kotlin:kotlin-test-annotations-common:1.3.72  (повтор)
            org.jetbrains.kotlin:kotlin-test:1.3.72
               ↳ org.jetbrains.kotlin:kotlin-test-common:1.3.72  (повтор)
               ↳ org.jetbrains.kotlin:kotlin-stdlib:1.3.72  (повтор)
               ↳ org.jetbrains.kotlin:kotlin-test-junit:1.3.72  (повтор)
               junit:junit:4.12
                  org.hamcrest:hamcrest-core:1.3
            ↳ junit:junit:4.12  (повтор)
      ↳ org.jetbrains.kotlin:kotlin-test-junit:1.3.72  (повтор)
   androidx.core:core-ktx:1.1.0
------------------------------------------------------------
Всего узлов: 12

Обратные зависимости (кто зависит от org.jetbrains.kotlin:kotlin-stdlib:2.1.0):
------------------------------------------------------------
 1. app.futured.donut:donut:2.1.0
 2. org.jetbrains.kotlin:kotlin-stdlib-jdk7:1.3.72
 3. org.jetbrains.kotlin:kotlin-test-junit:1.3.72
 4. org.jetbrains.kotlin:kotlin-test:1.3.72
------------------------------------------------------------
Всего обратных зависимостей: 4

Граф зависимостей успешно построен.
```
**Примечание: наличие предупреждений не указывает на ошибку в работе программы. Не все зависимости находятся в Maven-репозитории.**

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
reverse_package: None
------------------------------

Получение зависимостей для пакета non.existent:package...
Критическая ошибка: POM-файл для non.existent:package:1.0 не найден
```

**Тест 4: тестовый репозиторий**
```bash
python src/cli.py -p A -r tests/test_repo.txt -t --reverse B
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
reverse_package: B
------------------------------

Получение зависимостей для пакета A...

Прямые зависимости пакета A:
--------------------------------------------------
 1. B:B                                      1.0.0
 2. C:C                                      1.0.0
--------------------------------------------------
Всего зависимостей: 2

Зависимости успешно получены.

Построение полного графа зависимостей...
Максимальная глубина: неограничена

Полный граф зависимостей для A:latest:
------------------------------------------------------------
A:A:unknown
   B:B:1.0.0
      D:D:1.0.0
         H:H:1.0.0
            A:A:1.0.0
               ↳ B:B:1.0.0  (повтор)
               C:C:1.0.0
                  F:F:1.0.0
                     ↳ B:B:1.0.0  (повтор)
                     G:G:1.0.0
                  ↳ G:G:1.0.0  (повтор)
      E:E:1.0.0
   ↳ C:C:1.0.0  (повтор)
------------------------------------------------------------
Всего узлов: 9

Обратные зависимости (кто зависит от B):
------------------------------------------------------------
 1. A:A:1.0.0
 2. A:A:unknown
 3. C:C:1.0.0
 4. D:D:1.0.0
 5. F:F:1.0.0
 6. H:H:1.0.0
------------------------------------------------------------
Всего обратных зависимостей: 6

Граф зависимостей успешно построен.
```